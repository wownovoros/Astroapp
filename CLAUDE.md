# CLAUDE.md — Контекст проекта AstroApp для ИИ-ассистента

## Суть проекта

Telegram Mini App + бот. Flask-сервер на Render.com. Деплой через GitHub (push → автодеплой).
Два раздела: Гороскоп по знаку + Натальная карта по дате/времени рождения.

**Живой URL:** https://astroapp-gk0z.onrender.com/
**Репозиторий:** GitHub (ветка main, автодеплой на Render)
**Локальная папка:** `D:\cursor обучение\.cursor\astro_app`

---

## Структура файлов

```
astro_app/
├── main.py                  # Flask app: маршруты, вебхук, запуск, keep-alive поток
├── requirements.txt         # Flask, gunicorn, requests, bs4, flatlib, pyswisseph, python-dotenv, timezonefinder
├── Procfile                 # web: gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
├── .python-version          # 3.12
├── public/
│   └── index.html           # Весь фронтенд (SPA, ~1013 строк)
└── services/
    ├── natal.py             # Расчёт натальной карты (flatlib + pyswisseph)
    ├── parser.py            # Гороскопы: скрапинг geocult.ru + fallback генератор
    ├── zodiac.py            # get_sign(day, month) → slug; SIGN_RU dict
    ├── cache.py             # Простой кеш (in-memory или файловый)
    ├── analytics.py         # Аналитика (не используется активно)
    ├── ratelimit.py         # Rate limiting (не используется активно)
    └── subscriptions.py     # Подписки (не используется активно)
```

---

## API эндпоинты (main.py)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Отдаёт `public/index.html` |
| GET | `/health` | Возвращает "ok" |
| GET | `/api/geocode?q=<city>` | Поиск города через Nominatim. Возвращает `[{display, lat, lon, tz_name}]` |
| GET | `/api/horoscope?sign=<slug>&type=day\|week` | Гороскоп. Возвращает `{"text": "..."}` |
| POST | `/api/natal-data` | Натальная карта JSON. Body: `{"birthdate":"DD-MM-YYYY","birthtime":"HH:MM","lat":55.7,"lon":37.6,"tz_name":"Europe/Moscow","name":"Михаил"}` |
| POST | `/api/natal` | Устаревший текстовый отчёт. Возвращает `{"report": "..."}` |
| GET | `/setup` | Регистрирует Telegram webhook |
| POST | `/webhook/<WEBHOOK_SECRET>` | Принимает апдейты от Telegram |

---

## Критически важные патчи (main.py, natal.py)

### pyswisseph >= 2.8 ломает flatlib
В версии 2.8+ `swe.calc_ut()` возвращает `(tuple, retflag)` вместо просто `tuple`.
flatlib ожидает `tuple`. Патч нужен в ОБОИХ файлах:

```python
# В main.py (патч для самого swisseph)
import swisseph as _sw
_orig_calc_ut = _sw.calc_ut
def _compat_calc_ut(jd, planet, *a, **kw):
    r = _orig_calc_ut(jd, planet, *a, **kw)
    return r[0] if isinstance(r[0], (tuple, list)) else r
_sw.calc_ut = _compat_calc_ut
import flatlib.ephem.swe as _fswe
_fswe.swisseph.calc_ut = _compat_calc_ut  # патч внутри flatlib тоже

# В services/natal.py (свой патч перед импортом flatlib)
import swisseph as _swe
_orig_calc_ut = _swe.calc_ut
def _compat_calc_ut(jd, planet, *args, **kwargs):
    result = _orig_calc_ut(jd, planet, *args, **kwargs)
    return result[0] if isinstance(result[0], (tuple, list)) else result
_swe.calc_ut = _compat_calc_ut
import flatlib as _fl
_swe.set_ephe_path(_fl.PATH_RES + 'swefiles')  # ОБЯЗАТЕЛЬНО для Flask-контекста
```

### Внешние планеты в flatlib
flatlib не включает Уран/Нептун/Плутон/Хирон по умолчанию — нужно явно передавать:
```python
ALL_OBJECTS = [const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
               const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE,
               const.PLUTO, const.CHIRON, const.NORTH_NODE]
chart = Chart(dt, pos, IDs=ALL_OBJECTS)
```

