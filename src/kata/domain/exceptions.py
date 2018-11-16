from .models import KataTemplate


class KataError(Exception):
    pass


class KataTemplateError(KataError):
    def __init__(self, kata_template: KataTemplate):
        self.kata_template = kata_template


class KataTemplateLanguageNotFound(KataTemplateError):
    pass


class KataTemplateTemplateNameNotFound(KataTemplateError):
    pass
