from django.db import models


class Reporter(models.Model):
    name = models.CharField(max_length=255, null=True)


class Article(models.Model):
    title = models.CharField(max_length=255, null=True)
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)


class Topping(models.Model):
    pass


class Pizza(models.Model):
    toppings = models.ManyToManyField(Topping)
