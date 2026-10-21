"""Схемы Pydantic: проверка входящих данных и формат ответов."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.code_generator import TemplateSyntaxError, check_template_syntax


def _not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Имя не может быть пустым")
    return value


class ProfileBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Python (PEP 8)"])
    language: Literal["python"] = "python"
    indent: int = Field(default=4, ge=1, le=16, description="Число пробелов в отступе")
    naming: Literal["snake_case", "camel_case"] = "snake_case"

    _check_name = field_validator("name")(_not_blank)


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Простой класс"])
    content: str = Field(min_length=1, max_length=20000, description="Текст шаблона (Jinja2)")
    profile_id: int = Field(ge=1)

    _check_name = field_validator("name")(_not_blank)

    @field_validator("content")
    @classmethod
    def _check_syntax(cls, value: str) -> str:
        try:
            check_template_syntax(value)
        except TemplateSyntaxError as exc:
            raise ValueError(f"Ошибка в шаблоне: {exc.message}") from exc
        return value


class TemplateCreate(TemplateBase):
    pass


class TemplateRead(TemplateBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GenerateResponse(BaseModel):
    code: str
