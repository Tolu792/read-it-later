from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from read_it_later.models import Article
from read_it_later.services import fetch_article_metadata, filter_articles
from .serializers import ArticleSerializer

from django.db import IntegrityError
import requests


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        articles = Article.objects.filter(user=self.request.user)
        return filter_articles(articles, self.request.query_params)

    def perform_create(self, serializer):
        url = serializer.validated_data['url']
        try:
            metadata = fetch_article_metadata(url)
        except requests.RequestException:
            raise ValidationError({'url': "Couldn't fetch that URL."})
        try:
            serializer.save(user=self.request.user, **metadata)
        except IntegrityError:
            raise ValidationError({'url': "You have already saved that article."})


class RevokeTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=204)
