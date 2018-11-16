import re
from pathlib import Path
from typing import Optional

from kata import config
from kata.data.repos import KataTemplateRepo
from kata.domain.exceptions import InvalidKataName, KataTemplateLanguageNotFound, KataTemplateTemplateNameNotFound
from kata.domain.grepo import GRepo


class InitKataService:
    def __init__(self, kata_template_repo: KataTemplateRepo, grepo: GRepo):
        self._kata_template_repo = kata_template_repo
        self._grepo = grepo

    def init_kata(self, parent_dir: Path, kata_name: str, template_language: str, template_name: Optional[str]) -> None:
        self.validate_parent_dir(parent_dir)
        self.validate_kata_name(kata_name)

        kata_template = self.get_kata_template(template_language, template_name)

        path = f'{kata_template.language}/{kata_template.template_name}'
        files_to_download = self._grepo.get_files_to_download(user=config.KATA_GITHUB_REPO_USER,
                                                              repo=config.KATA_GITHUB_REPO_REPO,
                                                              path=path)
        kata_dir = parent_dir / kata_name
        self._grepo.download_files_at_location(kata_dir, files_to_download)

    @staticmethod
    def validate_parent_dir(parent_dir):
        if not parent_dir.exists():
            raise FileNotFoundError(f"Invalid Directory: '{parent_dir.absolute()}'")

    @staticmethod
    def validate_kata_name(kata_name):
        def has_spaces():
            return len(kata_name.split(' ')) > 1

        if not kata_name:
            raise InvalidKataName(kata_name, reason='empty')
        if has_spaces():
            raise InvalidKataName(kata_name, reason='contains spaces')

        if not re.match(r'^[_a-z]*$', kata_name):
            raise InvalidKataName(kata_name)

    def get_kata_template(self, template_language: str, template_name: str):

        def none_available_for_language():
            return not templates_for_language

        def only_one_available_for_language():
            return len(templates_for_language) == 1

        def first():
            return templates_for_language[0]

        def first_found_or_raise(exception):
            for template in templates_for_language:
                if template.template_name == template_name:
                    return template
            raise exception()

        templates_for_language = self._kata_template_repo.get_for_language(template_language)
        if none_available_for_language():
            raise KataTemplateLanguageNotFound()
        if only_one_available_for_language():
            return first()
        else:
            return first_found_or_raise(KataTemplateTemplateNameNotFound)
