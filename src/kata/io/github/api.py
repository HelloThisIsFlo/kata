import requests


class Api:
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
        # TODO: Maybe throw exceptions if not `200` or if specifically `404`/'Not Found'
        return response.json()

    def download_raw_text_file(self, raw_text_file_url: str):
        # self.get_url('')
        raise NotImplementedError()

    def _get_url(self, url: str):
        response = self._requests.get(url)
        return response
