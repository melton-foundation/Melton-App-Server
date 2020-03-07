from rest_framework import status

from authentication.serializers import ProfileSerializer, RegistrationStatusSerializer


def register_user(data):
    serializer = ProfileSerializer(data=data)

    if serializer.is_valid():
        _ = serializer.save()
        response_status = status.HTTP_201_CREATED
        response = {"type": "success", "message": "User created successfully"}
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
                        "is_active": is_active,
                        "message": f"Your registration is {approved}"}
            response_status = status.HTTP_200_OK
    else:
        response, response_status = _form_bad_request_response(
            serializer.errors)

    return response, response_status


def _form_bad_request_response(errors):
    response_status = status.HTTP_400_BAD_REQUEST
    errors["type"] = "failure"
    return errors, response_status
