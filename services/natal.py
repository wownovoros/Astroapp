# --- Compatibility patch for pyswisseph >= 2.8 ---
import swisseph as _swe
_orig_calc_ut = _swe.calc_ut
def _compat_calc_ut(jd, planet, *args, **kwargs):
    result = _orig_calc_ut(jd, planet, *args, **kwargs)
    return result[0] if isinstance(result[0], (tuple, list)) else result
_swe.calc_ut = _compat_calc_ut
# Set Swiss Ephemeris path explicitly so it works in any server context
import flatlib as _fl
_swe.set_ephe_path(_fl.PATH_RES + 'swefiles')
# --- end patch ---

import os, math
from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

DEFAULT_TZ_OFFSET = os.getenv("DEFAULT_TZ_OFFSET", "+03:00")
DEFAULT_LAT = os.getenv("DEFAULT_LAT", "55.7558")
DEFAULT_LON = os.getenv("DEFAULT_LON", "37.6176")

SIGN_RU = {
    "Aries":"Овен","Taurus":"Телец","Gemini":"Близнецы","Cancer":"Рак",
    "Leo":"Лев","Virgo":"Дева","Libra":"Весы","Scorpio":"Скорпион",
    "Sagittarius":"Стрелец","Capricorn":"Козерог","Aquarius":"Водолей","Pisces":"Рыбы",
}
SIGN_EMOJI = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋",
    "Leo":"♌","Virgo":"♍","Libra":"♎","Scorpio":"♏",
    "Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
}
PLANET_RU = {
    const.SUN:"Солнце",const.MOON:"Луна",const.MERCURY:"Меркурий",
    const.VENUS:"Венера",const.MARS:"Марс",const.JUPITER:"Юпитер",
    const.SATURN:"Сатурн",const.URANUS:"Уран",const.NEPTUNE:"Нептун",
    const.PLUTO:"Плутон",const.CHIRON:"Хирон",const.NORTH_NODE:"Сев. Узел",
}
PLANET_EMOJI = {
    const.SUN:"☉",const.MOON:"☽",const.MERCURY:"☿",const.VENUS:"♀",
    const.MARS:"♂",const.JUPITER:"♃",const.SATURN:"♄",const.URANUS:"♅",
    const.NEPTUNE:"♆",const.PLUTO:"♇",const.CHIRON:"⚷",const.NORTH_NODE:"☊",
}
PLANET_MEANING = {
    const.SUN: "воля, самовыражение, жизненная сила",
    const.MOON: "эмоции, интуиция, подсознание",
    const.MERCURY: "ум, речь, коммуникация",
    const.VENUS: "любовь, красота, ценности",
    const.MARS: "энергия, воля, действие",
    const.JUPITER: "удача, рост, мудрость",
    const.SATURN: "дисциплина, ограничения, уроки",
    const.URANUS: "перемены, свобода, оригинальность",
    const.NEPTUNE: "мечты, духовность, иллюзии",
    const.PLUTO: "трансформация, власть, глубина",
    const.CHIRON: "раны и исцеление, ключ к мудрости",
    const.NORTH_NODE: "кармическая задача, путь роста",
}
SIGN_MEANING = {
    "Aries":"инициатива и прямая энергия","Taurus":"устойчивость и практичность",
    "Gemini":"гибкий ум и коммуникация","Cancer":"эмоции и потребность в безопасности",
    "Leo":"самовыражение и лидерство","Virgo":"порядок и аналитичность",
    "Libra":"баланс и дипломатия","Scorpio":"глубина и внутренняя сила",
    "Sagittarius":"рост и поиск смысла","Capricorn":"дисциплина и результат",
    "Aquarius":"независимость и новаторство","Pisces":"интуиция и сопереживание",
}
ASPECT_NAMES = {
    0:"Соединение ☌",60:"Секстиль ⚹",90:"Квадрат □",
    120:"Тригон △",150:"Квинконс ⚻",180:"Оппозиция ☍",
}
ASPECT_ORB = {0:8,60:6,90:7,120:8,150:3,180:8}
ASPECT_NATURE = {0:"нейтральный",60:"гармоничный",90:"напряжённый",
                 120:"гармоничный",150:"напряжённый",180:"напряжённый"}

