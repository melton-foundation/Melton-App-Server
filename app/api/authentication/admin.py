from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from rest_framework.authtoken.models import Token
from authentication.models import AppUser, ExpiringToken
from authentication.forms import AppUserCreationForm, AppUserChangeForm

class AppUserAdmin(UserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created', 'refreshed')
    fields = ('user',)
    ordering = ('-created',)

admin.site.unregister(Token)
admin.site.register(ExpiringToken, TokenAdmin)
admin.site.register(AppUser, AppUserAdmin)
