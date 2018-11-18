from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint
from typing import List

import click

from kata.data.io.file import FileWriter
from kata.data.io.network import GithubApi
from kata.data.repos import KataTemplateRepo, KataLanguageRepo
from kata.domain.exceptions import KataError, KataLanguageNotFound, KataTemplateNotFound
from kata.domain.grepo import GRepo
from kata.domain.models import DownloadableFile
from kata.domain.services import InitKataService


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    main = Main()
    ctx.obj = main


def print_error(msg):
    click.secho(msg, fg='red')


def print_success(msg):
    click.secho(msg, fg='green')


def print_warning(msg):
    click.secho(msg, fg='yellow')


def print_normal(msg):
    click.echo(msg)


@cli.command()
@click.pass_context
@click.argument('kata_name')
@click.argument('template_language')
@click.argument('template_name', required=False)
def init(ctx: click.Context, kata_name, template_language, template_name):
    main_ctx: Main = ctx.obj

    current_dir = Path('.')
    print_normal(f"Initializing Kata in './{kata_name}'")
    print_normal(f"  - Kata Language: '{template_language}'")
    print_normal(f"  - Kata Template: '{template_name}'")
    print_normal("")
    try:
        main_ctx.init_kata_service.init_kata(current_dir, kata_name, template_language, template_name)
        print_success("Done!")

    except KataLanguageNotFound as lang_not_found:
        print_error(f"Language '{template_language}' could not be found!")
        print_error('')
        print_error('Available languages:')
        for lang in lang_not_found.available_languages:
            print_error(f"  - {lang.name}")

    except KataTemplateNotFound as template_not_found:
        def has_only_root_template():
            return len(template_not_found.available_templates) == 1 \
                   and template_not_found.available_templates[0].template_name is None

        print_error(f"Template '{template_name}' could not be found!")
        print_error('')

        if has_only_root_template():
            print_warning(f"Language '{template_language}' only has one template, and its located at its root")
            print_warning(f"To initialize a kata with '{template_language}', simply do not specify any template name:")
            print_warning('')
            print_warning(f"    kata init {kata_name} {template_language}")
            print_warning('')
        else:
            print_error(f"Available templates for '{template_language}':")
            for template in template_not_found.available_templates:
                print_error(f"  - {template.template_name}")
               
    except KataError as error:
        print_error(str(error))


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
        # self.kata_template_repo = HardCodedKataTemplateRepo()
        self.kata_template_repo = KataTemplateRepo(self.api)
        self.kata_language_repo = KataLanguageRepo(self.api)
        self.init_kata_service = InitKataService(self.kata_language_repo, self.kata_template_repo, self.grepo)
