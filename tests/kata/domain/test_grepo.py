from pathlib import Path
from typing import List
from unittest import mock

import pytest

from kata.data.io.file import FileWriter
from kata.data.io.network import GithubApi
from kata.domain.grepo import GRepo
from kata.domain.models import DownloadableFile

NOT_USED = 'Not Used'


@pytest.fixture
@mock.patch('src.kata.data.io.network.GithubApi')
def mock_api(mocked_api):
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

    def return_scenario_given_as_repo_name(_user, repo, path):
        scenario = repo
        if scenario not in mocked_contents_scenarios:
            raise ValueError(f"Scenario: '{scenario}' doesn't correspond to a valid scenario")
        if path not in mocked_contents_scenarios[scenario]:
            raise ValueError(f"Path: '{path}' doesn't correspond to a valid path for the scenario: '{scenario}'")

        return mocked_contents_scenarios[scenario][path]

    mocked_api.contents.side_effect = return_scenario_given_as_repo_name
    return mocked_api


@pytest.fixture
def grepo(mock_api, thread_pool_executor):
    file_writer = FileWriter()
    return GRepo(mock_api, file_writer, thread_pool_executor)


def sort_by_file_path(files: List[DownloadableFile]):
    def file_path(file_entry: DownloadableFile):
        return file_entry.file_path

    return sorted(files, key=file_path)


class TestGetFileUrls:
    @pytest.fixture
    def grepo_with_scenario(self, grepo):
        class RepoWithScenario:
            def __init__(self, grepo):
                self.scenario = None
                self._grepo = grepo

            def init_scenario(self, scenario):
                self.scenario = scenario

            def get_files_to_download(self, path):
                return self._grepo.get_files_to_download(user=NOT_USED, repo=self.scenario, path=path)

        return RepoWithScenario(grepo)

    def test_only_files(self, grepo_with_scenario):
        # Given: A repo containing only files | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('only_files')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_directory_containing_files(self, grepo_with_scenario):
        # Given: A repo containing a dir, itself containing files | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('directory_containing_files')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_multiple_directories_containing_files(self, grepo_with_scenario):
        # Given: A repo containing multiple dirs, themselves containing files | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('multiple_directories_containing_files')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_multiple_directories_one_is_empty(self, grepo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('multiple_directories_one_is_empty')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_mix_of_files_and_directory(self, grepo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('mix_of_files_and_directory')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_nested_directories(self, grepo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('nested_directories')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='')

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

    def test_nested_directories_path_isn_t_root(self, grepo_with_scenario):
        # Given: A repo containing multiple dirs, one of them is empty | See: `mocked_contents_scenarios`
        grepo_with_scenario.init_scenario('nested_directories')

        # When: Fetching the root path: ''
        result = grepo_with_scenario.get_files_to_download(path='dir_at_root/dir_at_level_1')

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


