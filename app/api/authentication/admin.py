from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token

from authentication.forms import AppUserChangeForm, AppUserCreationForm
from authentication.models import AppUser, ExpiringToken, PhoneNumber, Profile


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
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created', 'refreshed')
    fields = ('user',)
    ordering = ('-created',)


class PhoneNumberInline(admin.StackedInline):
    extra = 1
    model = PhoneNumber


class ProfileAdmin(admin.ModelAdmin):
    model = Profile

    inlines = [
        PhoneNumberInline
    ]


admin.site.unregister(Token)
admin.site.register(ExpiringToken, TokenAdmin)
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Profile, ProfileAdmin)
