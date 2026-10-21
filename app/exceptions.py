"""Собственные исключения модуля."""


class XmiParseError(ValueError):
    """XMI-файл нельзя прочитать или в нём нет UML-классов."""


class TemplateNotFoundError(LookupError):
    """Шаблон с указанным идентификатором не найден."""

    def __init__(self, template_id: int) -> None:
        super().__init__(f"Шаблон с id={template_id} не найден")
        self.template_id = template_id
