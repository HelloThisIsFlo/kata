import requests


class Api:
    """
    Basic wrapper around the Github Api
    """

    def contents(self, user, repo, path=''):
        url = f'https://api.github.com/repos/{user}/{repo}/contents'
        if path:
            url += f'/{path}'

        response = requests.get(url)
        # TODO: Maybe throw exceptions if not `200` or if specifically `404`/'Not Found'
        return response.json()
