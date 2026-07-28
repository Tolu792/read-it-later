from rest_framework import serializers

from read_it_later.models import Article, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'url', 'title', 'description', 'image_url',
            'content_text', 'reading_time_minutes', 'status',
            'tags', 'created_at',
        ]
        read_only_fields = [
            'title', 'description', 'image_url',
            'content_text', 'reading_time_minutes', 'created_at',
        ]