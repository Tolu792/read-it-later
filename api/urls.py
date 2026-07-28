from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import ArticleViewSet, RevokeTokenView

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='api-article')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', obtain_auth_token, name='api_token'),
    path('token/revoke/', RevokeTokenView.as_view(), name='api_token_revoke')
]

urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
