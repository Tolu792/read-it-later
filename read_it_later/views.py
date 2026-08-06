import json
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import Http404
from rest_framework.authtoken.models import Token

from .forms import AddArticleForm
from .models import Article, Tag
from .services import filter_articles, get_or_create_tags
from .tasks import fetch_and_populate_article


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
                article = Article.objects.create(user=request.user, url=url)
                tag_names = form.cleaned_data['tags'].split(',')
                article.tags.set(get_or_create_tags(tag_names))
            except IntegrityError:
                messages.warning(request, "You've already saved that article.")
            else:
                fetch_and_populate_article.delay(article.id)
                messages.success(request, "Article saved. Fetching details...")
                return redirect("list_articles")
    else:
        form = AddArticleForm()

    return render(request, "read_it_later/add_article.html", {"form": form})


@login_required
def article_list(request):
    articles = filter_articles(Article.objects.filter(user=request.user), request.GET)

    status = request.GET.get("status")
    tag_slug = request.GET.get('tag')
    query = request.GET.get('q')

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


@login_required
@require_POST
def article_update_tags(request, pk):
    article = get_object_or_404(Article, pk=pk, user=request.user)
    tag_names = request.POST.get('tags', '').split(',')
    article.tags.set(get_or_create_tags(tag_names))
    messages.success(request, "Tags updated.")
    return redirect("article_detail", pk=pk)


@login_required
def bookmarklet(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    api_url = request.build_absolute_uri('/api/articles/')

    js_code = (
        "(function(){"
        "var t=%s;var u=%s;"
        "function toast(msg,ok){"
        "var el=document.createElement('div');"
        "el.textContent=msg;"
        "el.style.cssText='position:fixed;top:20px;right:20px;z-index:2147483647;"
        "padding:12px 20px;border-radius:6px;"
        "font:14px/1.4 -apple-system,BlinkMacSystemFont,sans-serif;color:#fff;"
        "background:'+(ok?'#15803d':'#dc2626')+';box-shadow:0 4px 14px rgba(0,0,0,.25);"
        "transition:opacity .4s ease;opacity:1;';"
        "document.body.appendChild(el);"
        "setTimeout(function(){el.style.opacity='0';},2600);"
        "setTimeout(function(){el.remove();},3000);"
        "}"
        "fetch(u,{method:'POST',headers:{'Authorization':'Token '+t,'Content-Type':'application/json'},"
        "body:JSON.stringify({url:window.location.href})})"
        ".then(function(r){return r.json().then(function(d){return{s:r.status,d:d};});})"
        ".then(function(res){if(res.s===201){toast('Saved to Read It Later',true);}"
        "else{toast('Could not save: '+(res.d.url||res.d.detail||JSON.stringify(res.d)),false);}})"
        ".catch(function(e){toast('Network error - could not reach Read It Later',false);});"
        "})();"
    ) % (json.dumps(token.key), json.dumps(api_url))

    return render(request, "read_it_later/bookmarklet.html", {
        "bookmarklet_href": "javascript:" + quote(js_code),
    })
