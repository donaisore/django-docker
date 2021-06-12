## これは何

タイトルの通り
`論理削除でも、関連テーブルのレコードを削除したい！`

どうにかやれないかなぁという内容です。

CASCADE delete のことを書こうと思っていたにも関わらず、論理削除の実装から書いていたら長くなってしまいました。
適当に興味のあるところだけ読み飛ばしていただけると助かります :pray:

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

## 1. `deleted_at` カラムを持ちたい

ここは `deleted_at` カラムを持つだけなので、簡単です。

**Before**

```python
class Blog(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

**After**

```python
class Blog(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, default=None)
```

`Blog.objects.filter(deleted_at__isnull=False)` で削除済みのレコードが含まれない queryset が取得できるようになりました。

## 2. `Model.objects.all()` で削除されたレコードが含まれない状態で取得したい

Blog のデータを取得するときに毎回 `.filter(deleted_at__isnull=False)` を書くのは現実的ではありません。

- filter を書き忘れてしまった！
- いちいち書くのが面倒という問題があります。

こんな時には `Manager` を使います。

[参考]

- [Django ドキュメント/クエリを作成する/オブジェクトを取得する](https://docs.djangoproject.com/ja/3.2/topics/db/queries/#retrieving-objects)
- [Django ドキュメント/マネージャー](https://docs.djangoproject.com/ja/3.2/topics/db/managers/)

↑ にも書いてあるように、

> `Manager.get_queryset()`メソッドをオーバーライドすることで、 `Manager`のベース`QuerySet`を上書きできます。

では、CustomManager として `LogicalDeletionManager` を実装します。

```python
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
```

削除されているものも含めて取得したいケースがあると思うので、 `all_objects` にデフォルトの `models.Manager()` を指定しています。

ではどうなるか試してみます。

```python
>>> Blog.objects.all()
<QuerySet [<Blog: Blog object (1)>, <Blog: Blog object (2)>]>
>>> first_blog = Blog.objects.first()
>>> first_blog.deleted_at = timezone.now()
>>> first_blog.save()
>>> Blog.objects.all()
<QuerySet [<Blog: Blog object (2)>]>
>>> user.blog_set.all()
<QuerySet [<Blog: Blog object (2)>]>
>>> Blog.all_objects.all()
<QuerySet [<Blog: Blog object (1)>, <Blog: Blog object (2)>]>
```

このように、論理削除されたレコードを含まない queryset を取得することが出来ました。

## 3. `model_instance.delete()` で `deleted_at` に現在時刻を入れる

2 の最後で書いたように、このままでは `deleted_at` を埋めるために、 save() をよぶ必要があります。

**before**

```python
>>> first_blog = Blog.objects.first()
>>> first_blog.deleted_at = timezone.now()
>>> first_blog.save()
```

本来は delete() で `deleted-at` に現在時刻が入るようになって欲しいです。

↓ 目指す形

```python
>>> first_blog = Blog.objects.first()
>>> first_blog.delete()
```

このために
BlogModel の delete メソッドをオーバーライドします。

```python
from django.utils import timezone

class Blog(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, default=None)

    objects = LogicalDeletionManager()
    all_objects = models.Manager()

    def delete(self, **kwargs):
        now = timezone.now()
        self.deleted_at = now
        self.save()
```

実装が完了しました。
では試してみます！

```python
>>> user = User.objects.create_user('user', 'user@example.com', 'user')
>>> blog1 = user.blog_set.create(name='blog1')
>>> blog2 = user.blog_set.create(name='blog2')
>>> Blog.objects.all()
<QuerySet [<Blog: Blog object (1)>, <Blog: Blog object (2)>]>
>>> blog2.delete()
>>> Blog.objects.all()
<QuerySet [<Blog: Blog object (1)>]>
>>> blog2.deleted_at
datetime.datetime(2021, 6, 12, 7, 18, 54, 419027, tzinfo=<UTC>)
```

完了です！

## 4. `model_queryset.delete()` で `deleted_at` に現在時刻を入れる

## 5. `model_instance.delete()` で 関連するレコードを削除する

## 6. `model_queryset.delete()` で 関連するレコードを削除する

## 7. 1~4 の内容を、継承すれば論理削除の実装が終了するクラスとして用意したい
