"""Подключение к базе данных (SQLAlchemy).

Адрес БД берётся из переменной окружения DATABASE_URL:
  * по умолчанию - файл SQLite (удобно для запуска без Docker);
  * в docker-compose - PostgreSQL.
"""
import os
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

DEFAULT_URL = "sqlite:///./codegen.db"


def make_engine(url: str | None = None) -> Engine:
    final_url: str = url or os.getenv("DATABASE_URL") or DEFAULT_URL
    if final_url.startswith("sqlite"):
        kwargs: dict[str, Any] = {"connect_args": {"check_same_thread": False}}
        if final_url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool  # одна общая БД в памяти (для тестов)
        return create_engine(final_url, **kwargs)
    return create_engine(final_url, pool_pre_ping=True)
