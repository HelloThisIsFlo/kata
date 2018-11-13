from typing import List

from .github.api import Api
from .models import DownloadableFile


class Downloader:
    def __init__(self, api: Api):
        self.api = api

    def download_file_at_location(self, root_dir, files_to_download: List[DownloadableFile]):
        pass
