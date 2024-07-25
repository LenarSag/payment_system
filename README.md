# payment_system

# Описание проекта

Этот проект предоставляет API для управления пользовательскими аккаунтами, балансами и платежами. Система поддерживает две роли: обычных пользователей и администраторов, каждая из которых имеет свои уникальные возможности.

## Возможности пользователя

Пользователь имеет следующие возможности:
- **Авторизация**: Вход в систему по email и паролю.
- **Информация о себе**: Получение данных о себе, таких как ID, email и полное имя.
- **Список счетов и балансов**: Получение списка своих счетов и их балансов.
- **История платежей**: Получение списка своих платежей.

## Возможности администратора

Администратор имеет следующие возможности:
- **Авторизация**: Вход в систему по email и паролю.
- **Информация о себе**: Получение данных о себе, таких как ID, email и полное имя.
- **Управление пользователями**: Создание, удаление и обновление информации о пользователях.
- **Список пользователей и их счета**: Получение списка пользователей и списка их счетов с балансами.

## Обработка платежей

Для работы с платежами используется роут, эмулирующий обработку вебхука от сторонней платежной системы. Структура JSON-объекта для обработки вебхука включает следующие поля:
- `transaction_id`: уникальный идентификатор транзакции в сторонней системе.
- `account_id`: уникальный идентификатор счета пользователя.
- `user_id`: уникальный идентификатор пользователя.
- `amount`: сумма пополнения счета пользователя.
- `signature`: подпись объекта.

Подпись (`signature`) формируется с использованием SHA256 хеша для строки, состоящей из конкатенации значений объекта в алфавитном порядке ключей и "секретного ключа", хранящегося в конфигурации проекта (`{account_id}{amount}{transaction_id}{user_id}{secret_key}`).

Пример:
Для `secret_key` равного `gfdmhghif38yrf9ew0jkf32`:
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

### Проверка вебхука

При обработке вебхука выполняются следующие проверки:
- **Подпись объекта**: Проверка корректности подписи.
- **Существование счета**: Проверка наличия счета у пользователя. Если счета нет, он создается.
- **Сохранение транзакции**: Сохранение информации о транзакции в базе данных.
- **Начисление суммы**: Начисление суммы транзакции на счет пользователя.

Транзакции являются уникальными. Начисление суммы с одним `transaction_id` производится только один раз.

### Технологии

- Python 3.9
- FastAPI
- SqlAlchemy


### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке: 
```
git clone git@github.com:LenarSag/foodgram_fastapi.git
```
Cоздать и активировать виртуальное окружение: 
```
python3.9 -m venv venv 
```
* Если у вас Linux/macOS 

    ```
    source venv/bin/activate
    ```
* Если у вас windows 
 
    ```
    source venv/scripts/activate
    ```
```
python3.9 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```


Выполнить миграции:


Подключаем и настраиваем алембик:

```
alembic init migration
```

В файле alembic.ini указываем адрес базы:

```
[alembic]
...
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
```

В файле migration/env.py импортируем все модели и указываем target_metadata:

```
from models.user import Base

target_metadata = Base.metadata
```

После этого:

```
alembic revision --autogenerate -m 'initial'
```
```
alembic revision -m "insert initial values"
```
Затем в папке migration заменяем upgrade и downgrade на этот код

```
def upgrade() -> None:
    # Insert test users into the person table and get their IDs
    person1_id = str(uuid.uuid4())
    person2_id = str(uuid.uuid4())

    op.execute(f"""
    INSERT INTO person (id, username, email, first_name, last_name, password, is_active, role, created_at)
    VALUES
    ('{person1_id}', 'testuser1', 'testuser1@test.com', 'Test', 'User1', '$2b$12$3D1f8osq1RSDwRoj4AwO5eyPC/hkEVxr..K3BwldLYoa4ltCdhp7C', true, 'user', NOW()),
    ('{person2_id}', 'testuser2', 'testuser2@test.com', 'Test', 'User2', '$2b$12$3D1f8osq1RSDwRoj4AwO5eyPC/hkEVxr..K3BwldLYoa4ltCdhp7C', true, 'admin', NOW());
    """)

    # Insert the corresponding records into the user and admin tables
    op.execute(f"""
    INSERT INTO "user" (person_id) VALUES ('{person1_id}');
    """)
    op.execute(f"""
    INSERT INTO "admin" (person_id) VALUES ('{person2_id}');
    """)


def downgrade() -> None:
    # Delete the inserted records
    op.execute("""
    DELETE FROM "user" WHERE person_id IN (SELECT id FROM person WHERE username IN ('testuser1'));
    DELETE FROM "admin" WHERE person_id IN (SELECT id FROM person WHERE username IN ('testuser2'));
    DELETE FROM person WHERE username IN ('testuser1', 'testuser2');
    """)
```
Потом создаем миграции

```
alembic upgrade head
```


Пароли для получения JWT токена Q16werty!23