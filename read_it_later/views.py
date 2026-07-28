import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import Http404

from .forms import AddArticleForm
from .models import Article, Tag
from .services import fetch_article_metadata


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("list_articles")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


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


@login_required
@require_POST
def article_set_status(request, pk, status):
    if status not in Article.Status.values:
        raise Http404

    article = get_object_or_404(Article, pk=pk, user=request.user)
    article.status = status
    article.save(update_fields=["status"])
    messages.success(request, f"Marked as {article.get_status_display()}.")
    return redirect("list_articles")
