# План разработки: Бот техподдержки Finbox для Max мессенджера

## Стек технологий

| Компонент | Технология |
|---|---|
| Бот | Python 3.11+ / `maxapi` (polling) |
| БД | SQLite + SQLAlchemy ORM + Alembic |
| Веб-админка бэкенд | FastAPI + JWT auth |
| Веб-админка фронтенд | React + Vite + Ant Design |
| Google Sheets | `gspread` + `google-auth` |
| Файловое хранилище | Локальная директория (Docker volume) |
| Деплой | Docker Compose (3 контейнера) |

---

## Структура проекта

```
Max_bot/
├── docker-compose.yml
├── .env                          # Токены, секреты
├── .env.example                  # Шаблон
│
├── bot/                          # --- КОНТЕЙНЕР 1: БОТ ---
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                   # Точка входа (polling)
│   ├── config.py                 # Загрузка ENV переменных
│   ├── db/
│   │   ├── models.py             # SQLAlchemy модели
│   │   ├── database.py           # Подключение к SQLite
│   │   └── crud.py               # CRUD операции
│   ├── handlers/
│   │   ├── __init__.py           # Регистрация всех роутеров
│   │   ├── auth.py               # /start, регистрация, авторизация
│   │   ├── menu.py               # Главное меню (8 кнопок)
│   │   ├── pamyatki.py           # Памятки и инструкции (многоуровневое)
│   │   ├── tt.py                 # Подключение онлайн ТТ
│   │   ├── education.py          # Обучение + форма записи → Sheets
│   │   ├── ads.py                # Рекламные материалы
│   │   ├── partners.py           # Работа с партнёрами
│   │   ├── technology.py         # Наши технологии
│   │   ├── feedback.py           # "Нет информации" + "Идея"
│   │   └── request.py            # /request (заглушка)
│   ├── keyboards/
│   │   └── inline.py             # Фабрика inline-клавиатур
│   ├── states/
│   │   └── forms.py              # FSM-состояния для форм
│   └── services/
│       ├── sheets.py             # Google Sheets (gspread)
│       └── file_manager.py       # Отправка файлов из uploads/
│
├── api/                          # --- КОНТЕЙНЕР 2: FASTAPI ---
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                   # FastAPI app + CORS
│   ├── config.py
│   ├── auth.py                   # JWT авторизация админов
│   ├── deps.py                   # Зависимости (get_db, get_current_admin)
│   └── routers/
│       ├── auth_router.py        # POST /login, POST /register
│       ├── users.py              # GET/PATCH пользователи бота
│       ├── documents.py          # CRUD документы + upload файлов
│       ├── categories.py         # CRUD дерево разделов
│       └── stats.py              # GET статистика
│
├── frontend/                     # --- КОНТЕЙНЕР 3: REACT ---
│   ├── Dockerfile
│   ├── nginx.conf                # Проксирование /api → FastAPI
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx               # Роутинг
│       ├── api/
│       │   └── client.ts         # Axios + JWT interceptor
│       ├── pages/
│       │   ├── LoginPage.tsx     # Логин админа
│       │   ├── DashboardPage.tsx # Статистика
│       │   ├── UsersPage.tsx     # Таблица пользователей
│       │   ├── DocumentsPage.tsx # Файл-менеджер
│       │   └── CategoriesPage.tsx# Дерево разделов
│       └── components/
│           ├── Layout.tsx        # Sidebar + header
│           ├── UserTable.tsx     # Таблица с фильтрами
│           ├── FileUpload.tsx    # Drag-and-drop загрузка
│           └── CategoryTree.tsx  # Дерево категорий
│
├── data/                         # --- VOLUMES ---
│   ├── db/                       # SQLite файл
│   └── uploads/                  # Загруженные PDF/DOCX/MP4
│
└── alembic/                      # Миграции БД
    ├── alembic.ini
    └── versions/
```

---

## Модели базы данных

### User (пользователи бота)
```
id              INTEGER PRIMARY KEY
max_user_id     TEXT UNIQUE NOT NULL    -- ID пользователя в Max
username        TEXT                     -- username в Max
full_name       TEXT                     -- ФИО из формы регистрации
phone           TEXT                     -- Телефон из request_contact
status          TEXT DEFAULT 'pending'   -- pending / approved / blocked
created_at      DATETIME
updated_at      DATETIME
```

