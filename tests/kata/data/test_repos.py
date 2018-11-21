import textwrap
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pytest

from kata import config
from kata.data.io.file import FileReader
from kata.data.repos import KataTemplateRepo, KataLanguageRepo, ConfigRepo
from kata.domain.exceptions import InvalidConfig
from kata.domain.models import KataTemplate, KataLanguage


def extract_name_from_path(path):
    return path.split('/')[-1]


def mock_file_entry(file_path):
    return {
        'name': extract_name_from_path(file_path),
        'path': file_path,
        'type': 'file',
        'download_url': f'https://github_url_for/{file_path}'
    }


def mock_dir_entry(dir_path):
    return {
        'name': extract_name_from_path(dir_path),
        'path': dir_path,
        'type': 'dir',
        'download_url': None
    }


@pytest.fixture
@mock.patch('src.kata.data.io.network.GithubApi')
def mock_api(mocked_api):
    return mocked_api


class TestKataTemplateRepo:

    @pytest.fixture
    def kata_template_repo(self, mock_api):
        config.has_template_at_root = {}
        return KataTemplateRepo(mock_api)

    class TestGetForLanguage:
        def test_request_contents_of_language_directory(self,
                                                        mock_api: MagicMock,
                                                        kata_template_repo: KataTemplateRepo):
            kata_template_repo.get_for_language(KataLanguage('javascript'))
            mock_api.contents.assert_called_with(config.KATA_GITHUB_REPO_USER, config.KATA_GITHUB_REPO_REPO,
                                                 'javascript')

        class TestTemplateIsAtRoot:
            class TestInfoIsInConfig:
                def test_template_not_at_root(self,
                                              mock_api: MagicMock,
                                              kata_template_repo: KataTemplateRepo):
                    # Given: 'java' is explicitly stated as not having the template at its root
                    config.has_template_at_root = {'java': False}
                    mock_api.contents.return_value = [mock_file_entry('java/some_random_file.txt'),
                                                      mock_file_entry('java/README.md'),
                                                      mock_dir_entry('java/template1'),
                                                      mock_dir_entry('java/template2')]

                    # When: Fetching the available templates for java
                    java_available_templates = kata_template_repo.get_for_language(KataLanguage('java'))

                    # Then: Only one is available and it is the root template (template_name == None)
                    assert java_available_templates == [KataTemplate(KataLanguage('java'), template_name='template1'),
                                                        KataTemplate(KataLanguage('java'), template_name='template2')]

                def test_template_at_root(self,
                                          mock_api: MagicMock,
                                          kata_template_repo: KataTemplateRepo):
                    # Given: 'rust' is explicitly stated as having the template at its root
                    config.has_template_at_root = {'rust': True}
                    mock_api.contents.return_value = [mock_file_entry('rust/some_random_file.txt'),
                                                      mock_dir_entry('rust/some_dir')]

                    # When: Fetching the available templates for rust
                    rust_available_templates = kata_template_repo.get_for_language(KataLanguage('rust'))

                    # Then: Only one is available and it is the root template (template_name == None)
                    assert rust_available_templates == [KataTemplate(KataLanguage('rust'), template_name=None)]

            class TestInfoIsNotInConfig:
                def test_check_if_has_readme(self,
                                             mock_api: MagicMock,
                                             kata_template_repo: KataTemplateRepo):
                    # If there's no information in the config whether this language has its template at root,
                    # try to guess by checking if there's a 'README.md' in the language root dir

                    # Given:
                    # - 'golang' isn't included in the list of languages w/ a template at root
                    # - there's a 'README.md' at 'golang' dir root
                    config.has_template_at_root = {}
                    mock_api.contents.return_value = [mock_file_entry('golang/README.md')]

                    # When: Fetching the available templates for java
                    available_java_templates = kata_template_repo.get_for_language(KataLanguage('golang'))

                    # Then: Only one is available and it is the root template (template_name == None)
                    assert len(available_java_templates) == 1
                    assert available_java_templates[0] == KataTemplate(KataLanguage('golang'), template_name=None)

        def test_template_is_not_at_root(self,
                                         mock_api: MagicMock,
                                         kata_template_repo: KataTemplateRepo):
            # Given: There are multiple directories at root of the language dir
            mock_api.contents.return_value = [mock_dir_entry('java/junit5'),
                                              mock_dir_entry('java/hamcrest')]

            # When: Fetching the available templates for java
            available_java_templates = kata_template_repo.get_for_language(KataLanguage('java'))

            # Then: All available templates are returned
            assert available_java_templates == [KataTemplate(KataLanguage('java'), 'junit5'),
                                                KataTemplate(KataLanguage('java'), 'hamcrest')]


