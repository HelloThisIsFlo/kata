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


class MockApi:
    mocked_responses = {
        'contents': {
            'only_files': [
                {
                    'name': '.travis.yml',
                    'path': '.travis.yml',
                    'type': 'file',
                    'download_url': 'https://github_url_for/.travis.yml'
                },
                {
                    'name': 'LICENSE.md',
                    'path': 'LICENSE.md',
                    'type': 'file',
                    'download_url': 'https://github_url_for/LICENSE.md'
                },
                {
                    'name': 'README.md',
                    'path': 'README.md',
                    'type': 'file',
                    'download_url': 'https://github_url_for/README.md'
                }
            ],
            'dir_containing_files': [

            ],
            'empty_dir': [

            ],
            'nested_dirs': [

            ],
            'mixed_files_and_dir': [

            ]

        }
    }

    def contents(self, _user, _repo, path):
        if path not in self.mocked_responses['contents']:
            raise ValueError(f"Path: '{path}' doesn't correspond to a valid mocked response")
        return self.mocked_responses['contents'][path]
