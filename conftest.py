from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.fixture
def thread_pool_executor():
    return ThreadPoolExecutor(100)
