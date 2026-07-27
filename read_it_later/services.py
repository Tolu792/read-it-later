import requests
from bs4 import BeautifulSoup


def _get_meta(soup, key):
    tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def _text(tag):
    if tag:
        text = tag.get_text(strip=True)
        return text or None
    return None


def fetch_article_metadata(url: str) -> dict:
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ReadItLaterBot/1.0)"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title = _get_meta(soup, "og:title") or _text(soup.title)
    description = _get_meta(soup, "og:description") or _get_meta(soup, "description")
    image_url = _get_meta(soup, "og:image")

    body_text = " ".join(p.get_text() for p in soup.find_all("p"))
    word_count = len(body_text.split())
    reading_time_minutes = max(1, round(word_count / 200))

    return {
        "title": title or "",
        "description": description or "",
        "image_url": image_url or "",
        "content_text": body_text,
        "reading_time_minutes": reading_time_minutes,
    }
