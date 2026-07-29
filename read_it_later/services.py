import requests
from bs4 import BeautifulSoup
import trafilatura
from django.db.models import Q


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


def _strip_html(text):
    if not text:
        return text
    return BeautifulSoup(text, "lxml").get_text(separator=" ", strip=True)


def fetch_article_metadata(url: str) -> dict:
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ReadItLaterBot/1.0)"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title = _strip_html(_get_meta(soup, "og:title") or _text(soup.title))
    description = _strip_html(_get_meta(soup, "og:description") or _get_meta(soup, "description"))
    image_url = _get_meta(soup, "og:image")

    content_text = trafilatura.extract(response.text, url=url) or ""
    word_count = len(content_text.split())
    reading_time_minutes = max(1, round(word_count / 200))

    return {
        "title": title or "",
        "description": description or "",
        "image_url": image_url or "",
        "content_text": content_text,
        "reading_time_minutes": reading_time_minutes,
    }


def filter_articles(articles, params):
    status = params.get('status')
    if status:
        articles = articles.filter(status=status)

    tag_slug = params.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)


    query = params.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(url__icontains=query)
        )

    return articles
