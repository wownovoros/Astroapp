# --- Compatibility patch for pyswisseph >= 2.8 ---
import swisseph as _swe
_orig_calc_ut = _swe.calc_ut
def _compat_calc_ut(jd, planet, *args, **kwargs):
    result = _orig_calc_ut(jd, planet, *args, **kwargs)
    return result[0] if isinstance(result[0], (tuple, list)) else result
_swe.calc_ut = _compat_calc_ut
import flatlib as _fl
_swe.set_ephe_path(_fl.PATH_RES + 'swefiles')
# --- end patch ---

import os
from datetime import datetime as _dt
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

DEFAULT_TZ_OFFSET = os.getenv("DEFAULT_TZ_OFFSET", "+03:00")
DEFAULT_LAT       = os.getenv("DEFAULT_LAT", "55.7558")
DEFAULT_LON       = os.getenv("DEFAULT_LON", "37.6176")

# ── Lookup tables ────────────────────────────────────────────────────────────

SIGN_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

SIGN_RU = {
    "Aries":"Овен","Taurus":"Телец","Gemini":"Близнецы","Cancer":"Рак",
    "Leo":"Лев","Virgo":"Дева","Libra":"Весы","Scorpio":"Скорпион",
    "Sagittarius":"Стрелец","Capricorn":"Козерог","Aquarius":"Водолей","Pisces":"Рыбы",
}
SIGN_EMOJI = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍",
    "Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
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
    const.SUN:"воля, самовыражение, жизненная сила",
    const.MOON:"эмоции, интуиция, подсознание",
    const.MERCURY:"ум, речь, коммуникация",
    const.VENUS:"любовь, красота, ценности",
    const.MARS:"энергия, воля, действие",
    const.JUPITER:"удача, рост, мудрость",
    const.SATURN:"дисциплина, ограничения, уроки",
    const.URANUS:"перемены, свобода, оригинальность",
    const.NEPTUNE:"мечты, духовность, иллюзии",
    const.PLUTO:"трансформация, власть, глубина",
    const.CHIRON:"раны и исцеление, ключ к мудрости",
    const.NORTH_NODE:"кармическая задача, путь роста",
}
SIGN_MEANING = {
    "Aries":"инициатива и прямая энергия","Taurus":"устойчивость и практичность",
    "Gemini":"гибкий ум и коммуникация","Cancer":"эмоции и потребность в безопасности",
    "Leo":"самовыражение и лидерство","Virgo":"порядок и аналитичность",
    "Libra":"баланс и дипломатия","Scorpio":"глубина и внутренняя сила",
    "Sagittarius":"рост и поиск смысла","Capricorn":"дисциплина и результат",
    "Aquarius":"независимость и новаторство","Pisces":"интуиция и сопереживание",
}

SIGN_RULER = {
    "Aries":"Марс","Taurus":"Венера","Gemini":"Меркурий","Cancer":"Луна",
    "Leo":"Солнце","Virgo":"Меркурий","Libra":"Венера","Scorpio":"Плутон",
    "Sagittarius":"Юпитер","Capricorn":"Сатурн","Aquarius":"Уран","Pisces":"Нептун",
}

HOUSE_MEANING = {
    1:"Личность, внешность, первое впечатление, начало пути",
    2:"Деньги, ресурсы, ценности, материальная безопасность",
    3:"Общение, мышление, братья/сёстры, короткие поездки",
    4:"Дом, семья, корни, детство, недвижимость",
    5:"Творчество, романтика, дети, удовольствие, игра",
    6:"Работа, здоровье, распорядок дня, служение",
    7:"Партнёрство, брак, открытые враги, договоры",
    8:"Трансформация, чужие ресурсы, тайное, сексуальность",
    9:"Философия, высшее образование, путешествия, мировоззрение",
    10:"Карьера, репутация, публичная жизнь, статус",
    11:"Друзья, группы, мечты, гуманизм, социальные связи",
    12:"Тайное, подсознание, изоляция, духовность, карма",
}

ASPECT_NAMES = {
    0:"Соединение ☌",60:"Секстиль ⚹",90:"Квадрат □",
    120:"Тригон △",150:"Квинконс ⚻",180:"Оппозиция ☍",
}
ASPECT_ORB  = {0:8,60:6,90:7,120:8,150:3,180:8}
ASPECT_NATURE = {0:"нейтральный",60:"гармоничный",90:"напряжённый",
                 120:"гармоничный",150:"напряжённый",180:"напряжённый"}

