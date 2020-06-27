from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

class AppUserManager(UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AppUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), blank=False, unique=True)

    objects = AppUserManager()

    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class ExpiringTokenManager(models.Manager):
    def get_or_create_by_email(self, email):
        try:
            user = AppUser.objects.get(email = email)
            token = self.get_or_create(user = user)
            return token
        except AppUser.DoesNotExist:
            return None

class ExpiringToken(Token):
    refreshed = models.DateTimeField(_('Refreshed'), auto_now_add=True)

    objects = ExpiringTokenManager()

    def refresh(self):
        self.refreshed = timezone.now()
        self.save(update_fields=['refreshed'])

    @property
    def timedout(self):
        now = timezone.now()
        timeout_interval = settings.TOKEN_SETTINGS.get(
            'IDLE_TOKEN_LIFESPAN', timedelta(hours=2))
        if now - self.refreshed > timeout_interval:
            return True
        return False

    @property
    def expired(self):
        now = timezone.now()
        expiry_interval = settings.TOKEN_SETTINGS.get(
            'EXPIRING_TOKEN_LIFESPAN', timedelta(days=30))
        if self.created < now - expiry_interval:
            return True
        return False

    class Meta:
        verbose_name = 'Expiring Token'
        verbose_name_plural = 'Expiring Tokens'


class ProfileManager(models.Manager):

    def create(self, email, name, is_junior_fellow, campus, batch, number, country_code='', points=0):
        user = AppUser(email=email, is_active=False)
        user.save()

        profile = Profile(user=user, name=name, is_junior_fellow=is_junior_fellow,
                          campus=campus, batch=batch, points=points)
        profile.save()

        phone_number = PhoneNumber(
            user_profile=profile, country_code=country_code, number=number)
        phone_number.save()

        token = ExpiringToken(user = user)
        token.save()

        return profile


class Profile(models.Model):
    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        primary_key=True
    )
    name = models.CharField(max_length=100)
    is_junior_fellow = models.BooleanField()
    campus = models.CharField(max_length=100)
    batch = models.PositiveIntegerField()
    points = models.PositiveIntegerField(blank=True)
    picture = models.ImageField(upload_to='profile-pics', blank=True)

    objects = ProfileManager()

    def deduct_points(self, points):
        self.points -= points
        self.save()

    def __str__(self):
        return f'{self.name} - {self.user}'


class PhoneNumber(models.Model):
    user_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='phone_number'
    )
    country_code = models.CharField(max_length=5, blank=True)
    number = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.country_code} {self.number}'
