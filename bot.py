import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice
from aiogram.utils import executor

from config import BOT_TOKEN, PAYMENT_TOKEN
from database.db import get_user, init_db, save_user, set_subscription
from keyboards.inline import main_menu
from services.analytics import format_stats, track_event
from services.natal import build_natal_report
from services.parser import get_daily_horoscope, get_weekly_horoscope
from services.ratelimit import is_allowed
from services.subscriptions import has_active_subscription
from services.zodiac import SIGN_RU, get_sign, parse_birthdate

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is empty. Set it in .env file.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message) -> None:
    track_event(message.from_user.id, "start")
    await message.answer(
        "Введите дату рождения в формате ДД-ММ-ГГГГ.\n"
        "После этого я открою меню с гороскопом и натальной картой."
    )


@dp.message_handler(commands=["stats"])
async def stats_handler(message: types.Message) -> None:
    await message.answer(format_stats())


@dp.message_handler(lambda m: "-" in m.text)
async def save_birthdate_handler(message: types.Message) -> None:
    try:
        date = parse_birthdate(message.text)
    except ValueError:
        await message.answer("Неверный формат. Пример: 09-11-1998")
        return
    sign_slug = get_sign(date.day, date.month)
    save_user(message.from_user.id, date.strftime("%d-%m-%Y"), sign_slug)
    track_event(message.from_user.id, "birthdate_saved", sign_slug)
    await message.answer(
        f"Сохранено. Ваш знак: {SIGN_RU[sign_slug]}.\nВыберите действие:",
        reply_markup=main_menu(),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("horo:"))
async def horoscope_handler(call: types.CallbackQuery) -> None:
    await call.answer()
    if not is_allowed(call.from_user.id):
        await call.message.answer("Слишком много запросов. Подождите минуту.")
        return

    user = get_user(call.from_user.id)
    if not user:
        await call.message.answer("Сначала отправьте дату рождения.")
        return

    sign_slug = user["sign"]
    mode = call.data.split(":")[1]
    if mode == "day":
        text = get_daily_horoscope(sign_slug)
    else:
        text = get_weekly_horoscope(sign_slug)

    track_event(call.from_user.id, "view_horoscope", mode)
    await call.message.answer(f"{SIGN_RU[sign_slug]}:\n\n{text}")


@dp.callback_query_handler(lambda c: c.data == "natal:open")
async def natal_handler(call: types.CallbackQuery) -> None:
    await call.answer()
    user = get_user(call.from_user.id)
    if not user:
        await call.message.answer("Сначала отправьте дату рождения.")
        return

    if not has_active_subscription(user):
        track_event(call.from_user.id, "paywall", "natal")
        await call.message.answer(
            "Натальная карта доступна в PRO.\n"
            "Нажмите кнопку `Открыть PRO (199 RUB)`.",
        )
        return

    report = build_natal_report(user["birthdate"])
    await call.message.answer(report)


@dp.callback_query_handler(lambda c: c.data == "pay:open")
async def pay_handler(call: types.CallbackQuery) -> None:
    await call.answer()
    if not PAYMENT_TOKEN:
        await call.message.answer("Платежи не настроены. Добавьте PAYMENT_TOKEN в .env.")
        return
    await bot.send_invoice(
        call.from_user.id,
        title="Astro PRO - 30 дней",
        description="Полный доступ к натальной карте и персональным разборам.",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice("Подписка 30 дней", 19900)],
        payload="astro_pro_30",
        start_parameter="astro-pro",
    )


@dp.pre_checkout_query_handler(lambda q: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message) -> None:
    set_subscription(message.from_user.id, days=30)
    track_event(message.from_user.id, "paid", "30_days")
    await message.answer("Оплата прошла успешно. PRO активирован на 30 дней.")


async def daily_retention_loop() -> None:
    # Placeholder for production scheduler integration (cron/APScheduler/Celery).
    while True:
        await asyncio.sleep(24 * 60 * 60)


if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
