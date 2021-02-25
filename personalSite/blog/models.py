from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from martor.models import MartorField


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, primary_key=True)
    tag_description = models.CharField(max_length=255, null=False, blank=True)


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = MartorField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    views = models.IntegerField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class TaggedPost(models.Model):
    post = models.ForeignKey(

        Post, on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE
    )