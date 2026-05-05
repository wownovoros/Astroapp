# Astro App Telegram Bot

Готовый проект Telegram-бота с:
- гороскопом на день и неделю (парсинг `geocult.ru`),
- натальной картой (через `flatlib`),
- paywall и Telegram-платежами,
- аналитикой событий воронки,
- ограничением частоты запросов,
- Docker-развертыванием.

## Быстрый старт

1. Скопируйте `.env.example` в `.env`.
2. Заполните `BOT_TOKEN` и `PAYMENT_TOKEN`.
3. Запустите:

```bash
docker compose up -d --build
```

4. Откройте Telegram-бота и выполните:
   - `/start`
   - отправьте дату рождения `ДД-ММ-ГГГГ`
   - используйте кнопки меню.

## Команды

- `/start` — начало работы.
- `/stats` — показатели воронки.

## События аналитики

Записываются в `events`:
- `start`
- `birthdate_saved`
- `view_horoscope`
- `paywall`
- `paid`
