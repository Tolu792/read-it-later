from django.urls import path
from  . import views
urlpatterns = [
    path('', views.article_list, name='list_articles'),
    path('add/', views.add_article, name='add_article'),
]