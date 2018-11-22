import requests

from kata.domain.exceptions import ApiLimitReached


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

        # X - RateLimit - Limit
        # 403
        response = self._get_url(url)
        return response.json()

    def download_raw_text_file(self, raw_text_file_url: str):
        response = self._get_url(raw_text_file_url)
        return response.text

    def _get_url(self, url: str):
        response = self._requests.get(url)
        self._validate_response(response)
        return response

    @staticmethod
    def _validate_response(response: requests.Response):
        def rate_limit_reached():
            def unauthorised():
                return response.status_code == 403

            def limit_reached():
                return int(response.headers.get('X-RateLimit-Remaining', -1)) == 0

            return unauthorised() and limit_reached()

        if rate_limit_reached():
            raise ApiLimitReached()
        response.raise_for_status()
