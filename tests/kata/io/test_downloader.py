# Test here with temp dir / temp files injected with pyenv that:
#     - Single DownloadableFile in entry is actually downloaded
#     - List of DownloadableFile in entry are actually downloaded
#     - Edge cases
from pathlib import Path
from unittest import mock

import pytest

from src.kata.io.downloader import Downloader
from src.kata.io.github.api import Api
from src.kata.io.models import DownloadableFile


@pytest.fixture
@mock.patch('src.kata.io.github.api.Api')
def mock_api(mocked_api):
    return mocked_api


@pytest.fixture
def downloader(mock_api):
    return Downloader(mock_api)


@pytest.fixture
def helper(mock_api: Api, downloader: Downloader):
    return Helper(mock_api, downloader)


class TestSingleFile:

    def test_at_root(self, tmp_path: Path, helper):
        file = DownloadableFile(file_path=Path('file.txt'), download_url='http://this_is_the_url/file.txt')

        helper.test_file_is_downloaded_and_saved_with_correct_content(
            root_dir=tmp_path,
            file_to_download=file,
            file_content='EXPECTED TEXT CONTENT')

    def test_empty_file(self, tmp_path: Path, helper):
        file = DownloadableFile(file_path=Path('file.txt'), download_url='http://this_is_the_url/file.txt')

        helper.test_file_is_downloaded_and_saved_with_correct_content(
            root_dir=tmp_path,
            file_to_download=file,
            file_content='')

    def test_in_sub_path(self, tmp_path: Path, helper):
        file = DownloadableFile(file_path=Path('this/is/a/sub_path/file.txt'),
                                download_url='http://this_is_the_url/this/is/a/sub_path/file.txt')

        helper.test_file_is_downloaded_and_saved_with_correct_content(
            root_dir=tmp_path,
            file_to_download=file,
            file_content='EXPECTED TEXT CONTENT')

    def test_file_has_different_name_in_url(self, tmp_path: Path, helper):
        file = DownloadableFile(file_path=Path('correct_name.txt'), download_url='http://this_is_the_url/wrong_name.md')
        root_dir = tmp_path

        helper.test_file_is_downloaded_and_saved_with_correct_content(
            root_dir=root_dir,
            file_to_download=file,
            file_content='EXPECTED TEXT CONTENT')

        # Already tested in helper, but re-tested here for clarity of intent
        expected_written_file_path = root_dir / 'correct_name.txt'
        assert expected_written_file_path.exists()


class Helper:
    def __init__(self, mock_api: Api, downloader: Downloader):
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
        self._downloader.download_file_at_location(root_dir, [file_to_download])

        # Then: File was downloaded and saved w/ correct content
        expected_file_path = root_dir / file_to_download.file_path
        assert expected_file_path.exists()
        with expected_file_path.open('r') as expected_file:
            assert expected_file.read() == file_content