class TestDownloadFilesAtLocation:
    class TestSingleFile:
        class SingleFileTestHelper:
            def __init__(self, mock_api: GithubApi, grepo: GRepo):
                self._mock_api = mock_api
                self._grepo = grepo

            def test_file_is_downloaded_and_saved_with_correct_content(self,
                                                                       root_dir: Path,
                                                                       file_to_download: DownloadableFile,
                                                                       file_content: str):
                def return_file_content_only_for_correct_url(url):
                    if url == file_to_download.download_url:
                        return file_content
                    else:
                        pytest.fail(f"Api wasn't called with the correct url | Incorrect URL: {url}")

                # Given: Mock Api returning the file contents only if queried with the correct url
                self._mock_api.download_raw_text_file.side_effect = return_file_content_only_for_correct_url

                # When: Downloading file at location
                self._grepo.download_files_at_location(root_dir, [file_to_download])

                # Then: File was downloaded and saved w/ correct content
                expected_file_path = root_dir / file_to_download.file_path
                assert expected_file_path.exists()
                with expected_file_path.open('r') as expected_file:
                    assert expected_file.read() == file_content

        @pytest.fixture
        def single_file_test_helper(self, mock_api: GithubApi, grepo):
            return __class__.SingleFileTestHelper(mock_api, grepo)

        def test_at_root(self, tmp_path: Path, single_file_test_helper):
            file = DownloadableFile(file_path=Path('file.txt'), download_url='http://this_is_the_url/file.txt')

            single_file_test_helper.test_file_is_downloaded_and_saved_with_correct_content(
                root_dir=tmp_path,
                file_to_download=file,
                file_content='EXPECTED TEXT CONTENT')

        def test_empty_file(self, tmp_path: Path, single_file_test_helper):
            file = DownloadableFile(file_path=Path('file.txt'), download_url='http://this_is_the_url/file.txt')

            single_file_test_helper.test_file_is_downloaded_and_saved_with_correct_content(
                root_dir=tmp_path,
                file_to_download=file,
                file_content='')

        def test_in_sub_path(self, tmp_path: Path, single_file_test_helper):
            file = DownloadableFile(file_path=Path('this/is/a/sub_path/file.txt'),
                                    download_url='http://this_is_the_url/this/is/a/sub_path/file.txt')

            single_file_test_helper.test_file_is_downloaded_and_saved_with_correct_content(
                root_dir=tmp_path,
                file_to_download=file,
                file_content='EXPECTED TEXT CONTENT')

        def test_file_has_different_name_in_url(self, tmp_path: Path, single_file_test_helper):
            file = DownloadableFile(file_path=Path('correct_name.txt'),
                                    download_url='http://this_is_the_url/wrong_name.md')
            root_dir = tmp_path

            single_file_test_helper.test_file_is_downloaded_and_saved_with_correct_content(
                root_dir=root_dir,
                file_to_download=file,
                file_content='EXPECTED TEXT CONTENT')

            # Already tested in helper, but re-tested here for clarity of intent
            expected_written_file_path = root_dir / 'correct_name.txt'
            assert expected_written_file_path.exists()

    class TestMultipleFiles:
        def test_diverse_multiple_files(self, tmp_path: Path, mock_api: GithubApi, grepo: GRepo):
            def return_file_content_for_correct_url(url):
                mock_content_for_url = {
                    'http://this_is_the_url/file_1.md': "CONTENT FOR 'file_1.md'",
                    'http://this_is_the_url/file_2.md': "CONTENT FOR 'file_2.md'",
                    'http://this_is_the_url/file_with_wrong_name_in_url.txt': "CONTENT FOR 'file_3.md'",
                    'http://this_is_the_url/file_empty.md': "",
                    'http://this_is_the_url/sub/path/file_in_sub_path.md': "CONTENT FOR 'file_in_sub_path.md'",
                }
                if url not in mock_content_for_url:
                    pytest.fail(f"Api wasn't called with the correct url | Incorrect URL: {url}")
                return mock_content_for_url[url]

            # GIVEN: A list of DownloadableFiles w/ content available in the Mock Api
            mock_api.download_raw_text_file.side_effect = return_file_content_for_correct_url
            files_to_download = [
                DownloadableFile(file_path=Path('file_1.md'),
                                 download_url='http://this_is_the_url/file_1.md'),
                DownloadableFile(file_path=Path('file_2.md'),
                                 download_url='http://this_is_the_url/file_2.md'),
                DownloadableFile(file_path=Path('file_3.md'),
                                 download_url='http://this_is_the_url/file_with_wrong_name_in_url.txt'),
                DownloadableFile(file_path=Path('file_empty.md'),
                                 download_url='http://this_is_the_url/file_empty.md'),
                DownloadableFile(file_path=Path('sub/path/file_in_sub_path.md'),
                                 download_url='http://this_is_the_url/sub/path/file_in_sub_path.md')]

            # WHEN: Downloading all files
            root_dir = tmp_path
            grepo.download_files_at_location(root_dir=root_dir, files_to_download=files_to_download)

            # THEN: All files have been correctly downloaded
            def assert_file_at_path_has_content(file_path: Path, expected_content: str):
                assert file_path.exists()
                with file_path.open('r') as downloaded_file:
                    assert downloaded_file.read() == expected_content

            assert_file_at_path_has_content(root_dir / 'file_1.md', "CONTENT FOR 'file_1.md'")
            assert_file_at_path_has_content(root_dir / 'file_2.md', "CONTENT FOR 'file_2.md'")
            assert_file_at_path_has_content(root_dir / 'file_3.md', "CONTENT FOR 'file_3.md'")
            assert_file_at_path_has_content(root_dir / 'file_empty.md', "")
            assert_file_at_path_has_content(root_dir / 'sub/path/file_in_sub_path.md',
                                            "CONTENT FOR 'file_in_sub_path.md'")

    @pytest.mark.usefixtures('ensure_mock_api_isn_t_called')
    class TestEdgeCases:
        @pytest.fixture
        def ensure_mock_api_isn_t_called(self, mock_api: GithubApi):
            mock_api.download_raw_text_file.side_effect = NotImplementedError

        def test_empty_list(self, tmp_path: Path, grepo: GRepo):
            root_dir = tmp_path
            empty_list = []
            grepo.download_files_at_location(root_dir, empty_list)
            for _ in root_dir.iterdir():
                pytest.fail('root_dir should be empty but was not!!')

        def test_root_dir_doesnt_exist(self, grepo: GRepo):
            # Given: Root dir doesn't exist

            root_dir = Path('this/does/not/exist')
            assert not root_dir.exists()

            # When: Trying to download files
            # Then: An exception is raised
            with pytest.raises(ValueError) as raised_exception:
                grepo.download_files_at_location(root_dir,
                                                 [DownloadableFile(Path('file.txt'), 'http://url.com/file.txt')])
            assert raised_exception.match("Root dir 'this/does/not/exist' isn't a valid directory")

        def test_root_dir_isn_t_a_dir(self, tmp_path: Path, grepo: GRepo):
            # Given: Root dir isn't a 'directory'
            not_a_dir = tmp_path / 'not_a_dir'
            with not_a_dir.open('w') as file:
                file.write('I am not a dir')
            assert not not_a_dir.is_dir()

            # When: Trying to download files
            # Then: An exception is raised
            with pytest.raises(ValueError) as raised_exception:
                grepo.download_files_at_location(root_dir=not_a_dir,
                                                 files_to_download=[DownloadableFile(Path('file.txt'),
                                                                                     'http://url.com/file.txt')])
            assert raised_exception.match(r"Root dir '.*not_a_dir' isn't a valid directory")
