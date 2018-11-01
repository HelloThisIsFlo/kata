import functools
from pprint import pprint

import pytest

from src.kata.github.api import MockApi, Api
from src.kata.github.repo import Repo


@pytest.fixture
def mock_api():
    return MockApi()


@pytest.fixture
def repo(mock_api):
    return Repo(mock_api)


@pytest.fixture
def file_urls_for_given_path(repo):
    @functools.wraps(repo.file_urls)
    def wrapper(path):
        return repo.file_urls(user='NotUsed', repo='NotUsed', path=path)

    return wrapper


@pytest.mark.skip
def test_sandbox():
    api = Api()
    res = api.contents('FlorianKempenich', 'ansible-role-python-virtualenv', '')
    pprint(res)


def test_only_files(file_urls_for_given_path):
    assert file_urls_for_given_path('only_files') == [
        {
            'file_path': '.travis.yml',
            'download_url': 'https://github_url_for/.travis.yml'
        },
        {
            'file_path': 'LICENSE.md',
            'download_url': 'https://github_url_for/LICENSE.md'
        },
        {
            'file_path': 'README.md',
            'download_url': 'https://github_url_for/README.md'
        }
    ]