class TestKataLanguageRepo:

    @pytest.fixture
    def kata_language_repo(self, mock_api):
        config.has_template_at_root = {}
        return KataLanguageRepo(mock_api)

    class TestGetAll:
        def test_request_contents_of_root_directory(self,
                                                    mock_api: MagicMock,
                                                    kata_language_repo: KataLanguageRepo):
            kata_language_repo.get_all()
            mock_api.contents.assert_called_with(config.KATA_GITHUB_REPO_USER,
                                                 config.KATA_GITHUB_REPO_REPO,
                                                 '')

        def test_return_all_directory_as_kata_languages(self,
                                                        mock_api: MagicMock,
                                                        kata_language_repo: KataLanguageRepo):
            mock_api.contents.return_value = [mock_file_entry('some_random_file.txt'),
                                              mock_dir_entry('java'),
                                              mock_file_entry('README.md'),
                                              mock_dir_entry('rust')]
            all_languages = kata_language_repo.get_all()
            assert all_languages == [KataLanguage('java'),
                                     KataLanguage('rust')]

    class TestGet:
        def test_request_contents_of_root_directory(self,
                                                    mock_api: MagicMock,
                                                    kata_language_repo: KataLanguageRepo):
            kata_language_repo.get(language_name='java')
            mock_api.contents.assert_called_with(config.KATA_GITHUB_REPO_USER,
                                                 config.KATA_GITHUB_REPO_REPO,
                                                 '')

        def test_valid_language_name(self,
                                     mock_api: MagicMock,
                                     kata_language_repo: KataLanguageRepo):
            mock_api.contents.return_value = [mock_file_entry('some_random_file.txt'),
                                              mock_dir_entry('java'),
                                              mock_file_entry('README.md'),
                                              mock_dir_entry('rust')]
            assert kata_language_repo.get('java') == KataLanguage('java')

        def test_invalid_language_name(self,
                                       mock_api: MagicMock,
                                       kata_language_repo: KataLanguageRepo):
            mock_api.contents.return_value = [mock_file_entry('some_random_file.txt'),
                                              mock_dir_entry('java'),
                                              mock_file_entry('README.md'),
                                              mock_dir_entry('rust')]
            assert kata_language_repo.get('doesnotexist') is None


