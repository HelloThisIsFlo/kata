import pytest

from src.kata.github.repo import Repo


@pytest.fixture
def repo():
    return Repo()


def test_something(repo):
    assert repo.some_method() == 42
