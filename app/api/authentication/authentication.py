from rest_framework.authentication import TokenAuthentication
from authentication.models import ExpiringToken
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as localize
from abc import ABC
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):

    model = ExpiringToken

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            raise exceptions.AuthenticationFailed(localize('Invalid token.'))
        else:
            return result

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(localize('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.PermissionDenied(
                localize('Your account has not been approved yet.'))

        if token.expired:
            token.delete()
            raise exceptions.AuthenticationFailed(
                localize('Token has expired. Please login again.'))

        token.refresh()
        return (token.user, token)


class OauthSignIn(ABC):

    def __init__(self, claimed_email, token):
        self.claimed_email = claimed_email
        self.token = token
        self.idinfo = None
        # print("---------------------------------\n\n", token, "----------------------------------------------\n")

    def check_claim(self, verified_email):
        return self.claimed_email == verified_email

    def login(self, token):
        raise NotImplementedError


class GoogleOauth(OauthSignIn):

    def login(self):
        idinfo = id_token.verify_oauth2_token(
            self.token, requests.Request(), settings.GAUTH_CLIENT_ID)

        if not isinstance(idinfo, dict) or 'email' not in idinfo:
            raise exceptions.AuthenticationFailed('Invalid token')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        success = self.check_claim(idinfo['email'])
        return success


class WeChatOauth(OauthSignIn):

    def login(self):
        return False

