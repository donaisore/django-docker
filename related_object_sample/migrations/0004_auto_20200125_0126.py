# Generated by Django 3.0.2 on 2020-01-25 01:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('related_object_sample', '0003_auto_20200121_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='related_object_sample.Reporter'),
        ),
    ]
