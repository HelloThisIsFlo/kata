from concurrent import futures
from concurrent.futures import Executor
from pathlib import Path
from typing import List, NamedTuple

from .github.api import Api
from ..models import DownloadableFile


class _DownloadedFile(NamedTuple):
    file_path: Path
    file_text_contents: str


class Downloader:
    def __init__(self, api: Api, executor: Executor):
        self._api = api
        self._executor = executor

    def download_files_at_location(self, root_dir: Path, files_to_download: List[DownloadableFile]) -> None:
        if not root_dir.exists() or not root_dir.is_dir():
            raise ValueError(f"Root dir '{root_dir}' isn't a valid directory")

        download_file_futures = []
        for file_to_download in files_to_download:
            download_file_futures.append(
                self._executor.submit(self._download_file, file_to_download))

        for download_file_future in futures.as_completed(download_file_futures):
            downloaded_file = download_file_future.result()
            self._write_to_file_in_sub_path(root_dir, downloaded_file.file_path, downloaded_file.file_text_contents)

    def _download_file(self, file: DownloadableFile):
        file_contents = self._api.download_raw_text_file(file.download_url)
        return _DownloadedFile(file_path=file.file_path, file_text_contents=file_contents)

    @staticmethod
    def _write_to_file_in_sub_path(root_dir: Path, file_sub_path: Path, file_content: str):
        def create_dir_hierarchy_if_does_not_exist():
            file_full_path.parent.mkdir(parents=True, exist_ok=True)

        def write_to_file():
            with file_full_path.open('w') as file:
                file.write(file_content)

        file_full_path = root_dir / file_sub_path
        create_dir_hierarchy_if_does_not_exist()
        write_to_file()