---

## services/natal.py — что возвращает build_natal_data()

```python
{
  "name": "Михаил",
  "date": "23.07.1986",
  "time": "07:52",
  "location": {"lat": 55.4241, "lon": 37.5547, "tz_offset": "+03:00"},
  "planets": [
    {
      "id": "Sun", "name": "Солнце", "emoji": "☉",
      "sign": "Leo", "sign_ru": "Лев", "sign_emoji": "♌",
      "deg": 0, "min": 1, "sec": 6, "lon": 120.02,
      "retro": False,
      "house": 12,          # номер дома 1–12
      "meaning": "воля, самовыражение, жизненная сила",
      "sign_meaning": "самовыражение и лидерство"
    },
    ... # 12 планет
  ],
  "houses": [
    {"num": 1, "lon": 144.17, "sign": "Leo", "sign_ru": "Лев", "sign_emoji": "♌",
     "deg": 24, "min": 10, "ruler": "Солнце", "meaning": "Личность, внешность..."},
    ... # 12 домов
  ],
  "asc": {"sign": "Leo", "sign_ru": "Лев", "sign_emoji": "♌", "deg": 24, "min": 10, "lon": 144.17},
  "mc":  {"sign": "Taurus", "sign_ru": "Телец", "sign_emoji": "♉", "deg": 8, "min": 31, "lon": 38.52},
  "aspects": [
    {
      "p1": "Солнце", "p1e": "☉", "p2": "Луна", "p2e": "☽",
      "angle": 150, "name": "Квинконс ⚻", "orb": 0.6,
      "nature": "напряжённый"
    },
    ... # 30+ аспектов
  ],
  "elements":   {"fire": 3, "earth": 4, "air": 2, "water": 2},
  "modalities": {"cardinal": 3, "fixed": 4, "mutable": 4},
  "dominant":   {"element": "earth", "element_ru": "Земля", "modality": "fixed", "modality_ru": "Фиксированный"}
}
```

---

## services/parser.py — гороскопы

Пытается скрапить geocult.ru. Если не получается (сервер заблокирован) — генерирует детерминированный текст.

**Знаки (slug):** oven, telec, bliznecy, rak, lev, deva, vesy, skorpion, strelec, kozerog, vodoley, ryby

```python
get_daily_horoscope(sign_slug)   # гороскоп на день
get_weekly_horoscope(sign_slug)  # гороскоп на неделю
```

Fallback-тексты: 7 вариантов на день × 12 знаков, 4 варианта на неделю × 12 знаков.
Выбор детерминированный через `hashlib.md5(f"{date}{sign_slug}")`.

---

## public/index.html — фронтенд (SPA, ~1013 строк)

### Страницы (id):
- `page-home` — главная (кнопки: Гороскоп / Натальная карта)
- `page-signs` — выбор знака зодиака (12 кнопок)
- `page-horo` — просмотр гороскопа (вкладки: день / неделя)
- `page-input` — ввод: **Имя** + дата + время + город рождения
- `page-chart` — натальная карта (вкладки: Карта / Планеты / Дома / Аспекты / Разбор)

### Ключевые JS-функции:
- `showPage(id)` — переключение страниц
- `openHoroscope(sign)` — открыть гороскоп для знака
- `loadHoro(slug, type)` — загрузить гороскоп через API (с кешем `horoCache`)
- `renderAll(d)` — отрендерить все вкладки; ставит заголовок "Имя — натальная карта"
- `renderWheel(d)` — SVG-колесо (зодиак + дома + планеты + аспекты + ASC/MC)
- `renderPlanets(d)` — таблица планет с домом
- `renderHouses(d)` — список 12 домов с планетами внутри
- `renderAspects(d)` — список аспектов (гармоничные / напряжённые)
- `renderInterp(d)` — детальный разбор (geocult-стиль)
- `renderElements(d)` — стихии и модальности

