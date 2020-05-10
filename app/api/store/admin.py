from django.contrib import admin
from store.models import StoreItem, Transaction


class StoreItemAdmin(admin.ModelAdmin):
    model = StoreItem
    list_display = ('name', 'points', 'active')

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('user', 'transaction_date', 'item', 'points', 'transaction_type')

admin.site.register(StoreItem, StoreItemAdmin)
admin.site.register(Transaction, TransactionAdmin)