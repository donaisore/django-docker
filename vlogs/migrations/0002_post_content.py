# Generated by Django 3.0.2 on 2020-02-13 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vlogs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
