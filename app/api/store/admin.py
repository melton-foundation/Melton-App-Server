from django.contrib import admin
from store.models import StoreItem, Transaction, TransactionType
from django.core.exceptions import ValidationError



class StoreItemAdmin(admin.ModelAdmin):
    model = StoreItem
    list_display = ('name', 'points', 'active')

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('user', 'transaction_date', 'item', 'points', 'transaction_type')
    exclude = ('points',)

    def save_model(self, request, transaction, form, change):
        if not change and transaction.transaction_type == TransactionType.BUY:
            self.model.objects.buy_item(transaction.user, transaction.item)
        elif transaction.transaction_type == TransactionType.BUY:
            super().save_model(request, transaction, form, change)

admin.site.register(StoreItem, StoreItemAdmin)
admin.site.register(Transaction, TransactionAdmin)