class KataError(Exception):
    pass


class InvalidKataName(KataError):
    def __init__(self, kata_name: str, reason=None):
        super().__init__(f"Kata name '{kata_name}' is invalid!")
        self.kata_name = kata_name
        self.reason = reason


class KataTemplateLanguageNotFound(KataError):
    pass


class KataTemplateTemplateNameNotFound(KataError):
    pass
