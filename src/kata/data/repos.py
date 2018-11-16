from typing import List

from kata.domain.models import KataTemplate


class KataTemplateRepo:
    """
    For now this is hard-coded.
    """

    def __init__(self):
        self.fake_template_repo = {
            'java': [
                'junit5',
                'some-other'
            ],
            'js': [
                'jasminesomething',
                'maybe-mocha'
            ]
        }

    def get_all(self) -> List[KataTemplate]:
        def all_templates():
            for language in self.fake_template_repo:
                for template_name in self.fake_template_repo[language]:
                    yield KataTemplate(language, template_name)

        return list(all_templates())

    def get_for_language(self, language: str) -> List[KataTemplate]:
        def all_for_language_or_empty():
            for template_name in self.fake_template_repo.get(language, []):
                yield KataTemplate(language, template_name)

        return list(all_for_language_or_empty())
