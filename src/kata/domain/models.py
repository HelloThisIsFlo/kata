from pathlib import Path
from typing import NamedTuple


class DownloadableFile(NamedTuple):
    file_path: Path
    download_url: str


class KataTemplate(NamedTuple):
    language: str
    template_name: str
