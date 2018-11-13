from pathlib import Path
from typing import List

import pytest

from src.kata.io.github.repo import Repo
from src.kata.io.models import DownloadableFile

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
            },
            'multiple_directories_one_is_empty': {
                '': [mock_dir_entry('some_dir'),
                     mock_dir_entry('empty_dir')],
                'some_dir': [mock_file_entry('some_dir/a_file.txt'),
                             mock_file_entry('some_dir/another_file.py'),
                             mock_file_entry('some_dir/a_third_file.md')],
                'empty_dir': []
            },
            'mix_of_files_and_directory': {
                '': [mock_file_entry('a_file.txt'),
                     mock_dir_entry('some_dir')],
                'some_dir': [mock_file_entry('some_dir/a_file.txt'),
                             mock_file_entry('some_dir/another_file.py')]

            },
            'nested_directories': {
                '':
                    [mock_file_entry('file_at_root.txt'),
                     mock_dir_entry('dir_at_root')],
                'dir_at_root':
                    [mock_file_entry('dir_at_root/file_at_level_1.txt'),
                     mock_dir_entry('dir_at_root/dir_at_level_1')],
                'dir_at_root/dir_at_level_1':
                    [mock_file_entry('dir_at_root/dir_at_level_1/file_at_level_2.txt'),
                     mock_dir_entry('dir_at_root/dir_at_level_1/dir_at_level_2')],
                'dir_at_root/dir_at_level_1/dir_at_level_2':
                    [mock_file_entry('dir_at_root/dir_at_level_1/dir_at_level_2/file_at_level_3.txt')]
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
def repo(mock_api, thread_pool_executor):
    return Repo(mock_api, thread_pool_executor)


def sort_by_file_path(files: List[DownloadableFile]):
    def file_path(file_entry: DownloadableFile):
        return file_entry.file_path

    return sorted(files, key=file_path)


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
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('a_file.txt'),
                download_url='https://github_url_for/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('another_file.py'),
                download_url='https://github_url_for/another_file.py'
            ),
            DownloadableFile(
                file_path=Path('a_third_file.md'),
                download_url='https://github_url_for/a_third_file.md'
            )])

    def test_directory_containing_files(self, repo_with_scenario):
        # Given: A repo containing a dir, itself containing files | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('directory_containing_files')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: List all the files recursively found
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('some_dir/a_file.txt'),
                download_url='https://github_url_for/some_dir/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('some_dir/another_file.py'),
                download_url='https://github_url_for/some_dir/another_file.py'
            ),
            DownloadableFile(
                file_path=Path('some_dir/a_third_file.md'),
                download_url='https://github_url_for/some_dir/a_third_file.md'
            )])

    def test_multiple_directories_containing_files(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, themselves containing files | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('multiple_directories_containing_files')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: List all the files recursively found
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('some_dir/a_file.txt'),
                download_url='https://github_url_for/some_dir/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('some_dir/another_file.py'),
                download_url='https://github_url_for/some_dir/another_file.py'
            ),
            DownloadableFile(
                file_path=Path('some_dir/a_third_file.md'),
                download_url='https://github_url_for/some_dir/a_third_file.md'
            ),
            DownloadableFile(
                file_path=Path('another_dir/a_file.txt'),
                download_url='https://github_url_for/another_dir/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('another_dir/another_file.py'),
                download_url='https://github_url_for/another_dir/another_file.py'
            ),
            DownloadableFile(
                file_path=Path('another_dir/some_other_file.md'),
                download_url='https://github_url_for/another_dir/some_other_file.md'
            )])

    def test_multiple_directories_one_is_empty(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('multiple_directories_one_is_empty')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: Empty dir is ignored
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('some_dir/a_file.txt'),
                download_url='https://github_url_for/some_dir/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('some_dir/another_file.py'),
                download_url='https://github_url_for/some_dir/another_file.py'
            ),
            DownloadableFile(
                file_path=Path('some_dir/a_third_file.md'),
                download_url='https://github_url_for/some_dir/a_third_file.md'
            )])

    def test_mix_of_files_and_directory(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('mix_of_files_and_directory')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: Files hierarchy is flattened
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('a_file.txt'),
                download_url='https://github_url_for/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('some_dir/a_file.txt'),
                download_url='https://github_url_for/some_dir/a_file.txt'
            ),
            DownloadableFile(
                file_path=Path('some_dir/another_file.py'),
                download_url='https://github_url_for/some_dir/another_file.py'
            )])

    def test_nested_directories(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('nested_directories')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='')

        # Then: Files hierarchy is flattened
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('file_at_root.txt'),
                download_url='https://github_url_for/file_at_root.txt'
            ),
            DownloadableFile(
                file_path=Path('dir_at_root/file_at_level_1.txt'),
                download_url='https://github_url_for/dir_at_root/file_at_level_1.txt'
            ),
            DownloadableFile(
                file_path=Path('dir_at_root/dir_at_level_1/file_at_level_2.txt'),
                download_url='https://github_url_for/dir_at_root/dir_at_level_1/file_at_level_2.txt'
            ),
            DownloadableFile(
                file_path=Path('dir_at_root/dir_at_level_1/dir_at_level_2/file_at_level_3.txt'),
                download_url='https://github_url_for/dir_at_root/dir_at_level_1/dir_at_level_2/file_at_level_3.txt'
            )])

    def test_nested_directories_path_isn_t_root(self, repo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        repo_with_scenario.init_scenario('nested_directories')

        # When: Fetching the root path: ''
        result = repo_with_scenario.file_urls(path='dir_at_root/dir_at_level_1')

        # Then: Files hierarchy is flattened
        assert sort_by_file_path(result) == sort_by_file_path([
            DownloadableFile(
                file_path=Path('dir_at_root/dir_at_level_1/file_at_level_2.txt'),
                download_url='https://github_url_for/dir_at_root/dir_at_level_1/file_at_level_2.txt'
            ),
            DownloadableFile(
                file_path=Path('dir_at_root/dir_at_level_1/dir_at_level_2/file_at_level_3.txt'),
                download_url='https://github_url_for/dir_at_root/dir_at_level_1/dir_at_level_2/file_at_level_3.txt'
            )])
