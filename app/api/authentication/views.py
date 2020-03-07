from rest_framework.decorators import api_view
from rest_framework.response import Response

from authentication import services


@api_view(['POST'])
def register(request):
    response, status = services.register_user(request.data)
    return Response(response, status=status)


@api_view(["GET"])
def check_registration(request):
    response, status = services.check_registration(
        {'email': request.query_params.get('email', None)})
    return Response(response, status=status)
