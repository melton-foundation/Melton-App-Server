from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from authentication.models import AppUser

class AppUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = AppUser
        fields = ['email', 'password1', 'password2']


class AppUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = AppUser
        fields = ['email', 'password']