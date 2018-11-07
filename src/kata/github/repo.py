from .api import Api


class Repo:

    def __init__(self, api: Api):
        self.api = api

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
        # TODO: Implement using multi-threading (add 0.5 sec delay in fake repo for dev purposes, remove then)
        dir_contents = self.api.contents(user, repo, dir_path)

        def filter_by_type(contents, content_type):
            return [entry for entry in contents if entry['type'] == content_type]

        files = filter_by_type(dir_contents, 'file')
        sub_dirs = filter_by_type(dir_contents, 'dir')

        for sub_dir in sub_dirs:
            sub_dir_path = f"{dir_path}/{sub_dir['name']}".lstrip('/')
            sub_dir_files = self.get_files_in_dir(user, repo, sub_dir_path)
            files += sub_dir_files

        return files

    @staticmethod
    def format_result(contents):
        return [{
            'file_path': file['path'],
            'download_url': file['download_url']
        } for file in contents]
