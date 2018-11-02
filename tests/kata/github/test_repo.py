from pprint import pprint

import pytest

from src.kata.github.api import Api
from src.kata.github.repo import Repo

NOT_USED = 'Not Used'


@pytest.fixture
def mock_api():
    class MockApi:
        mocked_responses = {
            'contents': {
                'only_files': {
                    '': [{
                        'name': 'a_file.txt',
                        'path': 'a_file.txt',
                        'type': 'file',
                        'download_url': 'https://github_url_for/a_file.txt'
                    }, {
                        'name': 'another_file.py',
                        'path': 'another_file.py',
                        'type': 'file',
                        'download_url': 'https://github_url_for/another_file.py'
                    }, {
                        'name': 'a_third_file.md',
                        'path': 'a_third_file.md',
                        'type': 'file',
                        'download_url': 'https://github_url_for/a_third_file.md'
                    }]
                },
                'dir_containing_files': [

                ],
                'empty_dir': [

                ],
                'nested_dirs': [

                ],
                'mixed_files_and_dir': [

                ]

            }
        }

        def contents(self, _user, repo, path):
            scenario = repo
            if scenario not in self.mocked_responses['contents']:
                raise ValueError(f"Scenario: '{scenario}' doesn't correspond to a valid scenario")
            if path not in self.mocked_responses['contents'][scenario]:
                raise ValueError(f"Path: '{path}' doesn't correspond to a valid path for the scenario: '{scenario}'")

            return self.mocked_responses['contents'][scenario][path]

    return MockApi()


@pytest.fixture
def repo(mock_api):
    return Repo(mock_api)


@pytest.mark.skip
def test_sandbox():
    api = Api()
    res = api.contents('FlorianKempenich', 'ansible-role-python-virtualenv', '')
    pprint(res)


def test_only_files(repo):
    assert repo.file_urls(NOT_USED, repo='only_files', path='') == [
        {
            'file_path': 'a_file.txt',
            'download_url': 'https://github_url_for/a_file.txt'
        },
        {
            'file_path': 'another_file.py',
            'download_url': 'https://github_url_for/another_file.py'
        },
        {
            'file_path': 'a_third_file.md',
            'download_url': 'https://github_url_for/a_third_file.md'
        }
    ]


@pytest.mark.skip
def test_directory_containing_files(repo):
    pass
