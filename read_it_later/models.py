from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = "Tag"
        managed = True


class Article(models.Model):
    class Status(models.TextChoices):
        UNREAD = 'Unread'
        READ = 'Read'
        ARCHIVED = 'Archived'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    url = models.URLField(max_length=2000)
    image_url = models.URLField(max_length=2000, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=300, blank=True)
    content_text = models.TextField(blank=True)
    reading_time_minutes = models.PositiveIntegerField(default=0)
    fetch_failed = models.BooleanField(default=False)
    status = models.CharField(choices=Status.choices, default=Status.UNREAD)
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Article"
        managed = True
        unique_together = ('user', 'url')
        ordering = ['-created_at']
