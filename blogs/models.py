from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone


class LogicalDeletionQuerySet(models.QuerySet):
    def delete(self):
        queryset_model = self.model
        related_objects = queryset_model._meta.related_objects
        for related_object in related_objects:
            if related_object.on_delete == models.CASCADE:
                related_model = related_object.related_model
                related_field_name = f'{related_object.field.name}__in'
                related_model.objects.filter(**{related_field_name: self}).delete()

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
        related_objects = self._meta.related_objects
        for related_object in related_objects:
            if related_object.on_delete == models.CASCADE:
                related_model = related_object.related_model
                related_field_name = related_object.field.name
                related_model.objects.filter(**{related_field_name: self}).delete()


class Blog(LogicalDeletionModel):
    name = models.CharField(max_length=255)


class Post(LogicalDeletionModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Comment(LogicalDeletionModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
