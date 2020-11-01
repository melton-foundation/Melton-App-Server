import uuid

from django.conf import settings
from django.core.files import File
from django.core.mail import mail_managers
from django.template.loader import render_to_string
from response.errors.authentication import (AccountNotApproved,
                                            ProfileDoesNotExist,
                                            UserNotRegistered)
from rest_framework import exceptions, status

from authentication.authentication import AppleOauth, GoogleOauth, WeChatOauth
from authentication.models import AppUser, ExpiringToken, Profile
from authentication.serializers import (LoginSerializer,
                                        ProfileCreateSerializer,
                                        ProfileReadUpdateSerializer,
                                        RegistrationStatusSerializer)


def register_user(request):
    data = request.data
    serializer = ProfileCreateSerializer(data=data)

    if serializer.is_valid():
        profile = serializer.save()
        if settings.EMAIL_REGISTER_NOTIFICATION and len(settings.MANAGERS) > 0:
            send_registration_notification(request, [profile])

        response_status = status.HTTP_201_CREATED
        response = {"type": "success",
                    "message": f"User {profile.user.email} created successfully"}

    else:
        response, response_status = _form_bad_request_response(
            serializer.errors)

    return response, response_status


def send_registration_notification(request, profiles):
    # TODO: Use a better way to send mails asynchronously
    message = render_to_string('authentication/new_registration_email.html',
                               request=request, context={"profiles": profiles})
    try:
        mail_managers(subject="New Sign-up on Melton App",
                      message='', html_message=message)
    except ValueError:
        print("ERROR: Manager mails are not configured properly")
    except:
        print("ERROR: Something went wrong in sending mail")


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


def check_profile_exists(email=None, user=None):
    profile_exists = False
    if user is not None:
        profile_exists = Profile.objects.exists(user=user)
    elif email is not None:
        profile_exists = Profile.objects.filter(user__email=email).exists()
    return profile_exists


def login(data):
    data = _normalise_login_data(data)
    serializer = LoginSerializer(data=data)

    try:
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            token = serializer.validated_data["token"]
            auth_provider = serializer.validated_data["authProvider"]
            response, response_status = check_registration({"email": email})

            if (response_status == status.HTTP_204_NO_CONTENT):
                return UserNotRegistered(email=email).to_dict(), status.HTTP_403_FORBIDDEN

            if not response.get('isApproved', False):
                return AccountNotApproved(email=email).to_dict(), status.HTTP_403_FORBIDDEN

            if not check_profile_exists(email=email):
                return ProfileDoesNotExist(email=email).to_dict(), status.HTTP_403_FORBIDDEN

            response, response_status = _login_valid_user(
                email, token, auth_provider)
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


def _login_valid_user(email, token, auth_provider):
    auth = _get_auth_client(email, token, auth_provider)
    success = auth.login()

    if success:
        extension, picture_file = auth.get_profile_picture()
        if picture_file is not None:
            save_profile_picture(picture_file, extension, email=email)
        response_status = status.HTTP_200_OK
        response = {"type": "success",
                    "appToken": get_token(email=email).key,
                    "message": "You are logged in."}
    else:
        response_status = status.HTTP_401_UNAUTHORIZED
        response = {"type": "failure",
                    "message": "Your email and token do not match."}

    return response, response_status


def _get_auth_client(email, token, auth_provider):
    if auth_provider == "GOOGLE":
        return GoogleOauth(email, token)
    elif auth_provider == "APPLE":
        return AppleOauth(email, token)
    else:
        return WeChatOauth(email, token)


def read_profile(user=None, email=None):
    profile = None
    try:
        profile = get_profile(user=user, email=email)
    except (AppUser.DoesNotExist, Profile.DoesNotExist):
        return ProfileDoesNotExist(email=email), status.HTTP_404_NOT_FOUND

    serializer = ProfileReadUpdateSerializer(profile)
    response = {"type": "success", "profile": serializer.data}
    response_status = status.HTTP_200_OK

    return response, response_status


def get_profile(user=None, email=None):
    profile = None
    if user is not None:
        profile = Profile.objects.prefetch_related(
            "phone_number").get(user=user)
    elif email is not None:
        user = AppUser.objects.get(email=email)
        profile = Profile.objects.prefetch_related(
            "phone_number").get(user=user)

    return profile


def update_profile(user, data):
    profile = Profile.objects.prefetch_related(
        "phone_number").get(user=user)
    serializer = ProfileReadUpdateSerializer(profile, data=data)
    if serializer.is_valid():
        serializer.save()

        response_status = status.HTTP_200_OK
        response = {"type": "success", "profile": serializer.data}
    else:
        response, response_status = _form_bad_request_response(
            serializer.errors)

    return response, response_status


def save_profile_picture(picture_file, extension, user=None, email=None):
    if user is not None:
        profile = Profile.objects.get(user=user)
        email = user.email
    elif email is not None:
        user = AppUser.objects.get(email=email)
        profile = Profile.objects.get(user=user)

    filename = email.split('@')[0] + "_" + \
        str(uuid.uuid4().hex)[:6] + extension
    profile.picture.save(filename, picture_file)
    profile.save()

    if picture_file is not None and isinstance(picture_file, File):
        picture_file.close()


def _form_bad_request_response(errors):
    response_status = status.HTTP_400_BAD_REQUEST
    errors["type"] = "failure"
    return errors, response_status


def _normalise_login_data(data):
    if "authProvider" in data:
        data["authProvider"] = data["authProvider"].upper()

    return data
