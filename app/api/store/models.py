from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import AppUser


class TransactionType(models.TextChoices):
    BUY = 'BUY', _('Buy Item')
    SELL = 'SELL', _('Sell Item')


class StoreItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    preview_image = models.ImageField(upload_to='store-items', blank=True)
    description = models.TextField(max_length=500)
    points = models.PositiveIntegerField(blank=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'


class TransactionManager(models.Manager):
    def buy_item(self, user, item):
        transaction = Transaction(user = user, item = item, points = item.points, transaction_type = TransactionType.BUY)
        transaction.save()
        user.profile.deduct_points(item.points)
        return transaction

    def is_purchased(self, user, item):
        transaction = self.filter(user = user).filter(item = item)
        return bool(transaction)


class Transaction(models.Model):

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(StoreItem, on_delete=models.DO_NOTHING)
    # although this data is already part of item model, 
    # adding it here so that we have some reference to points even though item is deleted for some reason
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices)

    objects = TransactionManager()

    def __str__(self):
        if (self.transaction_type == TransactionType.BUY):
            display = f'{self.item} was bought by {self.user} on {self.transaction_date}'
        else:
            display = f'{self.item} was sold by {self.user} on {self.transaction_date}'
        
        return display