FIRE_SIGNS     = {"Aries","Leo","Sagittarius"}
EARTH_SIGNS    = {"Taurus","Virgo","Capricorn"}
AIR_SIGNS      = {"Gemini","Libra","Aquarius"}
WATER_SIGNS    = {"Cancer","Scorpio","Pisces"}
CARDINAL_SIGNS = {"Aries","Cancer","Libra","Capricorn"}
FIXED_SIGNS    = {"Taurus","Leo","Scorpio","Aquarius"}
MUTABLE_SIGNS  = {"Gemini","Virgo","Sagittarius","Pisces"}

ALL_OBJECTS = [
    const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
    const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE,
    const.PLUTO, const.CHIRON, const.NORTH_NODE
]
HOUSE_CONST = [
    const.HOUSE1, const.HOUSE2, const.HOUSE3, const.HOUSE4,
    const.HOUSE5, const.HOUSE6, const.HOUSE7, const.HOUSE8,
    const.HOUSE9, const.HOUSE10, const.HOUSE11, const.HOUSE12,
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def _lon_to_sign_deg(lon):
    idx = int(lon // 30) % 12
    deg_total = lon - idx * 30
    d = int(deg_total)
    m = int((deg_total - d) * 60)
    s = int(((deg_total - d) * 60 - m) * 60)
    return SIGN_ORDER[idx], d, m, s

def _calc_aspect(lon1, lon2):
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    for angle, orb in ASPECT_ORB.items():
        if abs(diff - angle) <= orb:
            return angle, round(abs(diff - angle), 1)
    return None, None

def _get_tz_offset(tz_name: str, day: str, month: str, year: str, birth_time: str) -> str:
    """Return UTC offset string like +03:00 for a given timezone and local datetime."""
    try:
        h, m = map(int, birth_time.split(':'))
        naive = _dt(int(year), int(month), int(day), h, m)
        aware = naive.replace(tzinfo=ZoneInfo(tz_name))
        offset = aware.utcoffset()
        total = int(offset.total_seconds())
        sign = '+' if total >= 0 else '-'
        abs_t = abs(total)
        return f"{sign}{abs_t // 3600:02d}:{(abs_t % 3600) // 60:02d}"
    except Exception:
        return DEFAULT_TZ_OFFSET

def _get_house_num(planet_lon: float, house_lons: list) -> int:
    """Given sorted list of 12 house cusp longitudes, return house number 1-12."""
    for i in range(12):
        cusp      = house_lons[i]
        next_cusp = house_lons[(i + 1) % 12]
        if cusp < next_cusp:
            if cusp <= planet_lon < next_cusp:
                return i + 1
        else:  # wraps around 360
            if planet_lon >= cusp or planet_lon < next_cusp:
                return i + 1
    return 1

# ── Main builder ─────────────────────────────────────────────────────────────

def build_natal_data(birth_date_ddmmyyyy: str,
                     birth_time: str = "12:00",
                     lat: float = None,
                     lon: float = None,
                     tz_name: str = None,
                     name: str = "") -> dict:

    day, month, year = birth_date_ddmmyyyy.split("-")
    use_lat = lat if lat is not None else float(DEFAULT_LAT)
    use_lon = lon if lon is not None else float(DEFAULT_LON)

    tz_offset = (
        _get_tz_offset(tz_name, day, month, year, birth_time)
        if tz_name else DEFAULT_TZ_OFFSET
    )

    flatlib_dt = Datetime(f"{year}/{month}/{day}", birth_time, tz_offset)
    pos = GeoPos(use_lat, use_lon)

    # Try Placidus, fall back to Equal for polar latitudes
    try:
        chart = Chart(flatlib_dt, pos, hsys=const.HOUSES_PLACIDUS, IDs=ALL_OBJECTS)
    except Exception:
        chart = Chart(flatlib_dt, pos, hsys=const.HOUSES_EQUAL, IDs=ALL_OBJECTS)

    # ── Houses ──────────────────────────────────────────────────────────────
    house_lons = []
    houses = []
    for i, hid in enumerate(HOUSE_CONST):
        h = chart.get(hid)
        sign, d, m, s = _lon_to_sign_deg(h.lon)
        house_lons.append(h.lon)
        houses.append({
            "num":       i + 1,
            "lon":       round(h.lon, 4),
            "sign":      sign,
            "sign_ru":   SIGN_RU.get(sign, sign),
            "sign_emoji":SIGN_EMOJI.get(sign, ""),
            "deg": d, "min": m,
            "ruler":     SIGN_RULER.get(sign, ""),
            "meaning":   HOUSE_MEANING.get(i + 1, ""),
        })

    # ── Planets ─────────────────────────────────────────────────────────────
    elements   = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    modalities = {"cardinal": 0, "fixed": 0, "mutable": 0}
    planets = []

    for pid in ALL_OBJECTS:
        obj  = chart.get(pid)
        sign, d, m, s = _lon_to_sign_deg(obj.lon)
        retro    = obj.isRetrograde()
        house_n  = _get_house_num(obj.lon, house_lons)

        # Count elements / modalities (skip North Node — it's a point)
        if pid != const.NORTH_NODE:
            if sign in FIRE_SIGNS:     elements["fire"]      += 1
            elif sign in EARTH_SIGNS:  elements["earth"]     += 1
            elif sign in AIR_SIGNS:    elements["air"]       += 1
            elif sign in WATER_SIGNS:  elements["water"]     += 1

            if sign in CARDINAL_SIGNS:    modalities["cardinal"] += 1
            elif sign in FIXED_SIGNS:     modalities["fixed"]    += 1
            elif sign in MUTABLE_SIGNS:   modalities["mutable"]  += 1

        planets.append({
            "id":          pid,
            "name":        PLANET_RU.get(pid, pid),
            "emoji":       PLANET_EMOJI.get(pid, ""),
            "sign":        sign,
            "sign_ru":     SIGN_RU.get(sign, sign),
            "sign_emoji":  SIGN_EMOJI.get(sign, ""),
            "deg": d, "min": m, "sec": s,
            "lon":         round(obj.lon, 4),
            "retro":       retro,
            "house":       house_n,
            "meaning":     PLANET_MEANING.get(pid, ""),
            "sign_meaning":SIGN_MEANING.get(sign, ""),
        })

    # ── ASC / MC ─────────────────────────────────────────────────────────────
    asc = chart.get(const.ASC)
    mc  = chart.get(const.MC)
    asc_sign, ad, am, _ = _lon_to_sign_deg(asc.lon)
    mc_sign,  md, mm, _ = _lon_to_sign_deg(mc.lon)

    # ── Aspects ──────────────────────────────────────────────────────────────
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            angle, orb = _calc_aspect(planets[i]["lon"], planets[j]["lon"])
            if angle is not None:
                aspects.append({
                    "p1":    planets[i]["name"],  "p1e": planets[i]["emoji"],
                    "p2":    planets[j]["name"],  "p2e": planets[j]["emoji"],
                    "angle": angle,
                    "name":  ASPECT_NAMES[angle],
                    "orb":   orb,
                    "nature":ASPECT_NATURE[angle],
                })

    # ── Dominant element / modality ──────────────────────────────────────────
    ELEM_RU = {"fire":"Огонь","earth":"Земля","air":"Воздух","water":"Вода"}
    MOD_RU  = {"cardinal":"Кардинальный","fixed":"Фиксированный","mutable":"Мутабельный"}

    dom_elem = max(elements,   key=elements.get)
    dom_mod  = max(modalities, key=modalities.get)

    return {
        "name":     name,
        "date":     f"{day}.{month}.{year}",
        "time":     birth_time,
        "location": {"lat": use_lat, "lon": use_lon, "tz_offset": tz_offset},
        "planets":  planets,
        "houses":   houses,
        "asc": {
            "sign": asc_sign, "sign_ru": SIGN_RU.get(asc_sign, asc_sign),
            "sign_emoji": SIGN_EMOJI.get(asc_sign, ""),
            "deg": ad, "min": am, "lon": round(asc.lon, 4),
        },
        "mc": {
            "sign": mc_sign, "sign_ru": SIGN_RU.get(mc_sign, mc_sign),
            "sign_emoji": SIGN_EMOJI.get(mc_sign, ""),
            "deg": md, "min": mm, "lon": round(mc.lon, 4),
        },
        "aspects":   aspects,
        "elements":  elements,
        "modalities":modalities,
        "dominant": {
            "element":     dom_elem,
            "element_ru":  ELEM_RU[dom_elem],
            "modality":    dom_mod,
            "modality_ru": MOD_RU[dom_mod],
        },
    }


def build_natal_report(birth_date_ddmmyyyy: str, birth_time: str = "12:00") -> str:
    """Текстовый отчёт (обратная совместимость)."""
    d = build_natal_data(birth_date_ddmmyyyy, birth_time)
    lines = [f"Натальная карта — {d['date']} {d['time']}\n"]
    for p in d["planets"]:
        r = " ℞" if p["retro"] else ""
        lines.append(f"{p['emoji']} {p['name']} в {p['sign_emoji']} {p['sign_ru']} "
                      f"{p['deg']}°{p['min']:02d}' (дом {p['house']}){r}")
    lines.append(f"\nАСЦ: {d['asc']['sign_emoji']} {d['asc']['sign_ru']} {d['asc']['deg']}°{d['asc']['min']:02d}'")
    lines.append(f"MC:  {d['mc']['sign_emoji']}  {d['mc']['sign_ru']}  {d['mc']['deg']}°{d['mc']['min']:02d}'")
    return "\n".join(lines)
