"""Точка входа: сборка FastAPI-приложения."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker

from app.api import register_error_handlers, router
from app.database import make_engine
from app.models import Base
from app.seed import seed_defaults


def create_app(database_url: str | None = None) -> FastAPI:
    engine = make_engine(database_url)
    session_factory = sessionmaker(bind=engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(engine)
        with session_factory() as db:
            seed_defaults(db)
        yield

    app = FastAPI(title="Генератор кода по UML-классам", version="1.0.0", lifespan=lifespan)
    app.state.session_factory = session_factory
    register_error_handlers(app)
    app.include_router(router)
    return app


app = create_app()
