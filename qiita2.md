## これは何

タイトルの通り
`論理削除でも、関連テーブルのレコードを削除したい！`

どうにかやれないかなぁという内容です。

前もって以下のように `LogicalDeletionModel` を実装しました。

Django で以下のような Model を実装した時に

```python
from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

```

Blog のレコードを削除すると、削除したレコードに紐づいている
Post のレコードも削除してくれます。

(例)

```python
>>> user = User.objects.create_user('user', 'user@example.com', 'user')
>>> blog = user.blog_set.create(name='blog')
>>> post = blog.post_set.create(title='post')
>>> Blog.objects.all(), Post.objects.all()
(<QuerySet [<Blog: Blog object (1)>]>, <QuerySet [<Post: Post object (1)>]>)
>>> blog.delete()
(2, {'blogs.Post': 1, 'blogs.Blog': 1})
>>> Blog.objects.all(), Post.objects.all()
(<QuerySet []>, <QuerySet []>)
```

このようにいい感じに関連するレコードを一括で削除してくれる実装が出来ないものか考えてみました。

また `models.ForeignKey()` の `on_delete`に渡せるものには

- models.CASCADE
- models.PROTECT
- models.RESTRICT
- models.SET(value)
- models.SET_NULL
- models.SET_DEFAULT
- models.DO_NOTHING

がありますが、ここでは `CASCADE` についてのみ考慮します！

[django/GitHub](https://github.com/django/django/blob/main/django/db/models/deletion.py#L23-L67)

## 目次(論理削除の実装でやりたいことの整理)

1. `deleted_at` カラムを持ちたい
2. `Model.objects.all()` で削除されたレコードが含まれない状態で取得したい
3. `model_instance.delete()` で `deleted_at` に現在時刻を入れる
4. `model_queryset.delete()` で `deleted_at` に現在時刻を入れる
5. `model_instance.delete()` で 関連するレコードを削除する
6. `model_queryset.delete()` で 関連するレコードを削除する
7. 1~4 の内容を、継承すれば論理削除の実装が終了するクラスとして用意したい

では一つずつ実装していきます！
BlogModel に実装していきます
