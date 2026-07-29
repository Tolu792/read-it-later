import requests
from celery import shared_task

from .models import Article
from .services import fetch_article_metadata


@shared_task
def fetch_and_populate_article(article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return

    try:
        metadata = fetch_article_metadata(article.url)
    except requests.RequestException:
        article.fetch_failed = True
        article.save(update_fields=["fetch_failed"])
        return

    for field, value in metadata.items():
        setattr(article, field, value)
    article.save()
