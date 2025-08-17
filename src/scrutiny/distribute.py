"""
This module provides utilities to distribute parametrized tests across multiple
chunks for parallel or distributed execution.
"""

import functools
import inspect
from copy import deepcopy

from pytest import Mark

from scrutiny.config import _configs
from scrutiny.tracking import logger


def chunk_it_up(iterable: list, chunk_size: int):
    """
    Splits the iterable into chunk_size chunks as evenly as possible.
    """
    iterable = list(iterable)
    n = len(iterable)
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    avg = n // chunk_size
    rem = n % chunk_size
    chunks = []
    start = 0
    for i in range(chunk_size):
        end = start + avg + (1 if i < rem else 0)
        chunks.append(iterable[start:end])
        start = end
    return chunks


class TestDistributeMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        if len(kwargs):
            func_base = kwargs.get("func", None)
            is_async = inspect.iscoroutinefunction(func_base)
            count = kwargs.get("count", 1)
            marks = kwargs.get("marks", [])
            parametrize = kwargs.get("parametrize", None)

            chunked_params = (
                chunk_it_up(parametrize.args[1], count) if parametrize else []
            )
            func = deepcopy(func_base)
            if callable(func_base):
                try:
                    for idx, params in enumerate(chunked_params, start=1):
                        chunk_parametrize = Mark(
                            name=_configs["parameters"]["name"],
                            args=params,
                            kwargs={},
                        )
                        if is_async:

                            @functools.wraps(func)
                            async def wrapper(self, *args, **kwargs):
                                return await func(*args, **kwargs)
                        else:

                            @functools.wraps(func)
                            def wrapper(self, *args, **kwargs):
                                return func(*args, **kwargs)

                        function_marks = [chunk_parametrize] + marks
                        setattr(wrapper, "pytestmark", function_marks)
                        logger.debug(getattr(wrapper, "pytestmark"))

                        func_name = f"{func.__name__}_{idx}"
                        attrs[func_name] = wrapper
                        logger.debug("%s %s %s", attrs, func_name, name)

                except Exception as e:
                    logger.error("Failure distributing parameters: %s", e)
        return super().__new__(cls, name, bases, attrs)


class TestDistribute(metaclass=TestDistributeMeta):
    pass


def distribute(*args, **kwargs):
    try:
        if len(args) == 1 and len(kwargs) == 0:
            if callable(args[0]):
                logger.warning(
                    "distribute: no count passed to decorator, returning decorated function as is"
                )
                return args[0]
            elif isinstance(args[0], int):
                return lambda func: distribute(func, count=args[0])
        elif len(args) == 0 and "count" in kwargs and isinstance(kwargs["count"], int):
            return lambda func: distribute(func, count=kwargs["count"])
        elif (
            len(args) == 1
            and callable(args[0])
            and len(kwargs) == 1
            and "count" in kwargs
            and isinstance(kwargs["count"], int)
        ):
            func = args[0]
            logger.info("distribute: function decorated: %s", func.__name__)

            @functools.wraps(func)
            def _distribute(**kwargs):
                count = kwargs.get("count", 1)

                if count == 1 or not hasattr(func, "pytestmark"):
                    return func
                logger.info("distribute: pytest marks: %s", func.pytestmark)

                marks = getattr(func, "pytestmark", [])
                if not (
                    parametrize_mark := next(
                        (
                            mark
                            for mark in marks
                            if mark.name == _configs["parameters"]["name"]
                        ),
                        None,
                    )
                ):
                    return func
                if not (
                    distribute_mark := next(
                        (mark for mark in marks if mark.name == "distribute"),
                        None,
                    )
                ):
                    return func

                marks.remove(parametrize_mark)
                marks.remove(distribute_mark)

                test_class_name = f"TestDistribute_{func.__name__}_{count}_Times"
                return type(
                    test_class_name,
                    (TestDistribute,),
                    {},
                    func=func,
                    marks=marks,
                    parametrize=parametrize_mark,
                    count=count,
                )

            return _distribute(**kwargs)
    except Exception as e:
        logger.error("Failure distributing function: %s", e)
        raise
