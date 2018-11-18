from unittest import mock
from unittest.mock import MagicMock

import pytest

from kata import config
from kata.data.repos import KataTemplateRepo, KataLanguageRepo
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
