# --- Compatibility patch for pyswisseph >= 2.8 ---
import swisseph as _swe
_orig_calc_ut = _swe.calc_ut

def _compat_calc_ut(jd, planet, *args, **kwargs):
    result = _orig_calc_ut(jd, planet, *args, **kwargs)
    return result[0] if isinstance(result[0], (tuple, list)) else result

_swe.calc_ut = _compat_calc_ut
# --- end patch ---

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

DEFAULT_TZ_OFFSET = os.getenv("DEFAULT_TZ_OFFSET", "+03:00")
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "55.7558")
DEFAULT_LON = os.getenv("DEFAULT_LON", "37.6176")

PLANET_LABELS = {
    const.SUN:     "Солнце",
    const.MOON:    "Луна",
    const.MERCURY: "Меркурий",
    const.VENUS:   "Венера",
    const.MARS:    "Марс",
    const.JUPITER: "Юпитер",
    const.SATURN:  "Сатурн",
}

SIGN_RU = {
    "Aries":       "Овен",
    "Taurus":      "Телец",
    "Gemini":      "Близнецы",
    "Cancer":      "Рак",
    "Leo":         "Лев",
    "Virgo":       "Дева",
    "Libra":       "Весы",
    "Scorpio":     "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn":   "Козерог",
    "Aquarius":    "Водолей",
    "Pisces":      "Рыбы",
}

SIGN_MEANING = {
    "Aries":       "инициатива и прямая энергия",
    "Taurus":      "устойчивость и практичность",
    "Gemini":      "гибкий ум и коммуникация",
    "Cancer":      "эмоции и потребность в безопасности",
    "Leo":         "самовыражение и лидерство",
    "Virgo":       "порядок и аналитичность",
    "Libra":       "баланс и дипломатия",
    "Scorpio":     "глубина и внутренняя сила",
    "Sagittarius": "рост и поиск смысла",
    "Capricorn":   "дисциплина и результат",
    "Aquarius":    "независимость и новаторство",
    "Pisces":      "интуиция и сопереживание",
}


def build_natal_report(birth_date_ddmmyyyy: str, birth_time: str = "12:00") -> str:
    day, month, year = birth_date_ddmmyyyy.split("-")
    dt = Datetime(f"{year}/{month}/{day}", birth_time, DEFAULT_TZ_OFFSET)
    pos = GeoPos(float(DEFAULT_LAT), float(DEFAULT_LON))
    chart = Chart(dt, pos)

    lines = ["Персональный разбор натальной карты:"]
    for planet in PLANET_LABELS:
        obj = chart.get(planet)
        sign_ru  = SIGN_RU.get(obj.sign, obj.sign)
        meaning  = SIGN_MEANING.get(obj.sign, "индивидуальные особенности")
        lines.append(f"- {PLANET_LABELS[planet]} в {sign_ru}: акцент на {meaning}.")

    asc = chart.get(const.ASC)
    asc_ru = SIGN_RU.get(asc.sign, asc.sign)
    lines.append(f"- Асцендент в {asc_ru}: ваш социальный стиль и первое впечатление.")
    lines.append("")
    lines.append("Рекомендация: опирайтесь на сильные стороны Солнца и Луны, выбирая нагрузку и темп.")
    return "\n".join(lines)
