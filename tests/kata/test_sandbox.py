import textwrap
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint

import pytest
import requests

from kata.io.downloader import Downloader
from src.kata.io.github.api import GithubApi
from src.kata.io.github.repo import GithubRepo


class SandboxHelper:
    def __init__(self):
        self.executor = ThreadPoolExecutor(100)
        self.api = GithubApi()
        self.repo_explorer = GithubRepo(self.api, self.executor)
        self.downloader = Downloader(self.api, self.executor)
        self.sandbox_dir = Path('../sandbox')


@pytest.mark.skip
def test_explore_repo():
    github_user = 'FlorianKempenich'
    # repo_name = 'ansible-role-python-virtualenv'
    repo_name = 'My-Java-Archetype'
    path = ''
    thread_pool_executor = futures.ThreadPoolExecutor(100, thread_name_prefix='subdir-explorer-')
    api = GithubApi()
    repo = GithubRepo(api, thread_pool_executor)

    result = repo.file_urls(github_user, repo_name, path)
    pprint(result)


@pytest.mark.skip
def test_download_raw_file():
    res = requests.get(
        'https://raw.githubusercontent.com/FlorianKempenich/kata/master/README.md')

    print(res.text)


@pytest.mark.skip
def test_invalid_file():
    res = requests.get('https://raw.githubusercontent.com/asdf')
    res = requests.get(
        'https://raw.githubusercontent.com/FlorianKempenich/kata/master/R.sdfasdfasdmd')
    res.raise_for_status()
    # res = requests.get('asdfadsf')

    print(res)
    print(res.text)


@pytest.mark.skip
def test_write_subpath():
    def write_sandbox_file(path_relative_to_sandbox_root, content):
        def create_dir_hierarchy_if_does_not_exist():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        def write_to_file():
            with file_path.open('w') as sandbox_file:
                sandbox_file.write(content)

        file_path = Path(SANDBOX_DIR, path_relative_to_sandbox_root)
        create_dir_hierarchy_if_does_not_exist()
        write_to_file()

    write_sandbox_file('hey/bonjour/coucou.md', "This is a test :D")
    write_sandbox_file('iamatroot.txt', "it's working")

    write_sandbox_file('I/should/have/multi/lines/bijor.txt', textwrap.dedent("""\
        Hey this is a multiline
        file tests :D 

        Is it working?
        """))


@pytest.mark.skip
def test_for_loop_scope():
    some_numbers = [1, 3, 5]
    for number in some_numbers:
        declared_inside_loop = number
        print(f'In loop | number = {number}')

    last_number = some_numbers[-1]
    assert declared_inside_loop == last_number

    # for
    # helper = SandboxHelper()
    # helper.downloader.download_file_at_location()
    # downloader = Downloader(Api(), ThreadP)
