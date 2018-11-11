import textwrap
from concurrent import futures
from pathlib import Path
from pprint import pprint

import pytest
import requests

from src.kata.io.github.api import Api
from src.kata.io.github.repo import Repo


@pytest.mark.skip
def test_explore_repo():
    github_user = 'FlorianKempenich'
    # repo_name = 'ansible-role-python-virtualenv'
    repo_name = 'My-Java-Archetype'
    path = ''
    thread_pool_executor = futures.ThreadPoolExecutor(100, thread_name_prefix='subdir-explorer-')
    api = Api()
    repo = Repo(api, thread_pool_executor)

    result = repo.file_urls(github_user, repo_name, path)
    pprint(result)


@pytest.mark.skip
def test_download_raw_file():
    res = requests.get(
        'https://raw.githubusercontent.com/FlorianKempenich/kata/master/README.md')

    print(res.text)


SANDBOX_DIR = '../sandbox'


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
