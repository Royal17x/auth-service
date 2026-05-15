# Auth Service

Backend-сервис аутентификации и авторизации на Django REST Framework с PostgreSQL.

## Стек

- **Python 3.12** + **Django 5** + **Django REST Framework**
- **PostgreSQL 16** — основная база данных
- **JWT** (djangorestframework-simplejwt) — аутентификация через токены
- **RBAC** — ролевая модель доступа (Role-Based Access Control)
- **Docker** + **Docker Compose**

---

## Архитектура

```
auth-service/
├── apps/
│   ├── users/       # Аутентификация: register, login, logout, profile
│   ├── roles/       # RBAC: роли, права, назначение
│   └── resources/   # Mock бизнес-объекты с проверкой прав
├── config/          # Настройки Django, главный роутер
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

### Схема базы данных

```
users               roles               business_elements
─────────────       ─────────────       ─────────────────
id (UUID)           id                  id
email               name                name
first_name          description         description
last_name
patronymic          user_roles          access_roles_rules
is_active           ──────────          ──────────────────
password            user_id → users     role_id → roles
created_at          role_id → roles     element_id → business_elements
updated_at          assigned_at         read_permission
                                        read_all_permission
                                        create_permission
                                        update_permission
                                        update_all_permission
                                        delete_permission
                                        delete_all_permission
```

### Модель прав доступа

| Роль | products | orders | shops | users | access_rules |
|------|----------|--------|-------|-------|--------------|
| **admin** | CRUD все | CRUD все | CRUD все | CRUD все | CRUD все |
| **manager** | Read all + CU | Read all + CU | Read all | — | — |
| **user** | Read own | Read own | — | — | — |
| **guest** | Read own | — | — | — | — |

---

## Быстрый старт

### Вариант 1 — Docker (рекомендуется)

```bash
git clone https://github.com/YOUR_USERNAME/auth-service.git
cd auth-service

docker compose up --build
```

Приложение доступно на http://localhost:8000  
Тестовые пользователи создаются автоматически при старте.

### Вариант 2 — Локально

```bash
git clone https://github.com/YOUR_USERNAME/auth-service.git
cd auth-service

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Заполни .env своими данными

python manage.py migrate
python manage.py seed
python manage.py runserver
```

---

## Тестовые пользователи (после seed)

| Email | Пароль | Роль |
|-------|--------|------|
| admin@example.com | admin123 | admin |
| manager@example.com | manager123 | manager |
| user@example.com | user123 | user |
| guest@example.com | guest123 | guest |

---

## API

### Аутентификация

| Метод | URL | Описание | Auth |
|-------|-----|----------|------|
| POST | `/api/auth/register/` | Регистрация | — |
| POST | `/api/auth/login/` | Вход, возвращает access + refresh токены | — |
| POST | `/api/auth/logout/` | Выход, инвалидирует refresh токен | JWT |
| GET | `/api/auth/profile/` | Просмотр своего профиля | JWT |
| PATCH | `/api/auth/profile/` | Частичное обновление профиля | JWT |
| DELETE | `/api/auth/profile/` | Деактивация аккаунта (soft delete) | JWT |
| POST | `/api/auth/change-password/` | Смена пароля | JWT |
| POST | `/api/auth/token/refresh/` | Обновление access токена | — |

### Роли и права (только admin)

| Метод | URL | Описание |
|-------|-----|----------|
| GET / POST | `/api/roles/` | Список ролей / создать роль |
| GET / PATCH / DELETE | `/api/roles/<id>/` | Управление ролью |
| GET / POST | `/api/roles/elements/` | Список бизнес-элементов / создать |
| GET / PATCH / DELETE | `/api/roles/elements/<id>/` | Управление элементом |
| GET / POST | `/api/roles/rules/` | Правила доступа / создать |
| GET / PATCH / DELETE | `/api/roles/rules/<id>/` | Управление правилом |
| POST | `/api/roles/assign/` | Назначить роль пользователю |
| POST | `/api/roles/revoke/` | Снять роль с пользователя |
| GET | `/api/roles/user/<user_id>/` | Роли конкретного пользователя |
| GET | `/api/roles/my/` | Мои роли | JWT |

### Ресурсы

| Метод | URL | Описание | Auth |
|-------|-----|----------|------|
| GET / POST | `/api/resources/products/` | Продукты | JWT + права |
| GET / PATCH / DELETE | `/api/resources/products/<id>/` | Продукт по ID | JWT + права |
| GET / POST | `/api/resources/orders/` | Заказы | JWT + права |
| GET | `/api/resources/shops/` | Магазины | JWT + права |
| GET | `/api/resources/my-permissions/` | Мои права на все ресурсы | JWT |

---

## Примеры запросов

### Регистрация
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "Иван",
    "last_name": "Петров",
    "password": "strongpass123",
    "password_confirm": "strongpass123"
  }'
```

### Вход и сохранение токена
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['tokens']['access'])")
```

### Запрос с токеном
```bash
curl http://localhost:8000/api/resources/products/ \
  -H "Authorization: Bearer $TOKEN"
```

### Мои права
```bash
curl http://localhost:8000/api/resources/my-permissions/ \
  -H "Authorization: Bearer $TOKEN"
```

### Назначить роль (только admin)
```bash
curl -X POST http://localhost:8000/api/roles/assign/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "uuid-пользователя", "role_id": 2}'
```

---

## Тесты

```bash
# Локально
python manage.py test apps --verbosity=2

# Через Docker
docker compose exec web python manage.py test apps --verbosity=2
```

---

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `SECRET_KEY` | Секретный ключ Django | `django-secret-...` |
| `DEBUG` | Режим отладки | `True` / `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `DB_NAME` | Имя базы данных | `auth_db` |
| `DB_USER` | Пользователь БД | `auth_user` |
| `DB_PASSWORD` | Пароль БД | `yourpassword` |
| `DB_HOST` | Хост БД | `localhost` / `db` |
| `DB_PORT` | Порт БД | `5432` |
