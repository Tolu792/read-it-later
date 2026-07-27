import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import AddArticleForm
from .models import Article
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
                    return redirect("add_article")
    else:
        form = AddArticleForm()

    return render(request, "read_it_later/add_article.html", {"form": form})
