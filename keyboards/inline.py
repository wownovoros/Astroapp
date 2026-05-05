from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Гороскоп сегодня", callback_data="horo:day"),
        InlineKeyboardButton("Гороскоп неделя", callback_data="horo:week"),
    )
    kb.add(InlineKeyboardButton("Натальная карта", callback_data="natal:open"))
    kb.add(InlineKeyboardButton("Открыть PRO (199 RUB)", callback_data="pay:open"))
    return kb
