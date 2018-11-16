from typing import List

from kata.domain.models import KataTemplate


class KataTemplateRepo:
    def get_all(self) -> List[KataTemplate]:
        raise NotImplementedError()

    def get_for_language(self, language: str) -> List[KataTemplate]:
        raise NotImplementedError()


class HardCodedKataTemplateRepo(KataTemplateRepo):
    def __init__(self):
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

    def get_all(self) -> List[KataTemplate]:
        def all_templates():
            for language in self.available_templates:
                for template_name in self.available_templates[language]:
                    yield KataTemplate(language, template_name)

        return list(all_templates())

    def get_for_language(self, language: str) -> List[KataTemplate]:
        def all_for_language_or_empty():
            for template_name in self.available_templates.get(language, []):
                yield KataTemplate(language, template_name)

        return list(all_for_language_or_empty())
