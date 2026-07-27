from django.urls import path
from  . import views
urlpatterns = [
    path('', views.article_list, name='list_articles'),
    path('accounts/signup/', views.signup, name='signup'),
    path('add/', views.add_article, name='add_article'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
]