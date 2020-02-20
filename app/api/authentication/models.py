from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as localize
from django.conf import settings
from datetime import timedelta

# Create your models here.

class AppUser(AbstractUser):
    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ExpiringToken(Token):
    refreshed = models.DateTimeField(localize('Refreshed'), auto_now_add=True)

    def refresh(self):
        self.refreshed = timezone.now()
        self.save(update_fields=['refreshed'])

    @property
    def timedout(self):
        now = timezone.now()
        timeout_interval = settings.TOKEN_SETTINGS.get('IDLE_TOKEN_LIFESPAN', timedelta(hours=2))
        if now - self.refreshed > timeout_interval:
            return True 
        return False

    @property
    def expired(self):
        now = timezone.now()
        expiry_interval = settings.TOKEN_SETTINGS.get('EXPIRING_TOKEN_LIFESPAN', timedelta(days=30))
        if self.created < now - expiry_interval:
            return True
        return False

    class Meta:
        verbose_name = 'Expiring Token'
        verbose_name_plural = 'Expiring Tokens'
