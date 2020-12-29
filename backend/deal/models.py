from django.db import models


class Users(models.Model):
    username = models.CharField(max_length=30)


class Gem(models.Model):
    title = models.CharField(max_length=30)


class Deal(models.Model):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='deals')
    item = models.ForeignKey(Gem, on_delete=models.CASCADE, related_name='deals')
    total = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
