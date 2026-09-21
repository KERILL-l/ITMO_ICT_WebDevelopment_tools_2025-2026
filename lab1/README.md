# Time Manager API — ЛР1

FastAPI-приложение для управления задачами и временем.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **PostgreSQL** — база данных
- **Alembic** — миграции
- **JWT (jose)** — аутентификация
- **passlib[bcrypt]** — хэширование паролей

## Установка и запуск

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env файл
cp .env.example .env
# Отредактировать DATABASE_URL и SECRET_KEY

# 3. Применить миграции
alembic upgrade head

# 4. Запустить сервер
uvicorn app.main:app --reload
```

Документация API: http://localhost:8000/docs

## Структура проекта

```
app/
├── main.py          — точка входа
├── config.py        — конфигурация
├── database.py      — подключение к БД
├── models/          — SQLAlchemy модели
├── schemas/         — Pydantic схемы
├── crud/            — CRUD операции
├── routers/         — API эндпоинты
└── auth/            — JWT и хэширование
alembic/             — миграции
```

## Модели данных

| Таблица       | Описание                              |
|---------------|---------------------------------------|
| users         | Пользователи системы                  |
| categories    | Категории задач (one-to-many с tasks) |
| tags          | Теги (many-to-many с tasks)           |
| tasks         | Задачи с приоритетом и дедлайном      |
| task_tags     | Связь задача↔тег с полем note         |
| time_entries  | Записи затраченного времени           |
