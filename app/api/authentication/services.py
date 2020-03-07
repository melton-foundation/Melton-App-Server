from rest_framework import status

from authentication.serializers import ProfileSerializer, RegistrationStatusSerializer
from authentication.models import AppUser, ExpiringToken


def register_user(data):
    serializer = ProfileSerializer(data=data)

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


def _form_bad_request_response(errors):
    response_status = status.HTTP_400_BAD_REQUEST
    errors["type"] = "failure"
    return errors, response_status
