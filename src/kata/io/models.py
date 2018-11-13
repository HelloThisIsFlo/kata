from pathlib import Path
from typing import NamedTuple


class DownloadableFile(NamedTuple):
    file_path: Path
    download_url: str
