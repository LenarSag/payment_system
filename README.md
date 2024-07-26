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
git clone git@github.com:LenarSag/payment_system.git
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


В файле alembic.ini указываем адрес базы и данные для входа:

```
[alembic]
...
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
```
Затем запускаем команду

```
alembic upgrade head
```

Для запуска без Docker в main.py должен быть расскомментирован этот код

```
if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
```
Запуск:

```
python main.py
```

Для запуска c Docker в main.py должен быть расскомментирован этот код:

```
async def startup_event():
    await init_models()
app.add_event_handler("startup", startup_event)
```

Затем:

```
docker compose up --build
```

Из папки с проектом запустить команду bash:

```
docker exec -it  payment_system-web-1 alembic upgrade head
```

Пароли для получения JWT токена Q16werty!23