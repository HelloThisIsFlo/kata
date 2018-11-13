from pathlib import Path
from typing import List

from .github.api import Api
from .models import DownloadableFile


class Downloader:
    def __init__(self, api: Api):
        self._api = api

    def download_file_at_location(self, root_dir: Path, files_to_download: List[DownloadableFile]) -> None:
        # Note: No need to implement multi-threading here
        # => A lot of complexity (IO access to the drive) vs 0 perf gain.
        # EDIT: Actually totally wrong !! --> Completely forgot about the 'download' part.
        if not root_dir.exists() or not root_dir.is_dir():
            raise ValueError(f"Root dir '{root_dir}' isn't a valid directory")

        for file_to_download in files_to_download:
            file_content = self._api.download_raw_text_file(file_to_download.download_url)
            self._write_to_file_in_sub_path(root_dir, Path(file_to_download.file_path), file_content)

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
