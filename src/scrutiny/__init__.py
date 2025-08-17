import inspect

import pytest

from scrutiny.distribute import distribute
from scrutiny.tracking import logger


@pytest.hookimpl(wrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    try:
        logger.debug("pytest_pycollect_makeitem: %s", name)
        return (yield)
    finally:
        pass


# def pytest_generate_tests(metafunc):
#     print("-->Generate: {}".format(metafunc.function.__name__))


__all__ = ["distribute", "pytest_pycollect_makeitem"]
