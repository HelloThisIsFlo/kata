from concurrent import futures
from pprint import pprint

import click

from .github.api import Api
from .github.repo import Repo


@click.command()
@click.argument('github_user')
@click.argument('repo')
@click.argument('path', default='')
def cli(github_user, repo, path):
    thread_pool_executor = futures.ThreadPoolExecutor(100, thread_name_prefix='subdir-explorer-')
    api = Api()
    repo_obj = Repo(api, thread_pool_executor)

    click.echo('Debug - Print all files in repo')
    click.echo('')
    click.echo('Exploring:')
    click.echo(f" - User: '{github_user}'")
    click.echo(f" - Repo: '{repo}'")
    click.echo(f" - Path: '{path}'")
    click.echo('')
    repo_obj._format_result()
    result = repo_obj.file_urls(github_user, repo, path)
    pprint(result)
    click.echo('')
    click.echo('Done')
