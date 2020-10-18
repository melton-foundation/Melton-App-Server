import mimetypes
from abc import ABC
from django.utils import timezone
from datetime import timedelta

import jwt
import requests as rq
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils.translation import gettext_lazy as localize
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
            raise exceptions.AuthenticationFailed(localize("Invalid token."))
        else:
            return result

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(localize("Invalid token."))

        if not token.user.is_active:
            raise exceptions.PermissionDenied(
                localize("Your account has not been approved yet."))

        if token.expired:
            token.delete()
            raise exceptions.AuthenticationFailed(
                localize("Token has expired. Please login again."))

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
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)
            extension = str(extension) if extension is not None else ""
        img_temp = NamedTemporaryFile()
        img_temp.write(data)
        img_temp.flush()
        return extension, File(img_temp)


class GoogleOauth(OauthSignIn):

    def login(self):
        idinfo = id_token.verify_oauth2_token(self.token, requests.Request())

        if (not isinstance(idinfo, dict) or idinfo["aud"] not in [settings.GAUTH_ANDROID_CLIENT_ID, settings.GAUTH_IOS_CLIENT_ID] 
            or "email" not in idinfo):
            raise exceptions.AuthenticationFailed("Invalid token")

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        if "picture" in idinfo:
            self.save_profile_picture_url(idinfo["picture"])

        success = self.check_claim(idinfo["email"])
        return success

class AppleOauth(OauthSignIn):

    AUDIENCE = "https://appleid.apple.com"
    ACCESS_TOKEN_URL = "https://appleid.apple.com/auth/token"

    def login(self):
        idinfo = {}
        client_id, client_secret = self.get_key_and_secret()

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": self.token,
            "grant_type": "authorization_code",

        }

        res = rq.post(AppleOauth.ACCESS_TOKEN_URL, data=data, headers=headers)
        idinfo = res.json()

        if res.status_code == 400:
            error_message = idinfo.get("error", "Authentication failed.")
            raise exceptions.AuthenticationFailed(error_message) 

        id_token = idinfo.get("id_token", None)

        if id_token:
            decoded = jwt.decode(id_token, "", verify=False)
            idinfo.update({"email": decoded["email"]}) if "email" in decoded else None
            idinfo.update({"uid": decoded["sub"]}) if "sub" in decoded else None

        if not "email" in idinfo:
            raise exceptions.AuthenticationFailed("Invalid token.")

        success = self.check_claim(idinfo["email"])
        return success

    def get_key_and_secret(self):
        headers = {
            "kid": settings.APPLE_OAUTH_KEY_ID
        }

        payload = {
            "iss": settings.APPLE_OAUTH_TEAM_ID,
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(days=12),
            "aud": AppleOauth.AUDIENCE,
            "sub": settings.APPLE_OAUTH_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload, 
            settings.APPLE_OATH_PRIVATE_KEY, 
            algorithm="ES256", 
            headers=headers
        ).decode("utf-8")
        
        return settings.APPLE_OAUTH_CLIENT_ID, client_secret


class WeChatOauth(OauthSignIn):

    def login(self):
        return False
