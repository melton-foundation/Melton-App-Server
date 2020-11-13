from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token

from authentication.forms import AppUserChangeForm, AppUserCreationForm
from authentication.models import (
    AppUser,
    ExpiringToken,
    PhoneNumber,
    Profile,
    SocialMediaAccount,
    SustainableDevelopmentGoal,
)


class AppUserAdmin(UserAdmin):
    add_form = AppUserCreationForm
    form = AppUserChangeForm
    model = AppUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created", "refreshed")
    fields = ("user",)
    ordering = ("-created",)


class PhoneNumberInline(admin.StackedInline):
    extra = 1
    model = PhoneNumber


class SocialMediaAccountInline(admin.StackedInline):
    extra = 1
    model = SocialMediaAccount


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    filter_horizontal = ("sdgs",)
    list_display = ("user", "name", "campus", "batch", "points")
    actions = ["add_points", "reduce_points"]
    inlines = [PhoneNumberInline, SocialMediaAccountInline]
    list_editable = ("points",)
    change_list_template = "admin/profile_change_list.html"
    search_fields = ("user__email", "name", "campus")

    def add_points(self, request, queryset):
        points = request.POST.get("points", 0)
        for user in queryset:
            user.points += int(points)
            user.save()
        self.message_user(
            request,
            f"{points} Points were added successfully to all selected accounts.",
        )

    def reduce_points(self, request, queryset):
        points = request.POST.get("points", 0)
        for user in queryset:
            user.points -= int(points)
            user.save()
        self.message_user(
            request, f"{points} Points were removed from all selected accounts."
        )


admin.site.site_header = settings.SITE_HEADER
admin.site.site_title = settings.SITE_TITLE
admin.site.unregister(Token)
admin.site.register(ExpiringToken, TokenAdmin)
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SustainableDevelopmentGoal)
