from pprint import pprint

import pytest

from src.kata.github.api import Api
from src.kata.github.repo import Repo

NOT_USED = 'Not Used'


# def test_yo():
#
#     assert extract_name_from_path('hello') == 'hello'
#     assert extract_name_from_path('hey/hello') == 'hello'
#     assert extract_name_from_path('test/hey/hello') == 'hello'


@pytest.fixture
def mock_api():
    def extract_name_from_path(path):
        return path.split('/')[-1]

    def mock_file_entry(file_path):
        return {
            'name': extract_name_from_path(file_path),
            'path': file_path,
            'type': 'file',
            'download_url': f'https://github_url_for/{file_path}'
        }

    def mock_dir_entry(dir_path):
        return {
            'name': extract_name_from_path(dir_path),
            'path': dir_path,
            'type': 'dir',
            'download_url': None
        }

    class MockApi:
        mocked_contents_scenarios = {
            'only_files': {
                '': [mock_file_entry('a_file.txt'),
                     mock_file_entry('another_file.py'),
                     mock_file_entry('a_third_file.md')]
            },
            'directory_containing_files': {
                '': [mock_dir_entry('some_dir')],
                'some_dir': [mock_file_entry('some_dir/a_file.txt'),
                             mock_file_entry('some_dir/another_file.py'),
                             mock_file_entry('some_dir/a_third_file.md')]
            },
            'multiple_directories_containing_files': {
                '': [mock_dir_entry('some_dir'),
                     mock_dir_entry('another_dir')],
                'some_dir': [mock_file_entry('some_dir/a_file.txt'),
                             mock_file_entry('some_dir/another_file.py'),
                             mock_file_entry('some_dir/a_third_file.md')],
                'another_dir': [mock_file_entry('another_dir/a_file.txt'),
                                mock_file_entry('another_dir/another_file.py'),
                                mock_file_entry('another_dir/some_other_file.md')]
            }
        }

        def contents(self, _user, repo, path):
            scenario = repo
            if scenario not in self.mocked_contents_scenarios:
                raise ValueError(f"Scenario: '{scenario}' doesn't correspond to a valid scenario")
            if path not in self.mocked_contents_scenarios[scenario]:
                raise ValueError(f"Path: '{path}' doesn't correspond to a valid path for the scenario: '{scenario}'")

            return self.mocked_contents_scenarios[scenario][path]

    return MockApi()


@pytest.fixture
def repo(mock_api):
    return Repo(mock_api)


@pytest.mark.skip
def test_sandbox():
    api = Api()
    res = api.contents('FlorianKempenich', 'ansible-role-python-virtualenv', '')
    pprint(res)
    pytest.fail('debug')


class TestScenarios:

    @pytest.fixture
    def repo_with_scenario(self, repo):
        class RepoWithScenario:
            def __init__(self):
                self.scenario = None

            def init_scenario(self, scenario):
                self.scenario = scenario

            def file_urls(self, path):
                return repo.file_urls(user=NOT_USED, repo=self.scenario, path=path)

        return RepoWithScenario()

    def test_only_files(self, repo_with_scenario):
        # Given: A repo containing only files | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('only_files')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: List all the files
        assert repo_with_scenario.file_urls(path='') == [
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
            }]

    def test_directory_containing_files(self, repo_with_scenario):
        # Given: A repo containing a dir, itself containing files | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('directory_containing_files')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: List all the files recursively found
        assert result == [
            {
                'file_path': 'some_dir/a_file.txt',
                'download_url': 'https://github_url_for/some_dir/a_file.txt'
            },
            {
                'file_path': 'some_dir/another_file.py',
                'download_url': 'https://github_url_for/some_dir/another_file.py'
            },
            {
                'file_path': 'some_dir/a_third_file.md',
                'download_url': 'https://github_url_for/some_dir/a_third_file.md'
            }]

    @pytest.mark.skip
    def test_multiple_directories_containing_files(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, themselves containing files | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('multiple_directories_containing_files')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: List all the files recursively found
        assert result == [
            {
                'file_path': 'some_dir/a_file.txt',
                'download_url': 'https://github_url_for/some_dir/a_file.txt'
            },
            {
                'file_path': 'some_dir/another_file.py',
                'download_url': 'https://github_url_for/some_dir/another_file.py'
            },
            {
                'file_path': 'some_dir/a_third_file.md',
                'download_url': 'https://github_url_for/some_dir/a_third_file.md'
            },
            {
                'file_path': 'another_dir/a_file.txt',
                'download_url': 'https://github_url_for/another_dir/a_file.txt'
            },
            {
                'file_path': 'another_dir/another_file.py',
                'download_url': 'https://github_url_for/another_dir/another_file.py'
            },
            {
                'file_path': 'another_dir/some_other_file.md',
                'download_url': 'https://github_url_for/another_dir/some_other_file.md'
            }]

    # TODO: Tests to add:
    # - Multiple dir => Concatenate results
    # - Empty dir => Ignore
    # - Mixed files & dir => Flatten the file hierarchy
    # - Nested dir => Flatten the file hierarchy
    # - Path isn't root
