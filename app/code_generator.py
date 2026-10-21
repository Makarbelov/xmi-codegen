"""Генерация кода (класс CodeGenerator из ЛР№2).

Порядок вызовов в generate() совпадает с диаграммой последовательности:
  2. XmiParser.parse(xmi_path)
  4. Template.get_content(template_id)
  6. Profile.get_settings(template_id)
"""
import re
from typing import Any

from jinja2 import StrictUndefined, TemplateSyntaxError
from jinja2.sandbox import SandboxedEnvironment
from sqlalchemy.orm import Session

from app.models import Profile, Template
from app.xmi_parser import XmiParser

HEADER = "from __future__ import annotations\n\n\n"

_env = SandboxedEnvironment(
    trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True, undefined=StrictUndefined
)


def check_template_syntax(content: str) -> None:
    """Бросает TemplateSyntaxError, если в шаблоне синтаксическая ошибка."""
    _env.from_string(content)


def _words(name: str) -> list[str]:
    name = re.sub(r"\W+", "_", name)
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [w for w in name.lower().split("_") if w]


def to_snake(name: str) -> str:
    return "_".join(_words(name))


def to_camel(name: str) -> str:
    words = _words(name)
    return words[0] + "".join(w.capitalize() for w in words[1:]) if words else name


def to_pascal(name: str) -> str:
    return "".join(w.capitalize() for w in _words(name))


def apply_naming(classes: list[dict[str, Any]], naming: str) -> list[dict[str, Any]]:
    """Имена классов - PascalCase, имена атрибутов и методов - по стилю профиля."""
    convert = to_camel if naming == "camel_case" else to_snake
    result: list[dict[str, Any]] = []
    for cls in classes:
        result.append(
            {
                "name": to_pascal(cls["name"]),
                "attributes": [{"name": convert(a["name"]), "type": a["type"]} for a in cls["attributes"]],
                "methods": [
                    {
                        "name": convert(m["name"]),
                        "params": [{"name": convert(p["name"]), "type": p["type"]} for p in m["params"]],
                        "return_type": m["return_type"],
                    }
                    for m in cls["methods"]
                ],
            }
        )
    return result


def render_code(classes: list[dict[str, Any]], content: str, settings: dict[str, Any]) -> str:
    template = _env.from_string(content)
    body = template.render(
        classes=apply_naming(classes, settings["naming"]), indent=" " * settings["indent"]
    )
    return HEADER + body.rstrip() + "\n"


class CodeGenerator:
    def generate(self, db: Session, xmi_path: str, template_id: int) -> str:
        """Главный сценарий: XMI-файл + выбранный шаблон -> Python-код.

        Параметр db - сессия БД (в диаграмме классов опущен для читаемости).
        """
        classes = XmiParser().parse(xmi_path)
        content = Template.get_content(db, template_id)
        settings = Profile.get_settings(db, template_id)
        return render_code(classes, content, settings)


__all__ = ["CodeGenerator", "TemplateSyntaxError", "check_template_syntax", "render_code"]
