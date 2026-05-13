# Auth Service

Backend система аутентификации и авторизации на Django REST Framework с PostgreSQL.

## Стек технологий

- **Python 3.12** — язык разработки
- **Django 5** + **DRF** — веб-фреймворк и REST toolkit
- **PostgreSQL** — основная база данных
- **JWT** (djangorestframework-simplejwt) — аутентификация через токены
- **RBAC** — ролевая модель доступа (Role-Based Access Control)

## Архитектура доступа

Система реализует RBAC: каждый пользователь имеет одну или несколько ролей,
каждая роль имеет набор прав на бизнес-объекты (продукты, заказы, магазины).

Роли: `admin`, `manager`, `user`, `guest`

Права на ресурс: `read`, `read_all`, `create`, `update`, `update_all`, `delete`, `delete_all`

## Быстрый старт

```bash
# 1. Клонируем репозиторий
git clone https://github.com/ВАШ_ЛОГИН/auth-service.git
cd auth-service

# 2. Создаём и активируем виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Настраиваем переменные окружения
cp .env.example .env
# Заполни .env своими данными (БД, секретный ключ)

# 5. Применяем миграции
python manage.py migrate

# 6. Заполняем тестовыми данными
# python manage.py seed  

# 7. Запускаем сервер
python manage.py runserver
```

## API Endpoints (будущие)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| POST | `/api/auth/register/` | Регистрация | Нет |
| POST | `/api/auth/login/` | Вход | Нет |
| POST | `/api/auth/logout/` | Выход | JWT |
| GET | `/api/auth/profile/` | Просмотр профиля | JWT |
| PATCH | `/api/auth/profile/` | Частичное обновление профиля | JWT |
| DELETE | `/api/auth/profile/` | Удаление аккаунта (soft) | JWT |

## Схема БД