SIGN_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def _lon_to_sign_deg(lon):
    sign_idx = int(lon // 30)
    deg = lon - sign_idx * 30
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    sign = SIGN_ORDER[sign_idx % 12]
    return sign, d, m, s

def _calc_aspect(lon1, lon2):
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    for angle, orb in ASPECT_ORB.items():
        if abs(diff - angle) <= orb:
            return angle, round(abs(diff - angle), 1)
    return None, None

def build_natal_data(birth_date_ddmmyyyy: str, birth_time: str = "12:00") -> dict:
    day, month, year = birth_date_ddmmyyyy.split("-")
    dt = Datetime(f"{year}/{month}/{day}", birth_time, DEFAULT_TZ_OFFSET)
    pos = GeoPos(float(DEFAULT_LAT), float(DEFAULT_LON))
    ALL_OBJECTS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
               const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE,
               const.PLUTO, const.CHIRON, const.NORTH_NODE]
    chart = Chart(dt, pos, IDs=ALL_OBJECTS)

    # Planets
    planets = []
    for pid in [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
                const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE,
                const.PLUTO, const.CHIRON, const.NORTH_NODE]:
        obj = chart.get(pid)
        sign, d, m, s = _lon_to_sign_deg(obj.lon)
        retro = hasattr(obj, 'movement') and obj.movement() == const.RETROGRADE
        planets.append({
            "id": pid,
            "name": PLANET_RU.get(pid, pid),
            "emoji": PLANET_EMOJI.get(pid, ""),
            "sign": sign,
            "sign_ru": SIGN_RU.get(sign, sign),
            "sign_emoji": SIGN_EMOJI.get(sign, ""),
            "deg": d, "min": m, "sec": s,
            "lon": round(obj.lon, 4),
            "retro": retro,
            "meaning": PLANET_MEANING.get(pid, ""),
            "sign_meaning": SIGN_MEANING.get(sign, ""),
        })

    # ASC & MC
    asc = chart.get(const.ASC)
    mc  = chart.get(const.MC)
    asc_sign, ad, am, as_ = _lon_to_sign_deg(asc.lon)
    mc_sign,  md, mm, ms  = _lon_to_sign_deg(mc.lon)

    # Aspects
    aspects = []
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            angle, orb = _calc_aspect(planets[i]["lon"], planets[j]["lon"])
            if angle is not None:
                aspects.append({
                    "p1": planets[i]["name"],
                    "p1e": planets[i]["emoji"],
                    "p2": planets[j]["name"],
                    "p2e": planets[j]["emoji"],
                    "angle": angle,
                    "name": ASPECT_NAMES[angle],
                    "orb": orb,
                    "nature": ASPECT_NATURE[angle],
                })

    return {
        "date": f"{day}.{month}.{year}",
        "time": birth_time,
        "planets": planets,
        "asc": {"sign": asc_sign, "sign_ru": SIGN_RU.get(asc_sign, asc_sign),
                "sign_emoji": SIGN_EMOJI.get(asc_sign,""),
                "deg": ad, "min": am, "lon": round(asc.lon, 4)},
        "mc":  {"sign": mc_sign,  "sign_ru": SIGN_RU.get(mc_sign, mc_sign),
                "sign_emoji": SIGN_EMOJI.get(mc_sign,""),
                "deg": md, "min": mm, "lon": round(mc.lon, 4)},
        "aspects": aspects,
    }

def build_natal_report(birth_date_ddmmyyyy: str, birth_time: str = "12:00") -> str:
    """Текстовый отчёт (для обратной совместимости)"""
    data = build_natal_data(birth_date_ddmmyyyy, birth_time)
    lines = [f"🌌 Натальная карта — {data['date']} {data['time']}\n"]
    for p in data["planets"]:
        r = " ℞" if p["retro"] else ""
        lines.append(
            f"{p['emoji']} {p['name']} в {p['sign_emoji']} {p['sign_ru']} "
            f"{p['deg']}°{p['min']:02d}'{r}"
        )
    lines.append(f"\n↑ Асцендент: {data['asc']['sign_emoji']} {data['asc']['sign_ru']} {data['asc']['deg']}°{data['asc']['min']:02d}'")
    lines.append(f"MC: {data['mc']['sign_emoji']} {data['mc']['sign_ru']} {data['mc']['deg']}°{data['mc']['min']:02d}'")

    harm = [a for a in data["aspects"] if a["nature"] == "гармоничный"][:3]
    tens = [a for a in data["aspects"] if a["nature"] == "напряжённый"][:3]
    if harm:
        lines.append("\n✨ Гармоничные аспекты:")
        for a in harm:
            lines.append(f"  {a['p1e']}{a['p2e']} {a['name']} (орб {a['orb']}°)")
    if tens:
        lines.append("⚡ Напряжённые аспекты:")
        for a in tens:
            lines.append(f"  {a['p1e']}{a['p2e']} {a['name']} (орб {a['orb']}°)")
    return "\n".join(lines)
