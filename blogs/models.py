from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone


class LogicalDeletionQuerySet(models.QuerySet):
    def delete(self):
        now = timezone.now()
        return super().update(**{'deleted_at': now})


class LogicalDeletionManager(BaseManager.from_queryset(LogicalDeletionQuerySet)):
    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(deleted_at__isnull=True)


class LogicalDeletionModel(models.Model):
    class Meta:
        abstract = True

    deleted_at = models.DateTimeField(null=True, default=None)

    objects = LogicalDeletionManager()
    all_objects = models.Manager()

    def delete(self, **kwargs):
        now = timezone.now()
        self.deleted_at = now
        self.save()


class Blog(LogicalDeletionModel):
    name = models.CharField(max_length=255)


class Post(LogicalDeletionModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
