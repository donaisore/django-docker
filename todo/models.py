from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaskGroup(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Task(BaseModel):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    done_at = models.DateTimeField(null=True)
    group = models.ForeignKey(TaskGroup, null=True, default=None, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title
