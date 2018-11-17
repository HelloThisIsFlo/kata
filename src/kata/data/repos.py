import re
from typing import List

from kata import config
from kata.data.io.network import GithubApi
from kata.domain.models import KataTemplate


class KataTemplateRepo:
    def __init__(self, api: GithubApi):
        self._api = api

    def get_for_language(self, language: str) -> List[KataTemplate]:
        contents_of_language_root_dir = self._api.contents(config.KATA_GITHUB_REPO_USER,
                                                           config.KATA_GITHUB_REPO_REPO,
                                                           language)

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

        if language in config.has_template_at_root:
            return config.has_template_at_root[language]
        else:
            return has_readme()

    @staticmethod
    def _extract_available_template_names(language_root_dir_contents):
        def extract_template_name_from_sub_path(sub_path: str):
            return sub_path.split('/')[1]

        return [extract_template_name_from_sub_path(directory['path']) for directory in language_root_dir_contents if
                directory['type'] == 'dir']


class HardCodedKataTemplateRepo(KataTemplateRepo):
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

    def get_for_language(self, language: str) -> List[KataTemplate]:
        def all_for_language_or_empty():
            for template_name in self.available_templates.get(language, []):
                yield KataTemplate(language, template_name)

        return list(all_for_language_or_empty())
