from django.urls import path
from  . import views
urlpatterns = [
    path('', views.article_list, name='list_articles'),
    path('accounts/signup/', views.signup, name='signup'),
    path('add/', views.add_article, name='add_article'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('articles/<int:pk>/status/<str:status>/', views.article_set_status, name='article_set_status'),
    path('articles/<int:pk>/tags/', views.article_update_tags, name='article_update_tags'),
]