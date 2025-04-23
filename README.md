# TG-bot-Django
Проект реализция созданный для своевременного уведомления спортсменов о получении результатов на gymkhana-cup.

# Архитектура
Client - server
# Стэк
- Django ( web морда )
- htmx ( интерактивность в запросах )
- PostgreSQL ( Хранение данных )
- Redis ( FSM, Кэш )
- RabbitMQ ( Рассылка сообщений )
- Selery (Периодические задачи)
- python-telegram-bot ( api прослойка между тг и приложением )
- aiohttp ( Общение с api/парсинг )

# Схема взаимодействий

``` mermaid
graph TD
    A[api.gymkhana-cup.ru] -->|Polling каждые 5 мин| B(Django + Celery)
    B --> C[(Reddis)]
    C--> K[(PostgreSQL)]
    B -->|Отправка сообщений| D[RabbitMQ]
    D --> E[Telegram Consumer]
    E -->|Отправка уведомлений| F[Telegram API]
    G[Telegram Bot] -->|Команды подписки| H[Users]
    I[Django Admin] -->|Управление подписками| B
    H -->|Авторизация| J[Django Auth]
    J --> B
    F --> |Команды подписок| E
```