class TestConfigRepo:
    @pytest.fixture
    @mock.patch('src.kata.data.io.file.FileReader')
    def mock_file_reader(self, mocked_file_reader):
        return mocked_file_reader

    @pytest.fixture
    def valid_config(self):
        return {'KataGRepo': {'User': 'some_user',
                              'Repo': 'some_repo'},
                'HasTemplateAtRoot': {'python': False}}

    def test_load_config_at_initialization(self, valid_config, mock_file_reader):
        # Given: A config file path with valid config
        config_file = Path('config_file.yaml')
        mock_file_reader.read_yaml.return_value = valid_config

        # When: Initializing repo
        _config_repo = ConfigRepo(config_file, mock_file_reader)

        # Then: Config file has been loaded
        mock_file_reader.read_yaml.assert_called_with(config_file)

    class TestGetKataGRepoInfos:
        def test_get_kata_grepo_username(self, mock_file_reader):
            config_file = Path('NOT USED - MOCKED IN MOCK_FILE_READER')
            mock_file_reader.read_yaml.return_value = {'KataGRepo': {'User': 'my_username',
                                                                     'Repo': 'my_repo_name'}}
            config_repo = ConfigRepo(config_file, mock_file_reader)
            assert config_repo.get_kata_grepo_username() == 'my_username'

        def test_get_kata_grepo_reponame(self, mock_file_reader):
            config_file = Path('NOT USED - MOCKED IN MOCK_FILE_READER')
            mock_file_reader.read_yaml.return_value = {'KataGRepo': {'User': 'my_username',
                                                                     'Repo': 'my_repo_name'}}
            config_repo = ConfigRepo(config_file, mock_file_reader)
            assert config_repo.get_kata_grepo_reponame() == 'my_repo_name'

    class TestHasTemplateAtRoot:
        @pytest.fixture
        def config_repo(self, mock_file_reader, valid_config):
            config_file = Path('NOT USED - MOCKED IN MOCK_FILE_READER')
            valid_config['HasTemplateAtRoot'] = {'java': False,
                                                 'elixir': True}
            mock_file_reader.read_yaml.return_value = valid_config
            return ConfigRepo(config_file, mock_file_reader)

        def test_has_template(self, config_repo: ConfigRepo):
            assert config_repo.has_template_at_root(KataLanguage('java')) is False

        def test_doesnt_have_template(self, config_repo: ConfigRepo):
            assert config_repo.has_template_at_root(KataLanguage('elixir')) is True

        def test_no_information_whether_or_not_template_is_located_at_root(self, config_repo: ConfigRepo):
            assert config_repo.has_template_at_root(KataLanguage('csharp')) is None

    class TestConfigValidation:
        # TODO: - Add validation w/ schema (even maybe usign external lib: https://github.com/keleshev/schema)
        # TODO: - Also test that if config isn't found, it creates it and loads with defaults

        def test_missing_katagrepo_entry(self, mock_file_reader):
            config_file = Path('NOT USED - MOCKED IN MOCK_FILE_READER')
            mock_file_reader.read_yaml.return_value = {}  # Missing 'KataGRepo' entry

            with pytest.raises(InvalidConfig) as error:
                config_repo = ConfigRepo(config_file, mock_file_reader)
                config_repo.get_kata_grepo_reponame()
            assert error.match("Missing config entry: 'KataGRepo'")

            with pytest.raises(InvalidConfig) as error:
                config_repo = ConfigRepo(config_file, mock_file_reader)
                config_repo.get_kata_grepo_username()
            assert error.match("Missing config entry: 'KataGRepo'")

        def test_missing_2nd_level_entries(self, mock_file_reader):
            config_file = Path('NOT USED - MOCKED IN MOCK_FILE_READER')

            with pytest.raises(InvalidConfig) as error:
                mock_file_reader.read_yaml.return_value = {'KataGRepo': {'User': 'NotUsed'}}  # Missing 'Repo'
                config_repo = ConfigRepo(config_file, mock_file_reader)
                config_repo.get_kata_grepo_reponame()
            assert error.match("Missing config entry: 'KataGRepo -> Repo'")

            with pytest.raises(InvalidConfig) as error:
                mock_file_reader.read_yaml.return_value = {'KataGRepo': {'Repo': 'NotUsed'}}  # Missing 'User'
                config_repo = ConfigRepo(config_file, mock_file_reader)
                config_repo.get_kata_grepo_username()
            assert error.match("Missing config entry: 'KataGRepo -> User'")

        def test_do_not_forget_to_implement_the_rest(self):
            pytest.skip("Skipping further validation tests for now."
                        "We'll implement all at once with schema validation")

    class TestIntegration:
        def test_valid_config(self, tmp_path: Path):
            def write_config(config_contents):
                with config_file.open('w') as f:
                    f.write(textwrap.dedent(config_contents))

            def create_config_repo():
                actual_file_reader = FileReader()
                return ConfigRepo(config_file, actual_file_reader)

            # Given: A valid config in a real file
            config_file = tmp_path / 'config.yml'
            write_config("""\
                KataGRepo:
                    User: frank
                    Repo: 'awesome-repo'
                    
                HasTemplateAtRoot:
                    java: False
                    elixir: True
            """)

            # When: Creating a repo with real dependencies
            config_repo = create_config_repo()

            # Then: Config is read as expected
            assert config_repo.get_kata_grepo_username() == 'frank'
            assert config_repo.get_kata_grepo_reponame() == 'awesome-repo'
            assert config_repo.has_template_at_root(KataLanguage('java')) is False
            assert config_repo.has_template_at_root(KataLanguage('elixir')) is True
            assert config_repo.has_template_at_root(KataLanguage('csharp')) is None
