from unittest import mock
from unittest.mock import MagicMock

import pytest

from kata import config
from kata.data.repos import KataTemplateRepo
from kata.domain.models import KataTemplate


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


class TestKataTemplateRepo:
    @pytest.fixture
    @mock.patch('src.kata.data.io.network.GithubApi')
    def mock_api(self, mocked_api):
        return mocked_api

    @pytest.fixture
    def kata_template_repo(self, mock_api):
        return KataTemplateRepo(mock_api)

    class TestGetForLanguage:
        def test_request_contents_of_language_directory(self,
                                                        mock_api: MagicMock,
                                                        kata_template_repo: KataTemplateRepo):
            kata_template_repo.get_for_language('javascript')
            mock_api.contents.assert_called_with(config.KATA_GITHUB_REPO_USER, config.KATA_GITHUB_REPO_REPO,
                                                 'javascript')

        def test_template_is_at_root(self,
                                     mock_api: MagicMock,
                                     kata_template_repo: KataTemplateRepo):
            # Template is at root if there's a README.md at root of the language dir
            # Given: There's a 'README.md' at java dir root
            mock_api.contents.return_value = [mock_file_entry('java/README.md')]

            # When: Fetching the available templates for java
            available_java_templates = kata_template_repo.get_for_language('java')

            # Then: Only one is available and it is the root template (template_name == None)
            assert len(available_java_templates) == 1
            assert available_java_templates[0] == KataTemplate(language='java', template_name=None)

        def test_template_is_not_at_root(self,
                                         mock_api: MagicMock,
                                         kata_template_repo: KataTemplateRepo):
            # Given: There are multiple directories at root of the language dir
            mock_api.contents.return_value = [mock_dir_entry('java/junit5'),
                                              mock_dir_entry('java/hamcrest')]

            # When: Fetching the available templates for java
            available_java_templates = kata_template_repo.get_for_language('java')

            # Then: All available templates are returned
            assert available_java_templates == [KataTemplate('java', 'junit5'),
                                                KataTemplate('java', 'hamcrest')]
