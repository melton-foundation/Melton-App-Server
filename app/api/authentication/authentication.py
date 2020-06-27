from abc import ABC
import mimetypes

import requests as rq
from django.conf import settings
from django.utils.translation import gettext_lazy as localize
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from authentication.models import ExpiringToken


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
        self.picture_url = None

    def check_claim(self, verified_email):
        return self.claimed_email == verified_email

    def login(self, token):
        raise NotImplementedError

    def save_profile_picture_url(self, picture):
        self.picture_url = picture

    def get_profile_picture(self):
        if self.picture_url is None:
            return None, None
        response = rq.get(self.picture_url)
        data = None
        if response.status_code == 200:
            data = response.content
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type)
            extension = str(extension) if extension is not None else ''
        img_temp = NamedTemporaryFile()
        img_temp.write(data)
        img_temp.flush()
        return extension, File(img_temp)


class GoogleOauth(OauthSignIn):

    def login(self):
        idinfo = id_token.verify_oauth2_token(
            self.token, requests.Request(), settings.GAUTH_CLIENT_ID)

        if not isinstance(idinfo, dict) or 'email' not in idinfo:
            raise exceptions.AuthenticationFailed('Invalid token')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        if 'picture' in idinfo:
            self.save_profile_picture_url(idinfo['picture'])

        success = self.check_claim(idinfo['email'])
        return success


class WeChatOauth(OauthSignIn):

    def login(self):
        return False
