import textwrap
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pprint import pprint

import pytest
import requests

from kata.data.io.file import FileWriter
from kata.data.io.network import GithubApi
from kata.data.repos import KataTemplateRepo, HardCoded
from kata.domain.grepo import GRepo
from kata.domain.models import KataTemplate
from kata.domain.services import InitKataService


class SandboxContext:
    def __init__(self):
        self.executor = ThreadPoolExecutor(100)
        self.api = GithubApi()
        self.file_writer = FileWriter()
        self.grepo = GRepo(self.api, self.file_writer, self.executor)
        self.kata_template_repo = HardCoded.KataTemplateRepo()
        self.real_kata_template_repo = KataTemplateRepo(self.api)
        self.sandbox_dir = Path('../sandbox')
        self.init_kata_service = InitKataService(self.kata_template_repo, self.grepo)


class TestSandbox:

    @pytest.mark.skip(reason=None)
    def test_explore_repo(self):
        github_user = 'FlorianKempenich'
        # repo_name = 'ansible-role-python-virtualenv'
        repo_name = 'My-Java-Archetype'
        path = ''
        thread_pool_executor = futures.ThreadPoolExecutor(100, thread_name_prefix='subdir-explorer-')
        api = GithubApi()
        repo = GRepo(api, thread_pool_executor)

        result = repo.get_files_to_download(github_user, repo_name, path)
        pprint(result)

    @pytest.mark.skip
    def test_download_raw_file(self):
        res = requests.get(
            'https://raw.githubusercontent.com/FlorianKempenich/kata/master/README.md')

        print(res.text)

    @pytest.mark.skip
    def test_invalid_file(self):
        res = requests.get('https://raw.githubusercontent.com/asdf')
        res = requests.get(
            'https://raw.githubusercontent.com/FlorianKempenich/kata/master/R.sdfasdfasdmd')
        res.raise_for_status()
        # res = requests.get('asdfadsf')

        print(res)
        print(res.text)

    @pytest.mark.skip
    def test_write_subpath(self):
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
    def test_for_loop_scope(self):
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

    @pytest.mark.skip
    def test_kata_template_repo(self):
        repo = KataTemplateRepo()

        assert repo.get_all() == [
            KataTemplate('java', 'junit5'),
            KataTemplate('java', 'some-other'),
            KataTemplate('js', 'jasminesomething'),
            KataTemplate('js', 'maybe-mocha')
        ]
        assert repo.get_for_language('java') == [
            KataTemplate('java', 'junit5'),
            KataTemplate('java', 'some-other')
        ]

    @pytest.mark.skip
    def test_raise_if_used(self):
        class ShouldNeverBeUsed:
            def __getattribute__(self, name):
                raise NotImplementedError("This object/variable should never be used/access in this test")

            def __str__(self):
                raise NotImplementedError("This object/variable should never be used/access in this test")

        a = ShouldNeverBeUsed()
        # print(a)
        print(a.test)

    @pytest.mark.skip
    def test_asdfasdf(self):
        context = SandboxContext()
        context.kata_template_repo.available_templates = {'java': ['junit5', 'hamcrest']}
        context.init_kata_service.init_kata(context.sandbox_dir, 'hey_yo', 'java', 'junit5')

    @pytest.mark.skip
    def test_list_kata_templates(self):
        context = SandboxContext()

        def print_templates(language):
            templates = context.real_kata_template_repo.get_for_language(language)
            print(templates)

        print_templates('python')
        print_templates('java')
        print_templates('rust')
        print_templates('ruby')
        print_templates('elixir')
        print_templates('csharp')
