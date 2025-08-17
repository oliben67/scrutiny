import sys

import pytest

from scrutiny.distribute import distribute


def pytest_pycollect_makeitem(collector, name, obj):
    if hasattr(obj, "pytestmark") and isinstance(obj.pytestmark, list):
        if distributed := [
            mark for mark in obj.pytestmark if mark.name == "distribute"
        ]:
            count = distributed[0].kwargs.get("count", 1)
            distributed_cls = distribute(obj, count=count)
            distributed_name = "".join(part.capitalize() for part in name.split("_"))

            setattr(sys.modules[obj.__module__], distributed_name, distributed_cls)

            return pytest.Class.from_parent(
                collector,
                name=distributed_name,
                obj=distributed_cls,
            )
