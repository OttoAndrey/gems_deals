from django.db import models
from django.db.models import Sum


class UsersQuerySet(models.QuerySet):
    def most_spends(self):
        most_spends_users = Users.objects.annotate(total_sum=Sum('deals__total')).order_by('-total_sum')
        return most_spends_users


class Users(models.Model):
    objects = UsersQuerySet.as_manager()
    username = models.CharField(max_length=30)


class Gem(models.Model):
    title = models.CharField(max_length=30)


class Deal(models.Model):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='deals')
    item = models.ForeignKey(Gem, on_delete=models.CASCADE, related_name='deals')
    total = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