### Category (разделы меню — дерево)
```
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL            -- Название раздела
slug            TEXT UNIQUE              -- callback_data идентификатор
parent_id       INTEGER REFERENCES category(id)
sort_order      INTEGER DEFAULT 0
icon            TEXT                     -- Эмодзи для кнопки
is_active       BOOLEAN DEFAULT TRUE
```

### Document (файлы/материалы)
```
id              INTEGER PRIMARY KEY
title           TEXT NOT NULL            -- Отображаемое название
file_path       TEXT NOT NULL            -- Путь в uploads/
file_type       TEXT                     -- pdf / docx / pptx / mp4 / png / jpg
max_file_id     TEXT                     -- Кэш file_id после первой отправки
category_id     INTEGER REFERENCES category(id)
sort_order      INTEGER DEFAULT 0
is_active       BOOLEAN DEFAULT TRUE
created_at      DATETIME
```

### ExternalLink (внешние ссылки — Google Drive, сайты)
```
id              INTEGER PRIMARY KEY
title           TEXT NOT NULL
url             TEXT NOT NULL
category_id     INTEGER REFERENCES category(id)
sort_order      INTEGER DEFAULT 0
```

### TrainingRequest (записи на обучение)
```
id              INTEGER PRIMARY KEY
user_id         INTEGER REFERENCES user(id)
partner_name    TEXT
surname         TEXT
phone           TEXT
topic           TEXT
date            TEXT
time            TEXT
created_at      DATETIME
synced_to_sheets BOOLEAN DEFAULT FALSE
```

### FeedbackQuestion (вопросы "Нет информации")
```
id              INTEGER PRIMARY KEY
user_id         INTEGER REFERENCES user(id)
question        TEXT
created_at      DATETIME
is_resolved     BOOLEAN DEFAULT FALSE
```

### AdminUser (админы веб-панели)
```
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL
created_at      DATETIME
```

---

## Этапы реализации

### Этап 1: Инфраструктура (Docker + БД)
1. Создать `docker-compose.yml` с 3 сервисами:
   - `bot` — Python, volume: `./data:/app/data`
   - `api` — FastAPI, volume: `./data:/app/data`
   - `frontend` — nginx + React build, проксирование `/api`
2. Настроить SQLAlchemy + создать все модели
3. Настроить Alembic, создать начальную миграцию
4. Написать `config.py` — загрузка из `.env`
5. Создать `.env.example` с описанием переменных:
   - `MAX_BOT_TOKEN` — токен бота Max
   - `ADMIN_SECRET_KEY` — JWT secret
   - `GOOGLE_SHEETS_CREDENTIALS` — путь к JSON ключу
   - `GOOGLE_SHEETS_SPREADSHEET_ID` — ID таблицы

### Этап 2: Бот — авторизация и главное меню
6. Инициализация `maxapi.Bot` + `Dispatcher` в polling-режиме
7. Обработчик `/start`:
   - Проверка `User` в БД по `max_user_id`
   - Новый → запуск формы регистрации (ФИО → контакт)
   - `pending` → "Данные приняты, ждите"
   - `approved` → приветствие + кнопка "Меню"
8. Форма регистрации через FSM (конечный автомат):
   - Состояние 1: ввод ФИО
   - Состояние 2: отправка контакта (RequestContactButton)
   - Сохранение в БД со статусом `pending`
9. Главное меню `/menu`:
   - Отправка картинки (меню для бота.png) + inline-клавиатура 8 кнопок
   - Динамическая генерация кнопок из таблицы Category (корневые элементы)

### Этап 3: Бот — контент-разделы
10. **Универсальный обработчик разделов**:
    - По `callback_data` (slug категории) → запрос подкатегорий из БД
    - Если есть подкатегории → показать кнопки подменю
    - Если есть документы → отправить файлы
    - Если есть ссылки → отправить кнопки-ссылки
    - Кнопки «Назад» и «Меню» на каждом экране
11. **Памятки и инструкции**: заполнить дерево категорий (8 подразделов → вложенные)
12. **Онлайн ТТ**: 4 подраздела (видео, PDF, интеграция, чек-листы)
13. **Обучение**: ссылка на Google Sheets + форма записи (6 шагов FSM → запись в Sheets)
14. **Реклама, Партнёры, Технологии**: аналогичная структура
15. **Нет информации**: форма сбора вопроса (FSM → сохранение в БД)
16. **Идея**: текст + ссылка на контакт
17. **/request (заглушка)**: фиктивные данные, как в оригинале

