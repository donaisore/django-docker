from django.db import models
from django.contrib.auth.models import User


class LogicalDeletionManager(models.Manager):
    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(deleted_at__isnull=True)

class Blog(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, default=None)

    objects = LogicalDeletionManager()
    all_objects = models.Manager()


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
