from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_TZ_OFFSET

PLANET_LABELS = {
    const.SUN: "Солнце",
    const.MOON: "Луна",
    const.MERCURY: "Меркурий",
    const.VENUS: "Венера",
    const.MARS: "Марс",
}

SIGN_MEANING = {
    "Aries": "инициатива и прямая энергия",
    "Taurus": "устойчивость и практичность",
    "Gemini": "гибкий ум и коммуникация",
    "Cancer": "эмоции и потребность в безопасности",
    "Leo": "самовыражение и лидерство",
    "Virgo": "порядок и аналитичность",
    "Libra": "баланс и дипломатия",
    "Scorpio": "глубина и внутренняя сила",
    "Sagittarius": "рост и поиск смысла",
    "Capricorn": "дисциплина и результат",
    "Aquarius": "независимость и новаторство",
    "Pisces": "интуиция и сопереживание",
}


def build_natal_report(birth_date_ddmmyyyy: str, birth_time: str = "12:00") -> str:
    day, month, year = birth_date_ddmmyyyy.split("-")
    dt = Datetime(f"{year}/{month}/{day}", birth_time, DEFAULT_TZ_OFFSET)
    pos = GeoPos(DEFAULT_LAT, DEFAULT_LON)
    chart = Chart(dt, pos)

    lines = ["Персональный разбор натальной карты:"]
    for planet in PLANET_LABELS:
        obj = chart.get(planet)
        meaning = SIGN_MEANING.get(obj.sign, "индивидуальные особенности")
        lines.append(f"- {PLANET_LABELS[planet]} в {obj.sign}: акцент на {meaning}.")

    asc = chart.get(const.ASC)
    lines.append(f"- Асцендент в {asc.sign}: ваш социальный стиль и первое впечатление.")
    lines.append("")
    lines.append("Рекомендация дня: опирайтесь на сильные стороны Солнца и Луны, чтобы выбирать нагрузку и темп.")
    return "\n".join(lines)
