from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint
from typing import List

import click

from kata.data.repos import HardCodedKataTemplateRepo
from kata.domain.exceptions import KataError
from kata.domain.services import InitKataService
from ..data.io.file import FileWriter
from ..data.io.network import GithubApi
from ..domain.grepo import GRepo
from ..domain.models import DownloadableFile


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    main = Main()
    ctx.obj = main


@cli.command()
@click.pass_context
@click.argument('kata_name')
@click.argument('template_language')
@click.argument('template_name', required=False)
def init(ctx: click.Context, kata_name, template_language, template_name):
    main_ctx: Main = ctx.obj

    current_dir = Path('.')
    click.echo(f"Initializing Kata '{kata_name}'")
    main_ctx.init_kata_service.init_kata(current_dir, kata_name, template_language, template_name)


@cli.group()
@click.pass_context
def debug(_ctx: click.Context):
    pass


@debug.command()
@click.argument('github_user')
@click.argument('repo')
@click.argument('sub_path_in_repo', default='')
@click.pass_context
def explore(ctx: click.Context, github_user, repo, sub_path_in_repo):
    main_ctx: Main = ctx.obj
    click.echo('Debug - Print all files in repo')
    click.echo('')
    click.echo('Exploring:')
    click.echo(f" - User: '{github_user}'")
    click.echo(f" - Repo: '{repo}'")
    click.echo(f" - SubPath in Repo: '{sub_path_in_repo}'")
    click.echo('')
    result = main_ctx.grepo.get_files_to_download(github_user, repo, sub_path_in_repo)
    pprint(result)
    click.echo('')
    click.echo('Done')


@debug.command()
@click.argument('github_user')
@click.argument('repo')
@click.argument('sub_path_in_repo', default='')
@click.pass_context
def download(ctx: click.Context, github_user, repo, sub_path_in_repo):
    sandbox = Path('./sandbox')
    if not sandbox.exists():
        raise KataError("Please create an empty './sandbox' directory before proceeding")
    for _ in sandbox.iterdir():
        raise KataError("Please create an EMPTY './sandbox' directory before proceeding")

    main_ctx: Main = ctx.obj
    click.echo(f'Sandbox: {sandbox.absolute()}')

    repo_files: List[DownloadableFile] = main_ctx.grepo.get_files_to_download(github_user, repo, sub_path_in_repo)
    click.echo('Finished fetching the list. Writing to drive now')
    main_ctx.grepo.download_files_at_location(sandbox, repo_files)
    click.echo('Done! (probably ^_^)')


class Main:
    def __init__(self):
        self.executor = ThreadPoolExecutor(100)
        self.api = GithubApi()
        self.file_writer = FileWriter()
        self.grepo = GRepo(self.api, self.file_writer, self.executor)
        self.kata_template_repo = HardCodedKataTemplateRepo()
        self.init_kata_service = InitKataService(self.kata_template_repo, self.grepo)
