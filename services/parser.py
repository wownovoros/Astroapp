from typing import Optional

import requests
from bs4 import BeautifulSoup

from services.cache import get_cache, set_cache
from services.zodiac import SIGN_RU

BASE_URL = "https://geocult.ru"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AstroAppBot/1.0)"}


def _extract_text(html: str, max_paragraphs: int = 10) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="entry-content")
    if not content:
        return None
    paragraphs = [p.get_text(" ", strip=True) for p in content.find_all("p")]
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return None
    return "\n\n".join(paragraphs[:max_paragraphs])[:3500]


def _fetch(url: str, ttl: int = 1800) -> Optional[str]:
    cached = get_cache(url)
    if cached:
        return cached
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        return None
    text = _extract_text(response.text)
    if text:
        set_cache(url, text, ttl=ttl)
    return text


def get_daily_horoscope(sign_slug: str) -> str:
    url = f"{BASE_URL}/goroskop-na-segodnya-{sign_slug}"
    text = _fetch(url, ttl=3600)
    return text or f"Не удалось получить гороскоп на сегодня для знака {SIGN_RU.get(sign_slug, sign_slug)}."


def get_weekly_horoscope(sign_slug: str) -> str:
    url = f"{BASE_URL}/goroskop-na-nedelyu-{sign_slug}"
    text = _fetch(url, ttl=6 * 3600)
    return text or f"Не удалось получить гороскоп на неделю для знака {SIGN_RU.get(sign_slug, sign_slug)}."
