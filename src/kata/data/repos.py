import re
from typing import List, Optional

from kata import config
from kata.data.io.network import GithubApi
from kata.domain.models import KataTemplate, KataLanguage


class KataTemplateRepo:
    def __init__(self, api: GithubApi):
        self._api = api

    def get_for_language(self, language: KataLanguage) -> List[KataTemplate]:
        contents_of_language_root_dir = self._api.contents(config.KATA_GITHUB_REPO_USER,
                                                           config.KATA_GITHUB_REPO_REPO,
                                                           language.name)

        if self._has_template_at_root(language, contents_of_language_root_dir):
            template_at_root = KataTemplate(language=language, template_name=None)
            return [template_at_root]

        available_template_names = self._extract_available_template_names(contents_of_language_root_dir)

        def all_kata_templates_for_language():
            for template_name in available_template_names:
                yield KataTemplate(language, template_name)

        return list(all_kata_templates_for_language())

    @staticmethod
    def _has_template_at_root(language, dir_contents):
        def has_readme():
            for file_or_dir in dir_contents:
                if re.match(r'^.*README(\....?)?$', file_or_dir['path']):
                    return True
            return False

        if language.name in config.has_template_at_root:
            return config.has_template_at_root[language.name]
        else:
            return has_readme()

    @staticmethod
    def _extract_available_template_names(language_root_dir_contents):
        def extract_template_name_from_sub_path(sub_path: str):
            return sub_path.split('/')[1]

        return [extract_template_name_from_sub_path(directory['path']) for directory in language_root_dir_contents if
                directory['type'] == 'dir']


class KataLanguageRepo:
    def __init__(self, api: GithubApi):
        self._api = api

    def get_all(self) -> List[KataLanguage]:
        contents_of_root_dir = self._api.contents(config.KATA_GITHUB_REPO_USER,
                                                  config.KATA_GITHUB_REPO_REPO,
                                                  '')

        return list(self._all_sub_directories_mapped_to_languages(contents_of_root_dir))

    @staticmethod
    def _all_sub_directories_mapped_to_languages(contents_of_dir):
        for file_or_dir in contents_of_dir:
            if file_or_dir['type'] == 'dir':
                sub_dir_name_interpreted_as_available_kata_language_name = file_or_dir['path']
                yield KataLanguage(name=sub_dir_name_interpreted_as_available_kata_language_name)

    def get(self, language_name: str) -> Optional[KataLanguage]:
        all_languages = self.get_all()
        for language in all_languages:
            if language.name == language_name:
                return language


class HardCoded:
    class KataTemplateRepo(KataTemplateRepo):
        def __init__(self):
            super().__init__(None)
            self.available_templates = {
                'java': [
                    'junit5',
                    'some-other'
                ],
                'js': [
                    'jasminesomething',
                    'maybe-mocha'
                ]
            }

        def get_for_language(self, language: KataLanguage) -> List[KataTemplate]:
            def all_for_language_or_empty():
                for template_name in self.available_templates.get(language.name, []):
                    yield KataTemplate(language, template_name)

            return list(all_for_language_or_empty())

    class KataLanguageRepo(KataLanguageRepo):
        def __init__(self):
            super().__init__(None)
            self.available_languages: List[str] = []

        def get_all(self) -> List[KataLanguage]:
            return [KataLanguage(lang_name) for lang_name in self.available_languages]

        def get(self, language_name: str) -> Optional[KataLanguage]:
            for available_language_name in self.available_languages:
                if available_language_name == language_name:
                    return KataLanguage(language_name)
            if language_name not in self.available_languages:
                return None
