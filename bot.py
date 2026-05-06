import asyncio
import logging
import socket
import sys

# Fix for aiohttp on Windows Python 3.8+ (WinError 121)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Force IPv4: patch aiohttp.ClientSession before aiogram imports it
import aiohttp
_OrigClientSession = aiohttp.ClientSession
class _IPv4ClientSession(_OrigClientSession):
    def __init__(self, *args, **kwargs):
        if "connector" not in kwargs:
            kwargs["connector"] = aiohttp.TCPConnector(family=socket.AF_INET)
        super().__init__(*args, **kwargs)
aiohttp.ClientSession = _IPv4ClientSession

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN, MINI_APP_URL

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message) -> None:
    if not MINI_APP_URL:
        await message.answer("Mini App URL not configured. Set MINI_APP_URL in .env")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="Открыть Astro",
        web_app=types.WebAppInfo(url=MINI_APP_URL)
    ))
    await message.answer(
        "Ваш личный астролог.\nНажмите кнопку чтобы открыть приложение.",
        reply_markup=kb
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
