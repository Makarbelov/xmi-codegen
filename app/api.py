"""REST-интерфейс: профили, шаблоны, генерация кода."""
import os
import tempfile
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.code_generator import CodeGenerator
from app.exceptions import TemplateNotFoundError, XmiParseError
from app.models import Profile, Template
from app.schemas import (
    GenerateResponse,
    ProfileRead,
    TemplateCreate,
    TemplateRead,
)


def get_db(request: Request) -> Iterator[Session]:
    db: Session = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
router = APIRouter()


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(TemplateNotFoundError)
    async def _not_found(_: Request, exc: TemplateNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(XmiParseError)
    async def _bad_xmi(_: Request, exc: XmiParseError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})


# ---------- Профили (только чтение: набор готовый) ----------
@router.get("/profiles", response_model=list[ProfileRead], tags=["Профили"])
def list_profiles(db: DbSession) -> list[Profile]:
    return list(db.scalars(select(Profile).order_by(Profile.id)))


def _get_profile(db: Session, profile_id: int) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Профиль с id={profile_id} не найден")
    return profile


# ---------- Шаблоны ----------
def _get_template(db: Session, template_id: int) -> Template:
    template = db.get(Template, template_id)
    if template is None:
        raise TemplateNotFoundError(template_id)
    return template


@router.post("/templates", response_model=TemplateRead, status_code=201, tags=["Шаблоны"])
def create_template(data: TemplateCreate, db: DbSession) -> Template:
    _get_profile(db, data.profile_id)  # 404, если профиля нет
    template = Template(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=list[TemplateRead], tags=["Шаблоны"])
def list_templates(db: DbSession, profile_id: int | None = None) -> list[Template]:
    query = select(Template).order_by(Template.id)
    if profile_id is not None:
        query = query.where(Template.profile_id == profile_id)
    return list(db.scalars(query))


@router.get("/templates/{template_id}", response_model=TemplateRead, tags=["Шаблоны"])
def read_template(template_id: int, db: DbSession) -> Template:
    return _get_template(db, template_id)


@router.put("/templates/{template_id}", response_model=TemplateRead, tags=["Шаблоны"])
def update_template(template_id: int, data: TemplateCreate, db: DbSession) -> Template:
    template = _get_template(db, template_id)
    _get_profile(db, data.profile_id)
    for key, value in data.model_dump().items():
        setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}", status_code=204, tags=["Шаблоны"])
def delete_template(template_id: int, db: DbSession) -> None:
    db.delete(_get_template(db, template_id))
    db.commit()


# ---------- Генерация ----------
@router.post("/generate", response_model=GenerateResponse, tags=["Генерация"])
def generate(
    db: DbSession,
    file: Annotated[UploadFile, File(description="XMI-файл с UML-классами")],
    template_id: Annotated[int, Form(ge=1, description="Выбранный шаблон")],
) -> GenerateResponse:
    """Главный сценарий: загрузить XMI-файл, выбрать шаблон, получить Python-код."""
    with tempfile.NamedTemporaryFile(suffix=".xmi", delete=False) as tmp:
        tmp.write(file.file.read())
        path = tmp.name
    try:
        code = CodeGenerator().generate(db, path, template_id)
    finally:
        os.unlink(path)
    return GenerateResponse(code=code)
