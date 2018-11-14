import requests


class GithubApi:
    """
    Basic wrapper around the Github Api
    """

    def __init__(self):
        self._requests = requests

    def contents(self, user, repo, path=''):
        url = f'https://api.github.com/repos/{user}/{repo}/contents'
        if path:
            url += f'/{path}'

        response = self._get_url(url)
        return response.json()

    def download_raw_text_file(self, raw_text_file_url: str):
        response = self._get_url(raw_text_file_url)
        return response.text

    def _get_url(self, url: str):
        response = self._requests.get(url)
        response.raise_for_status()
        return response
