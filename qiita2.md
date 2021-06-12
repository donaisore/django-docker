## はじめに

タイトルの通り Django を使っていて

「論理削除でも、関連テーブルのレコードを削除したい！どうにかやれないかなぁ？」という内容です。

Django の論理削除の実装については色々な記事があるので割愛します。

サンプルとして、以下のように `Blog, Post, Comment` の三つの Model を用意し、全てを論理削除としました。

```python
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
    content = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Comment(LogicalDeletionModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
```

この上で、`on_delete=models.CASCADE` の場合、紐づくレコードが全て削除されるように変更を加えていきます。

**before**

```
>>> blog = Blog.objects.create(name='blog')
>>> post = blog.post_set.create(title='post')
>>> comment = post.comment_set.create(content='comment')
>>> post.delete()
>>> Post.objects.all()
<LogicalDeletionQuerySet []>
>>> Comment.objects.all()
<QuerySet [<Comment: Comment object (1)>]>
```

## やること

1. `model_instance.delete()` で `CASCADE DELETE`
2. `model_queryset.delete()` で `CASCADE DELETE`

## 1. `model_instance.delete()` で `CASCADE DELETE`

まずは `LogicalDeletionModel` の `delete()` に修正を加えます。

**before**

```python
class LogicalDeletionModel(models.Model):
    def delete(self, **kwargs):
        now = timezone.now()
        self.deleted_at = now
        self.save()
```

これを実現するためには

- 削除されたインスタンスのモデルが ForeignKey として設定されているモデルの一覧
- ForeignKey のフィールド名
- ForeignKey の on_delete

の全てが取得出来る必要があります。

それが完了すれば
`Model.objects.filter(field_name=deleted_instance).delete()`
とすることで実装が完了します。

まず
削除されたインスタンスのモデルが ForeignKey として設定されているモデルの一覧は
`instance._meta.related_objects` にアクセスすることで取得出来ました。

```python
>>> blog._meta.related_objects
(<ManyToOneRel: blogs.post>,)
>>> post._meta.related_objects
(<ManyToOneRel: blogs.comment>,)
>>> comment._meta.related_objects
()
```

次にそのクラスを取得します。
`instance._meta.related_objects` で取得出来たオブジェクトの
`related_model` で取得出来ました。

```
>>> blog._meta.related_objects[0].related_model
<class 'blogs.models.Post'>
```

フィールド名は `related_object` の `field.name`で取得出来ました。

```python
>>> blog._meta.related_objects[0].field.name
'blog'
```

ForeignKey の on_delete は `related_object` の `on_delete`で取得できました。

```python
>>> blog._meta.related_objects[0].on_delete
<function CASCADE at 0x7f8be5cbb830>
```

これらを使って `model_instance.delete()` での `CASCADE DELETE` を実装することができました。

**after**

```python
class LogicalDeletionModel(models.Model):
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
```

```python
>>> blog = Blog.objects.create(name='blog')
>>> post = blog.post_set.create(title='post')
>>> comment1 = post.comment_set.create(content='comment1')
>>> comment2 = post.comment_set.create(content='comment2')
>>> post.delete()
>>> Post.objects.all()
<LogicalDeletionQuerySet []>
>>> Comment.objects.all()
<QuerySet []>
```

## 2. `model_queryset.delete()` で `CASCADE DELETE`

こちらは

- 削除された queryset のモデル
- 削除された queryset のモデルが ForeignKey として設定されているモデルの一覧
- ForeignKey のフィールド名
- ForeignKey の on_delete

を取得することで実装できます。

削除された queryset のモデルは `queryset.model` で取得できます。

```python
>>> blogs = Blog.objects.all()
>>> blogs.model
<class 'blogs.models.Blog'>
```

ここからは 1 の `instance._meta` を `model._meta` に置き換えるだけで全く同じです。

これを踏まえて `LogicalDeletionQuerySet` の delete の実装を更新します。

**before**

```python
class LogicalDeletionQuerySet(models.QuerySet):
    def delete(self):
        now = timezone.now()
        return super().update(**{'deleted_at': now})

```

**after**

```python
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
        return = super().update(**{'deleted_at': now})
```

では試してみます。

```python
>>> blog = Blog.objects.create(name='blog')
>>> post = blog.post_set.create(title='post')
>>> comment = post.comment_set.create(content='comment')
>>> Blog.objects.all().delete()
1
>>> Blog.objects.all(), Post.objects.all(), Comment.objects.all()
(<LogicalDeletionQuerySet []>, <LogicalDeletionQuerySet []>, <LogicalDeletionQuerySet []>)
>>> Blog.all_objects.all(), Post.all_objects.all(), Comment.all_objects.all()
(<QuerySet [<Blog: Blog object (1)>]>, <QuerySet [<Post: Post object (1)>]>, <QuerySet [<Comment: Comment object (1)>]>)
```

うまくいきました。

## おわり

少し強引に実装してしまったかな？と思ってはいますが

> 「論理削除でも、関連テーブルのレコードを削除したい！」

を実現することができました。

より良い方法があれば是非教えてください！

ありがとうございました！！
