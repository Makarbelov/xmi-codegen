"""Модели данных (ER-диаграмма из ЛР№1: Profile 1 : N Template).

Методы get_settings() и get_content() - это те самые вызовы,
которые CodeGenerator делает на диаграмме последовательности (ЛР№2).
"""
from typing import Any

from sqlalchemy import ForeignKey, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from app.exceptions import TemplateNotFoundError


class Base(DeclarativeBase):
    pass


class Profile(Base):
    """Профиль - настройки оформления кода (язык, отступы, стиль имён)."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(20), default="python")
    indent: Mapped[int] = mapped_column(default=4)
    naming: Mapped[str] = mapped_column(String(20), default="snake_case")

    templates: Mapped[list["Template"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )

    @classmethod
    def get_settings(cls, db: Session, template_id: int) -> dict[str, Any]:
        """Настройки профиля, к которому относится выбранный шаблон."""
        profile = db.execute(
            select(cls).join(Template, Template.profile_id == cls.id).where(Template.id == template_id)
        ).scalar_one_or_none()
        if profile is None:
            raise TemplateNotFoundError(template_id)
        return {"language": profile.language, "indent": profile.indent, "naming": profile.naming}


class Template(Base):
    """Шаблон - заготовка кода, в которую подставляются классы из модели."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))

    profile: Mapped[Profile] = relationship(back_populates="templates")

    @classmethod
    def get_content(cls, db: Session, template_id: int) -> str:
        """Текст выбранного шаблона."""
        template = db.get(cls, template_id)
        if template is None:
            raise TemplateNotFoundError(template_id)
        return template.content
