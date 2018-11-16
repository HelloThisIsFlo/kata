from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint
from typing import List

import click

from ..data.io.file import FileWriter
from ..data.io.network import GithubApi
from ..domain.grepo import GRepo
from ..domain.models import DownloadableFile


@click.command()
@click.argument('github_user')
@click.argument('repo')
@click.argument('sub_path_in_repo', default='')
def cli(github_user, repo, sub_path_in_repo):
    main = Main()
    # main.explore_github_repo(user=github_user, repo_name=repo, sub_path_in_repo=sub_path_in_repo)
    main.download_github_repo(user=github_user, repo_name=repo, sub_path_in_repo=sub_path_in_repo)


class Main:
    def __init__(self):
        self._executor = ThreadPoolExecutor(100)
        self._api = GithubApi()
        self._file_writer = FileWriter()
        self._grepo = GRepo(self._api, self._file_writer, self._executor)

    def explore_github_repo(self, user, repo_name, sub_path_in_repo):
        click.echo('Debug - Print all files in repo')
        click.echo('')
        click.echo('Exploring:')
        click.echo(f" - User: '{user}'")
        click.echo(f" - Repo: '{repo_name}'")
        click.echo(f" - SubPath in Repo: '{sub_path_in_repo}'")
        click.echo('')
        result = self._grepo.get_files_to_download(user, repo_name, sub_path_in_repo)
        pprint(result)
        click.echo('')
        click.echo('Done')

    def download_github_repo(self, user, repo_name, sub_path_in_repo):
        sandbox = Path('./sandbox')
        sandbox.mkdir(exist_ok=True)
        click.echo(f'Sandbox: {sandbox.absolute()}')

        repo_files: List[DownloadableFile] = self._grepo.get_files_to_download(user, repo_name, sub_path_in_repo)
        click.echo('Finished fetching the list. Writing to drive now')
        self._grepo.download_files_at_location(sandbox, repo_files)
        click.echo('Done! (probably ^_^)')
