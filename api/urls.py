from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='api-article')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', obtain_auth_token, name='api_token'),
]