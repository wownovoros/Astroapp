from datetime import datetime


def get_sign(day: int, month: int) -> str:
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "oven"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "telec"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "bliznecy"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "rak"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "lev"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "deva"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "vesy"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "skorpion"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "strelec"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "kozerog"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "vodoley"
    return "ryby"


SIGN_RU = {
    "oven": "Овен",
    "telec": "Телец",
    "bliznecy": "Близнецы",
    "rak": "Рак",
    "lev": "Лев",
    "deva": "Дева",
    "vesy": "Весы",
    "skorpion": "Скорпион",
    "strelec": "Стрелец",
    "kozerog": "Козерог",
    "vodoley": "Водолей",
    "ryby": "Рыбы",
}


def parse_birthdate(text: str) -> datetime:
    return datetime.strptime(text.strip(), "%d-%m-%Y")
