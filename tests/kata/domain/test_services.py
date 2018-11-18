from pathlib import Path
from typing import Union
from unittest import mock
from unittest.mock import MagicMock

import pytest

from kata import config
from kata.data.repos import HardCoded
from kata.domain.exceptions import InvalidKataName, KataLanguageNotFound, KataTemplateTemplateNameNotFound
from kata.domain.grepo import GRepo
from kata.domain.models import DownloadableFile, KataLanguage, KataTemplate
from kata.domain.services import InitKataService

NOT_USED = 'Not Used'
VALID_KATA_NAME = 'kata_name'

MOCK_FILES_TO_DOWNLOAD = [DownloadableFile(Path('fake.txt'), 'http://hello.com/fake.txt'),
                          DownloadableFile(Path('hey/fake.txt'), 'http://hello.com/hey/fake.txt'),
                          DownloadableFile(Path('hey/fake.md'), 'http://hello.com/hey/fake.md')]


class TestInitKataService:

    @pytest.fixture
    @mock.patch('src.kata.domain.grepo.GRepo')
    def mock_grepo(self, mocked_grepo: Union[GRepo, MagicMock], ):
        mocked_grepo.get_files_to_download.return_value = MOCK_FILES_TO_DOWNLOAD
        return mocked_grepo

    @pytest.fixture
    def kata_template_repo(self):
        return HardCoded.KataTemplateRepo()

    @pytest.fixture
    def kata_language_repo(self):
        return HardCoded.KataLanguageRepo()

    @pytest.fixture
    def init_kata_service(self, kata_language_repo, kata_template_repo, mock_grepo):
        return InitKataService(kata_language_repo, kata_template_repo, mock_grepo)

    class TestValidCases:
        def test_with_valid_template(self,
                                     tmp_path: Path,
                                     kata_language_repo: HardCoded.KataLanguageRepo,
                                     kata_template_repo: HardCoded.KataTemplateRepo,
                                     mock_grepo: MagicMock,
                                     init_kata_service: InitKataService):
            # Given: Template is available and parent_dir is valid
            kata_language_repo.available_languages = ['java']
            kata_template_repo.available_templates = {'java': ['junit5', 'hamcrest']}
            kata_name = 'my_kata'
            template_lang = 'java'
            template_name = 'junit5'
            parent_dir = tmp_path

            # When: Initializing the Kata
            init_kata_service.init_kata(parent_dir, kata_name, template_lang, template_name)

            # Then:
            # - File URLs have been been fetched with the correct Username/GithubRepo/Subpath
            mock_grepo.get_files_to_download.assert_called_with(
                user=config.KATA_GITHUB_REPO_USER,
                repo=config.KATA_GITHUB_REPO_REPO,
                path='java/junit5')
            # - Files are requested to be downloaded in parent_dir/kata_name
            #   Note: MOCK_FILES_TO_DOWNLOAD are set in the mock_grepo fixture initialization
            mock_grepo.download_files_at_location.assert_called_with(parent_dir / kata_name,
                                                                     MOCK_FILES_TO_DOWNLOAD)

        class TestNoExplicitTemplateNameBut:
            def test_only_one_template_available_for_language(self,
                                                              tmp_path: Path,
                                                              kata_language_repo: HardCoded.KataLanguageRepo,
                                                              kata_template_repo: HardCoded.KataTemplateRepo,
                                                              mock_grepo: MagicMock,
                                                              init_kata_service: InitKataService):
                # Given: Template name not specified but only one available
                kata_language_repo.available_languages = ['java']
                kata_template_repo.available_templates = {'java': ['junit5']}
                kata_name = 'my_kata'
                template_lang = 'java'
                template_name = None

                # When: Initializing the Kata
                init_kata_service.init_kata(tmp_path, kata_name, template_lang, template_name)

                # Then: File URLs have been been fetched with using the only available template name
                mock_grepo.get_files_to_download.assert_called_with(
                    user=config.KATA_GITHUB_REPO_USER,
                    repo=config.KATA_GITHUB_REPO_REPO,
                    path='java/junit5')

            def test_only_one_template_at_root(self,
                                               tmp_path: Path,
                                               kata_language_repo: HardCoded.KataLanguageRepo,
                                               kata_template_repo: HardCoded.KataTemplateRepo,
                                               mock_grepo: MagicMock,
                                               init_kata_service: InitKataService):
                # Given: Template name not specified but only one available at root (sub-path == None)
                kata_language_repo.available_languages = ['java']
                kata_template_repo.available_templates = {'java': [None]}
                kata_name = 'my_kata'
                template_lang = 'java'
                template_name = None

                # When: Initializing the Kata
                init_kata_service.init_kata(tmp_path, kata_name, template_lang, template_name)

                # Then: File URLs have been been fetched without any sub-path
                mock_grepo.get_files_to_download.assert_called_with(
                    user=config.KATA_GITHUB_REPO_USER,
                    repo=config.KATA_GITHUB_REPO_REPO,
                    path='java')

            def test_default_specified_and_valid(self):
                pytest.skip('TODO')

    class TestEdgeCases:
        def test_invalid_parent_dir(self, init_kata_service: InitKataService):
            with pytest.raises(FileNotFoundError) as expected_error:
                invalid_dir = Path('i_do_not_exist')
                init_kata_service.init_kata(invalid_dir,
                                            kata_name=NOT_USED,
                                            template_language=NOT_USED,
                                            template_name=NOT_USED)

            expected_error.match(r"Invalid Directory: '.*i_do_not_exist'")

        class TestInvalidKataName:
            def test_kata_name_empty(self, tmp_path: Path, init_kata_service: InitKataService):
                with pytest.raises(InvalidKataName):
                    empty_name = ''
                    init_kata_service.init_kata(tmp_path, empty_name, NOT_USED, NOT_USED)

            def test_kata_name_with_spaces(self, tmp_path: Path, init_kata_service: InitKataService):
                with pytest.raises(InvalidKataName):
                    name_with_spaces = 'this is a kata name with spaces'
                    init_kata_service.init_kata(tmp_path, name_with_spaces, NOT_USED, NOT_USED)

            def test_kata_name_with_special_char_besides_underscore(self, tmp_path: Path,
                                                                    init_kata_service: InitKataService):
                with pytest.raises(InvalidKataName):
                    name_with_special_chars = 'this/a/kata/name/with/special/char'
                    init_kata_service.init_kata(tmp_path, name_with_special_chars, NOT_USED, NOT_USED)

                with pytest.raises(InvalidKataName):
                    name_with_special_chars = 'special?char'
                    init_kata_service.init_kata(tmp_path, name_with_special_chars, NOT_USED, NOT_USED)

        class TestInvalidTemplate:
            def test_language_doesnt_exist(self,
                                           tmp_path: Path,
                                           init_kata_service: InitKataService,
                                           kata_language_repo: HardCoded.KataLanguageRepo,
                                           kata_template_repo: HardCoded.KataTemplateRepo):
                with pytest.raises(KataLanguageNotFound) as language_not_found_error:
                    kata_language_repo.available_languages = ['java']
                    kata_template_repo.available_templates = {'java': ['junit5', 'hamcrest']}
                    init_kata_service.init_kata(tmp_path, VALID_KATA_NAME, 'python', NOT_USED)

                assert language_not_found_error.value.available_languages == [KataLanguage('java')]

            def test_template_name_doesnt_exist(self,
                                                tmp_path: Path,
                                                init_kata_service: InitKataService,
                                                kata_language_repo: HardCoded.KataLanguageRepo,
                                                kata_template_repo: HardCoded.KataTemplateRepo):
                with pytest.raises(KataTemplateTemplateNameNotFound) as template_not_found_error:
                    kata_language_repo.available_languages = ['java']
                    kata_template_repo.available_templates = {'java': ['junit5', 'hamcrest']}
                    init_kata_service.init_kata(tmp_path, VALID_KATA_NAME, 'java', 'some_framework_thats_not_junit5')

                assert template_not_found_error.value.available_templates == \
                       [KataTemplate(KataLanguage('java'), 'junit5'),
                        KataTemplate(KataLanguage('java'), 'hamcrest')]