### Этап 4: Google Sheets интеграция
18. `gspread` + Service Account JSON
19. Запись строки в Google Sheets при заполнении формы обучения
20. Формат: Партнёр, Фамилия, Телефон, Тема, Дата, Время

### Этап 5: FastAPI — бэкенд админки
21. JWT авторизация:
    - `POST /api/auth/login` → возврат access_token
    - Middleware проверки токена
22. Пользователи бота:
    - `GET /api/users` — список с пагинацией, фильтр по статусу
    - `PATCH /api/users/{id}` — смена статуса (approve / block)
    - `GET /api/users/{id}` — детальная информация
23. Документы:
    - `GET /api/documents` — список, фильтр по категории
    - `POST /api/documents` — загрузка файла + метаданные
    - `DELETE /api/documents/{id}` — удаление
    - `PATCH /api/documents/{id}` — редактирование метаданных
24. Категории (дерево разделов):
    - `GET /api/categories` — дерево целиком
    - `POST /api/categories` — создание
    - `PATCH /api/categories/{id}` — редактирование
    - `DELETE /api/categories/{id}` — удаление (если нет дочерних)
25. Статистика:
    - `GET /api/stats` — общие цифры (пользователи, документы, заявки)

### Этап 6: React — фронтенд админки
26. Настроить Vite + React + TypeScript + Ant Design
27. **LoginPage** — форма логина → JWT в localStorage
28. **DashboardPage** — карточки со статистикой (Ant Design Statistic)
29. **UsersPage** — таблица Ant Design Table:
    - Колонки: ФИО, телефон, статус, дата регистрации
    - Фильтры по статусу (pending / approved / blocked)
    - Кнопки действий: Одобрить / Заблокировать
30. **DocumentsPage**:
    - Список документов с группировкой по разделам
    - Drag-and-drop загрузка (Ant Design Upload)
    - Выбор категории при загрузке
    - Удаление документов
31. **CategoriesPage**:
    - Ant Design Tree с drag-and-drop для пересортировки
    - Создание / редактирование / удаление узлов
32. **Layout** — боковое меню с навигацией

### Этап 7: Docker финализация и запуск
33. Dockerfile для бота:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    CMD ["python", "main.py"]
    ```
34. Dockerfile для API:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
35. Dockerfile для фронтенда:
    ```dockerfile
    FROM node:20-alpine AS build
    WORKDIR /app
    COPY package*.json .
    RUN npm ci
    COPY . .
    RUN npm run build

    FROM nginx:alpine
    COPY --from=build /app/dist /usr/share/nginx/html
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    ```
36. `docker-compose.yml`:
    ```yaml
    services:
      bot:
        build: ./bot
        env_file: .env
        volumes:
          - ./data:/app/data
        restart: unless-stopped

      api:
        build: ./api
        env_file: .env
        volumes:
          - ./data:/app/data
        ports:
          - "8000:8000"
        restart: unless-stopped

      frontend:
        build: ./frontend
        ports:
          - "3000:80"
        depends_on:
          - api
        restart: unless-stopped
    ```

---

## Начальное заполнение данных

При первом запуске необходимо:
1. Создать админа через CLI-команду: `python -m api.create_admin`
2. Загрузить структуру разделов через seed-скрипт или через админку
3. Загрузить документы (PDF, DOCX, PPTX, MP4) через веб-админку
4. Настроить Google Sheets credentials

---

## Ключевые отличия от Telegram-версии

| Аспект | Telegram (оригинал) | Max (новая версия) |
|---|---|---|
| Библиотека | python-telegram-bot | maxapi |
| Регистрация бота | @BotFather | dev.max.ru |
| API домен | api.telegram.org | platform-api.max.ru |
| Файлы | file_id Telegram | Загрузка через POST /uploads |
| Кнопки | InlineKeyboardButton | CallbackButton, LinkButton и др. |
| Контакт | KeyboardButton(request_contact) | RequestContactButton |
| Хранение данных | Puzzle Bot (no-code) | SQLite + файловая система |
| Управление контентом | Захардкожено | Веб-админка с CRUD |

---

## Запуск

```bash
# 1. Скопировать и заполнить переменные
cp .env.example .env

# 2. Запустить всё
docker-compose up -d --build

# 3. Создать админа
docker-compose exec api python create_admin.py

# 4. Открыть админку
# http://localhost:3000

# 5. Загрузить документы и настроить разделы через админку
```
