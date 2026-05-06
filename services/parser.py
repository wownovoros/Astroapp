import hashlib
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup

from services.cache import get_cache, set_cache
from services.zodiac import SIGN_RU

BASE_URL = "https://geocult.ru"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── Scraper ───────────────────────────────────────────────────────────────────

def _extract_text(html: str, max_paragraphs: int = 10) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="entry-content")
    if not content:
        return None
    paragraphs = [p.get_text(" ", strip=True) for p in content.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 30]
    return "\n\n".join(paragraphs[:max_paragraphs])[:3500] if paragraphs else None


def _fetch(url: str, ttl: int = 1800) -> Optional[str]:
    cached = get_cache(url)
    if cached:
        return cached
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        text = _extract_text(response.text)
        if text:
            set_cache(url, text, ttl=ttl)
        return text
    except Exception:
        return None

# ── Fallback generator ────────────────────────────────────────────────────────

_DAY_PHRASES = [
    "Сегодня звёзды благоволят вашим начинаниям. Прислушайтесь к интуиции — она не подведёт. "
    "Хороший день для общения и новых знакомств. Избегайте импульсивных решений в финансах.",

    "День принесёт неожиданные возможности. Будьте открыты переменам и не цепляйтесь за старое. "
    "В личных отношениях важна честность. Вечер подходит для отдыха и восстановления сил.",

    "Энергия дня направлена на профессиональный рост. Ваши усилия будут замечены. "
    "Не откладывайте важные разговоры — время выбрано удачно. Берегите здоровье.",

    "Сегодня акцент на внутреннем мире. Уделите время размышлениям и планированию. "
    "Близкие нуждаются в вашем внимании. Небольшие радости принесут большое удовольствие.",

    "Активный и продуктивный день. Беритесь за сложные задачи — сейчас вы в ресурсе. "
    "Финансовые вопросы решаются в вашу пользу. Доверяйте своему чутью.",

    "День требует гибкости и терпения. Не все пойдёт по плану, но это открывает новые пути. "
    "Поддержка друзей окажется неожиданно ценной. Вечер — время для себя.",

    "Звёзды указывают на важный выбор. Взвесьте все варианты, не торопитесь. "
    "Творческая энергия на подъёме — используйте её. Отношения требуют заботы и тепла.",
]

_WEEK_PHRASES = [
    "Неделя открывает новую страницу в вашей жизни. В начале недели возможны неожиданные новости, "
    "которые потребуют быстрой реакции. Середина недели — идеальное время для переговоров и решения "
    "финансовых вопросов. К выходным накопится усталость, позвольте себе отдохнуть. "
    "Отношения с близкими потребуют внимания и терпения.",

    "Эта неделя насыщена событиями. Профессиональные дела идут в гору — покажите себя с лучшей стороны. "
    "Во вторник-среду возможно столкновение интересов: держите эмоции под контролем. "
    "Четверг и пятница принесут приятные сюрпризы. Выходные посвятите семье и восстановлению сил.",

    "Неделя требует чёткого планирования. Начните с расстановки приоритетов. "
    "Финансово неделя нейтральная — крупных трат лучше избегать. "
    "В среду-четверг возможно важное знакомство. "
    "Конец недели принесёт гармонию в личной жизни и приятное общение.",

    "Динамичная и насыщенная неделя. В понедельник заряд энергии высок — используйте его для старта "
    "новых проектов. Середина недели может принести некоторые трудности, но они преодолимы. "
    "К пятнице ситуация выровняется. Выходные подходят для отдыха на природе и творчества.",
]

_SIGN_TRAITS = {
    "oven":     "Огненная энергия Овна",
    "telec":    "Земная устойчивость Тельца",
    "bliznecy": "Воздушная гибкость Близнецов",
    "rak":      "Водная глубина Рака",
    "lev":      "Солнечная сила Льва",
    "deva":     "Земная точность Девы",
    "vesy":     "Воздушная гармония Весов",
    "skorpion": "Водная мощь Скорпиона",
    "strelec":  "Огненная свобода Стрельца",
    "kozerog":  "Земная мудрость Козерога",
    "vodoley":  "Воздушное новаторство Водолея",
    "ryby":     "Водная интуиция Рыб",
}


def _generate_day(sign_slug: str) -> str:
    today = date.today().isoformat()
    idx = int(hashlib.md5(f"{today}{sign_slug}".encode()).hexdigest(), 16) % len(_DAY_PHRASES)
    trait = _SIGN_TRAITS.get(sign_slug, "Особая энергия знака")
    sign_ru = SIGN_RU.get(sign_slug, sign_slug)
    return f"Гороскоп на сегодня для знака {sign_ru}:\n\n{trait} сегодня особенно ощутима.\n\n{_DAY_PHRASES[idx]}"


def _generate_week(sign_slug: str) -> str:
    today = date.today()
    week_num = today.isocalendar()[1]
    idx = int(hashlib.md5(f"{today.year}{week_num}{sign_slug}".encode()).hexdigest(), 16) % len(_WEEK_PHRASES)
    trait = _SIGN_TRAITS.get(sign_slug, "Особая энергия знака")
    sign_ru = SIGN_RU.get(sign_slug, sign_slug)
    return f"Гороскоп на неделю для знака {sign_ru}:\n\n{trait} задаёт тон всей неделе.\n\n{_WEEK_PHRASES[idx]}"

# ── Public API ────────────────────────────────────────────────────────────────

def get_daily_horoscope(sign_slug: str) -> str:
    url = f"{BASE_URL}/goroskop-na-segodnya-{sign_slug}"
    text = _fetch(url, ttl=3600)
    return text if text else _generate_day(sign_slug)


def get_weekly_horoscope(sign_slug: str) -> str:
    url = f"{BASE_URL}/goroskop-na-nedelyu-{sign_slug}"
    text = _fetch(url, ttl=6 * 3600)
    return text if text else _generate_week(sign_slug)
