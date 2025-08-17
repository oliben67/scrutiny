import pytest


def generate_test_data():
    return [(i, j, k) for i in [1] for j in [2, 3] for k in [4, 5, 6]]


@pytest.mark.parametrize("x, y, z", generate_test_data())
@pytest.mark.asyncio
@pytest.mark.distribute(count=3)
def test_one(x, y, z):
    assert x + 1 < 300


@pytest.mark.asyncio
class TestVanilla:
    def test_da_stuff(self):
        assert True

    def test_da_stuff_again(self):
        assert True


def testing_whatever():
    assert True
