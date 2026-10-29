# Генератор кода по UML-классам (учебный модуль)

Загружаете XMI-файл с UML-классами, выбираете шаблон - получаете Python-код.

## Запуск без Docker (самый простой)
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows;  на Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```
Откройте http://localhost:8000/docs - там можно нажимать кнопки и пробовать запросы.
Файл для проверки: `examples/sample.xmi`.

## Запуск в Docker (приложение + PostgreSQL)
```bash
docker compose up --build
```
* Приложение и документация: http://localhost:8000/docs

## Проверки
```bash
ruff check .            # линтер
mypy app                # типы
pytest --cov=app        # тесты
```
## ЛИТКОД АЛГОРИТМЫ GOLANG ВОЛК
