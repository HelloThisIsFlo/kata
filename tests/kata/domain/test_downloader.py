# Test here with temp dir / temp files injected with pyenv that:
#     - Single DownloadableFile in entry is actually downloaded
#     - List of DownloadableFile in entry are actually downloaded
#     - Edge cases
from pathlib import Path
from unittest import mock

import pytest

from src.kata.domain.downloader import Downloader
from src.kata.domain.models import DownloadableFile
from src.kata.io.network import GithubApi


@pytest.fixture
@mock.patch('src.kata.io.network.GithubApi')
def mock_api(mocked_api):
    return mocked_api


@pytest.fixture
def downloader(mock_api, thread_pool_executor):
    return Downloader(mock_api, thread_pool_executor)


class TestSingleFile:
    class SingleFileTestHelper:
        def __init__(self, mock_api: GithubApi, downloader: Downloader):
            self._mock_api = mock_api
            self._downloader = downloader

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
            self._downloader.download_files_at_location(root_dir, [file_to_download])

            # Then: File was downloaded and saved w/ correct content
            expected_file_path = root_dir / file_to_download.file_path
            assert expected_file_path.exists()
            with expected_file_path.open('r') as expected_file:
                assert expected_file.read() == file_content

    @pytest.fixture
    def single_file_test_helper(self, mock_api: GithubApi, downloader: Downloader):
        return TestSingleFile.SingleFileTestHelper(mock_api, downloader)

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
        file = DownloadableFile(file_path=Path('correct_name.txt'), download_url='http://this_is_the_url/wrong_name.md')
        root_dir = tmp_path

        single_file_test_helper.test_file_is_downloaded_and_saved_with_correct_content(
            root_dir=root_dir,
            file_to_download=file,
            file_content='EXPECTED TEXT CONTENT')

        # Already tested in helper, but re-tested here for clarity of intent
        expected_written_file_path = root_dir / 'correct_name.txt'
        assert expected_written_file_path.exists()


class TestMultipleFiles:
    def test_diverse_multiple_files(self, tmp_path: Path, mock_api: GithubApi, downloader: Downloader):
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
        downloader.download_files_at_location(root_dir=root_dir, files_to_download=files_to_download)

        # THEN: All files have been correctly downloaded
        def assert_file_at_path_has_content(file_path: Path, expected_content: str):
            assert file_path.exists()
            with file_path.open('r') as downloaded_file:
                assert downloaded_file.read() == expected_content

        assert_file_at_path_has_content(root_dir / 'file_1.md', "CONTENT FOR 'file_1.md'")
        assert_file_at_path_has_content(root_dir / 'file_2.md', "CONTENT FOR 'file_2.md'")
        assert_file_at_path_has_content(root_dir / 'file_3.md', "CONTENT FOR 'file_3.md'")
        assert_file_at_path_has_content(root_dir / 'file_empty.md', "")
        assert_file_at_path_has_content(root_dir / 'sub/path/file_in_sub_path.md', "CONTENT FOR 'file_in_sub_path.md'")


@pytest.mark.usefixtures('ensure_mock_api_isn_t_called')
class TestEdgeCases:
    @pytest.fixture
    def ensure_mock_api_isn_t_called(self, mock_api: GithubApi):
        mock_api.download_raw_text_file.side_effect = NotImplementedError

    def test_empty_list(self, tmp_path: Path, downloader: Downloader):
        root_dir = tmp_path
        empty_list = []
        downloader.download_files_at_location(root_dir, empty_list)
        for _ in root_dir.iterdir():
            pytest.fail('root_dir should be empty but was not!!')

    def test_root_dir_doesnt_exist(self, mock_api: GithubApi, downloader: Downloader):
        # Given: Root dir doesn't exist

        root_dir = Path('this/does/not/exist')
        assert not root_dir.exists()

        # When: Trying to download files
        # Then: An exception is raised
        with pytest.raises(ValueError) as raised_exception:
            downloader.download_files_at_location(root_dir,
                                                  [DownloadableFile(Path('file.txt'), 'http://url.com/file.txt')])
        assert raised_exception.match("Root dir 'this/does/not/exist' isn't a valid directory")

    def test_root_dir_isn_t_a_dir(self, tmp_path: Path, mock_api: GithubApi, downloader: Downloader):
        # Given: Root dir isn't a 'directory'
        not_a_dir = tmp_path / 'not_a_dir'
        with not_a_dir.open('w') as file:
            file.write('I am not a dir')
        assert not not_a_dir.is_dir()

        # When: Trying to download files
        # Then: An exception is raised
        with pytest.raises(ValueError) as raised_exception:
            downloader.download_files_at_location(root_dir=not_a_dir,
                                                  files_to_download=[
                                                      DownloadableFile(Path('file.txt'), 'http://url.com/file.txt')])
        assert raised_exception.match(r"Root dir '.*not_a_dir' isn't a valid directory")
