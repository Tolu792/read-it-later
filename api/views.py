from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from read_it_later.models import Article
from read_it_later.services import filter_articles, get_or_create_tags
from read_it_later.tasks import fetch_and_populate_article
from .serializers import ArticleSerializer

from django.db import IntegrityError


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        articles = Article.objects.filter(user=self.request.user)
        return filter_articles(articles, self.request.query_params)

    def perform_create(self, serializer):
        tag_names = serializer.validated_data.pop('tag_names', [])
        try:
            article = serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'url': "You have already saved that article."})
        article.tags.set(get_or_create_tags(tag_names))
        fetch_and_populate_article.delay(article.id)

    def perform_update(self, serializer):
        if 'url' in serializer.validated_data:
            raise ValidationError({'url': "URL cannot be changed after creation."})
        tag_names = serializer.validated_data.pop('tag_names', None)
        article = serializer.save()
        if tag_names is not None:
            article.tags.set(get_or_create_tags(tag_names))


class RevokeTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=204)
