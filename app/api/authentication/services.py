from rest_framework import status

from authentication.models import AppUser, ExpiringToken, Profile
from authentication.serializers import (LoginSerializer,
                                        ProfileCreateSerializer,
                                        ProfileReadSerializer,
                                        RegistrationStatusSerializer)
from django.conf import settings
from authentication.authentication import GoogleOauth, WeChatOauth
from rest_framework import exceptions


def register_user(data):
    serializer = ProfileCreateSerializer(data=data)

    if serializer.is_valid():
        profile = serializer.save()
        token = get_token(user=profile.user)
        response_status = status.HTTP_201_CREATED
        response = {"type": "success", "appToken": token.key if not token is None else None,
                    "message": "User created successfully"}
    else:
        response, response_status = _form_bad_request_response(
            serializer.errors)

    return response, response_status


def check_registration(data):
    serializer = RegistrationStatusSerializer(data=data)

    if serializer.is_valid():
        is_active = serializer.check_status()
        if is_active is None:
            response = {
                "type": "failure", "message": "Email provided not found. Please register before checking status."}
            response_status = status.HTTP_204_NO_CONTENT
        else:
            approved = "Approved" if is_active else "Pending"
            response = {"type": "success",
                        "email": serializer.validated_data["email"],
                        "isApproved": is_active,
                        "message": f"Your registration is {approved}"}
            response_status = status.HTTP_200_OK
    else:
        response, response_status = _form_bad_request_response(
            serializer.errors)

    return response, response_status


def get_token(email=None, user=None):
    token = None
    if user is not None:
        token, _ = ExpiringToken.objects.get_or_create(user=user)
    elif email is not None:
        token, _ = ExpiringToken.objects.get_or_create_by_email(email=email)

    return token


def login(data):
    data = _normalise_login_data(data)
    serializer = LoginSerializer(data=data)

    try:
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            token = serializer.validated_data["token"]
            auth_provider = serializer.validated_data["authProvider"]
            response, response_status = check_registration({"email": email})
            if not (response_status == status.HTTP_200_OK and response['isApproved']):
                return response, response_status

            auth = _get_auth_client(email, token, auth_provider)
            success = auth.login()

            if success:
                response_status = status.HTTP_200_OK
                response = {"type": "success",
                            "appToken": get_token(email=email).key,
                            "message": "You are logged in."}
            else:
                response_status = status.HTTP_401_UNAUTHORIZED
                response = {"type": "failure",
                            "message": "Your email and token do not match."}
        else:
            response, response_status = _form_bad_request_response(
                serializer.errors)

        return response, response_status
    except exceptions.AuthenticationFailed as e:
        response_status = e.status_code
        response = {"type": "failure", "message": e.detail}
        return response, response_status
    except ValueError as error:
        response_status = status.HTTP_401_UNAUTHORIZED
        response = {"type": "failure",
                    "message": "Login failed.", "details": str(error)}
        return response, response_status


def _get_auth_client(email, token, auth_provider):
    if auth_provider == "GOOGLE":
        return GoogleOauth(email, token)
    else:
        return WeChatOauth(email, token)


def get_profile(user=None, email=None):
    serializer = ProfileReadSerializer()
    if user is not None:
        profile = Profile.objects.prefetch_related(
            "phone_number").get(user=user)
        serializer = ProfileReadSerializer(profile)
    elif email is not None:
        user = AppUser.objects.get(email=email)
        profile = Profile.objects.prefetch_related(
            "phone_number").get(user=user)
        serializer = ProfileReadSerializer(profile)

    response = {"type": "success", "profile": serializer.data}
    response_status = status.HTTP_200_OK

    return response, response_status


def _form_bad_request_response(errors):
    response_status = status.HTTP_400_BAD_REQUEST
    errors["type"] = "failure"
    return errors, response_status


def _normalise_login_data(data):
    if "authProvider" in data:
        data["authProvider"] = data["authProvider"].upper()

    return data
