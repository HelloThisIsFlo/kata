from typing import NamedTuple


class DownloadableFile(NamedTuple):
    file_path: str
    download_url: str
