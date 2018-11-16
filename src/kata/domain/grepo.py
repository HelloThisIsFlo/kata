from concurrent import futures
from pathlib import Path
from typing import NamedTuple, List

from ..data.io.file import FileWriter
from ..data.io.network import GithubApi
from ..domain.models import DownloadableFile


class _DownloadedFile(NamedTuple):
    file_path: Path
    file_text_contents: str


class GRepo:

    def __init__(self, api: GithubApi, file_writer: FileWriter(), executor: futures.Executor):
        self._api = api
        self._executor = executor
        self._file_writer = file_writer

    def get_files_to_download(self, user, repo, path):
        """
        Explore recursively a repo and extract the file list

        :param user: Github Username
        :param repo: Github Repo
        :param path: Path in the Repo
        :return: Flat list of all files recursively found along with their download URLs
        """
        files = self._get_files_in_dir(user, repo, path)
        return self._format_result(files)

    def download_files_at_location(self, root_dir: Path, files_to_download: List[DownloadableFile]) -> None:
        if not root_dir.exists() or not root_dir.is_dir():
            raise ValueError(f"Root dir '{root_dir}' isn't a valid directory")

        download_file_futures = []
        for file_to_download in files_to_download:
            download_file_futures.append(
                self._executor.submit(self._download_file, file_to_download))

        for download_file_future in futures.as_completed(download_file_futures):
            downloaded_file = download_file_future.result()
            self._file_writer.write_to_file_in_sub_path(root_dir,
                                                        downloaded_file.file_path,
                                                        downloaded_file.file_text_contents)

    def _get_files_in_dir(self, user, repo, dir_path):
        def filter_by_type(contents, content_type):
            return [entry for entry in contents if entry['type'] == content_type]

        def get_files_in_all_sub_dirs_async():
            sub_dir_files_futures = []
            for sub_dir in sub_dirs:
                sub_dir_path = f"{dir_path}/{sub_dir['name']}".lstrip('/')
                sub_dir_files_future = self._executor.submit(self._get_files_in_dir, user, repo, sub_dir_path)
                sub_dir_files_futures += [sub_dir_files_future]

            all_sub_dir_files = []
            for sub_dir_files_future in futures.as_completed(sub_dir_files_futures):
                sub_dir_files = sub_dir_files_future.result()
                all_sub_dir_files += sub_dir_files

            return all_sub_dir_files

        dir_contents = self._api.contents(user, repo, dir_path)
        files = filter_by_type(dir_contents, 'file')
        sub_dirs = filter_by_type(dir_contents, 'dir')
        return files + get_files_in_all_sub_dirs_async()

    @staticmethod
    def _format_result(contents):
        return [
            DownloadableFile(
                file_path=Path(file['path']),
                download_url=file['download_url']
            ) for file in contents]

    def _download_file(self, file: DownloadableFile):
        file_contents = self._api.download_raw_text_file(file.download_url)
        return _DownloadedFile(file_path=file.file_path, file_text_contents=file_contents)
