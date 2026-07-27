import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import AddArticleForm
from .models import Article, Tag
from .services import fetch_article_metadata


@login_required
def add_article(request):
    if request.method == "POST":
        form = AddArticleForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["url"]
            try:
                metadata = fetch_article_metadata(url)
            except requests.RequestException:
                messages.error(request, "Couldn't fetch that URL. Check the link and try again.")
            else:
                try:
                    Article.objects.create(user=request.user, url=url, **metadata)
                except IntegrityError:
                    messages.warning(request, "You've already saved that article.")
                else:
                    messages.success(request, "Article saved.")
                    return redirect("list_articles")
    else:
        form = AddArticleForm()

    return render(request, "read_it_later/add_article.html", {"form": form})


@login_required
def article_list(request):
    articles = Article.objects.filter(user=request.user)

    status = request.GET.get("status")
    if status:
        articles = articles.filter(status=status)

    tag_slug = request.GET.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)


    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(url__icontains=query)
        )

    return render(request, 'read_it_later/article_list.html', {
        'articles': articles,
        'tags': Tag.objects.all(),
        'current_status': status or '',
        'current_tag': tag_slug or '',
        'query': query or '',
    })


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, user=request.user)
    return render(request, "read_it_later/article_detail.html", {"article": article})


@login_required
@require_POST
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk, user=request.user)
    article.delete()
    messages.success(request, "Article deleted.")
    return redirect("list_articles")
