import pytest

from src.db import DBManager


@pytest.fixture
def db():
    with DBManager(":memory:") as manager:
        manager.initialize()
        yield manager
