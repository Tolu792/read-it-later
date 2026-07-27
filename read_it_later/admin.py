from django.contrib import admin
from .models import Tag, Article

# Register your models here.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'reading_time_minutes', 'created_at')
    list_filter = ('status', 'tags')
    search_fields = ('title', 'url', 'description')
    filter_horizontal = ('tags',)