### Вкладка «Разбор» (renderInterp) — структура для каждой планеты:
1. **Роль планеты** — общее описание (PLANET_ROLE)
2. **Планета в знаке** — конкретный текст (SIGN_IN_PLANET: 7 планет × 12 знаков)
3. **Планета в Доме** — конкретный текст (PLANET_IN_HOUSE: 12 планет × 12 домов) ← главное добавление
4. **Аспекты этой планеты** — список с цветовой кодировкой

### Поиск города:
- Автодополнение через `/api/geocode` → Nominatim
- При выборе города сохраняются: `display`, `lat`, `lon`, `tz_name`
- Передаются в `/api/natal-data` для корректного расчёта времени

### SVG-колесо:
- 0° Овна = верхняя точка (lonToAngle преобразует lon → угол SVG)
- Планеты на радиусе RP=112, зодиак RSI–RO, аспекты внутри RI=85
- Номера домов внутри круга (radius 67)
- Аспекты: цвет по типу (ASP_COL), opacity 0.4 гармоничные, 0.22 напряжённые
- Линии ASC (жёлтая #fbbf24) и MC (зелёная #34d399)

---

## Telegram бот (main.py)

- Вебхук: `POST /webhook/<WEBHOOK_SECRET>`
- `/start` → сообщение с предупреждением о первом запуске + inline-кнопка `web_app: {url: MINI_APP_URL}`
- Регистрация вебхука: открыть `<APP_URL>/setup` в браузере

---

## Keep-alive (main.py)

Фоновый поток пингует `/health` каждые 10 минут — предотвращает засыпание Render free tier.
```python
threading.Thread(target=_keepalive, daemon=True).start()
```

---

## Переменные окружения (Render Dashboard)

| Переменная | Значение |
|------------|----------|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `WEBHOOK_SECRET` | astrosecret123 (или другой) |
| `MINI_APP_URL` | https://astroapp-gk0z.onrender.com |
| `DEFAULT_LAT` | 55.7558 (Москва) |
| `DEFAULT_LON` | 37.6176 (Москва) |
| `DEFAULT_TZ_OFFSET` | +03:00 |

---

## Git-проблемы (Windows NTFS)

При работе из Linux sandbox → Windows NTFS возникают lock-файлы.
**Пользователь должен запускать git-команды сам в PowerShell.**

```powershell
cd "D:\cursor обучение\.cursor\astro_app"
Remove-Item ".git\index.lock" -Force -ErrorAction SilentlyContinue
Remove-Item ".git\HEAD.lock" -Force -ErrorAction SilentlyContinue
git add .
git commit -m "feat: описание"
git push origin main
```

Запись файлов с кириллицей через ассистента — только через `python3` скрипт (не heredoc).

---

## Зависимости (requirements.txt)

```
flask==3.0.3
gunicorn==22.0.0
requests==2.32.3
beautifulsoup4==4.12.3
flatlib==0.2.1
pyswisseph==2.10.3.2
python-dotenv==1.0.1
timezonefinder
```

⚠️ aiogram/aiohttp НЕ в requirements.txt (не работают на Python 3.12 через pip).
⚠️ pyswisseph==2.10.3.2 требует патча совместимости (см. выше).

---

## Render.com — особенности

- Бесплатный тариф: сервер засыпает после 15 минут неактивности, первый запрос ~30 сек
- Keep-alive поток внутри приложения решает эту проблему частично
- Автодеплой: push в main → Render пересобирает
- Build command: `pip install -r requirements.txt`
- Start command: из Procfile — `gunicorn main:app`

---

## История ключевых изменений

| Коммит | Что сделано |
|--------|-------------|
| `8e75ae0` | Геокодинг городов, реальный часовой пояс, keep-alive поток, предупреждение в /start |
| `334ed6a` | Экран гороскопа + детальные интерпретации натальной карты |
| `933c4a5` | SVG-колесо, 12 планет, аспекты, интерпретации |
| `07b4ff9` | Полная натальная карта: 12 планет, аспекты, ретроград, /api/natal-data |
| последний | Поле имени, PLANET_IN_HOUSE (144 текста), аспекты по планете в разборе |
