# Generated by Django 3.0.2 on 2020-01-19 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('related_object_sample', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reporter',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
