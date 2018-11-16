from concurrent import futures
from pathlib import Path

from ..domain.models import DownloadableFile
from ..io.network import GithubApi


class GRepo:

    def __init__(self, api: GithubApi, executor: futures.Executor):
        self._api = api
        self._executor = executor

    def get_file_urls(self, user, repo, path):
        """
        Explore recursively a repo and extract the file list

        :param user: Github Username
        :param repo: Github Repo
        :param path: Path in the Repo
        :return: Flat list of all files recursively found along with their download URLs
        """
        files = self._get_files_in_dir(user, repo, path)
        return self._format_result(files)

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
