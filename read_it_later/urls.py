from django.urls import path
from  . import views
urlpatterns = [
    path('add/', views.add_article, name='add_article'),
    path('articles/', views.article_list, name='list_articles')
]