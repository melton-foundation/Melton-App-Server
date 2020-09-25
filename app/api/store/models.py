from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import AppUser
from django.core.exceptions import ValidationError


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
    item = models.ForeignKey(StoreItem, on_delete=models.SET_NULL, null=True)
    # although this data is already part of item model, 
    # adding it here so that we have some reference to points even though item is deleted for some reason
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices)

    objects = TransactionManager()

    def clean(self):
        user_points = 0
        if not self.user.profile.points is None:
            user_points = self.user.profile.points

        if self.item.points > user_points:
            raise ValidationError('The user does not have enough points.')
        if (Transaction.objects.is_purchased(self.user, self.item)):
            raise ValidationError('The user has already purchased this item.')
        return super().clean()

    def __str__(self):
        if (self.transaction_type == TransactionType.BUY):
            display = f'{self.item} was bought by {self.user} on {self.transaction_date}'
        else:
            display = f'{self.item} was sold by {self.user} on {self.transaction_date}'
        
        return display

