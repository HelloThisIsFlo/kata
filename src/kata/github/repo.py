from concurrent import futures

from .api import Api


class Repo:

    def __init__(self, api: Api, executor: futures.Executor):
        self.api = api
        self.executor = executor

    def file_urls(self, user, repo, path):
        """
        Explore recursively a repo and extract the file list

        :param user: Github Username
        :param repo: Github Repo
        :param path: Path in the Repo
        :return: Flat list of all files recursively found along with their download URLs
        """
        files = self.get_files_in_dir(user, repo, path)
        return self.format_result(files)

    def get_files_in_dir(self, user, repo, dir_path):
        def filter_by_type(contents, content_type):
            return [entry for entry in contents if entry['type'] == content_type]

        def get_files_in_all_sub_dirs_async():
            sub_dir_files_futures = []
            for sub_dir in sub_dirs:
                sub_dir_path = f"{dir_path}/{sub_dir['name']}".lstrip('/')
                sub_dir_files_future = self.executor.submit(self.get_files_in_dir, user, repo, sub_dir_path)
                sub_dir_files_futures += [sub_dir_files_future]

            all_sub_dir_files = []
            for sub_dir_files_future in futures.as_completed(sub_dir_files_futures):
                sub_dir_files = sub_dir_files_future.result()
                all_sub_dir_files += sub_dir_files

            return all_sub_dir_files

        dir_contents = self.api.contents(user, repo, dir_path)
        files = filter_by_type(dir_contents, 'file')
        sub_dirs = filter_by_type(dir_contents, 'dir')
        return files + get_files_in_all_sub_dirs_async()

    @staticmethod
    def format_result(contents):
        return [{
            'file_path': file['path'],
            'download_url': file['download_url']
        } for file in contents]
