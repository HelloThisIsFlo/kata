from concurrent import futures
from pprint import pprint

import pytest

from src.kata.github.api import Api
from src.kata.github.repo import Repo


@pytest.mark.skip
def test_run_sandbox():
    github_user = 'FlorianKempenich'
    # repo_name = 'ansible-role-python-virtualenv'
    repo_name = 'My-Java-Archetype'
    path = ''
    thread_pool_executor = futures.ThreadPoolExecutor(100, thread_name_prefix='subdir-explorer-')
    api = Api()
    repo = Repo(api, thread_pool_executor)

    result = repo.file_urls(github_user, repo_name, path)
    pprint(result)
