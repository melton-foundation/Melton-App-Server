from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import filters

from authentication import services, authentication
from authentication.models import Profile
from authentication.serializers import ProfileListSerializer, ProfileRetrieveSerializer

@api_view(['POST'])
def register(request):
    response, status = services.register_user(request.data)
    return Response(response, status=status)


@api_view(['GET'])
def check_registration(request):
    response, status = services.check_registration(
        {'email': request.query_params.get('email', None)})
    return Response(response, status=status)

@api_view(['POST'])
def login(request):
    response, response_status = services.login(request.data)
    return Response(response, status=response_status)

class ProfileView(APIView):
    authentication_classes = [authentication.ExpiringTokenAuthentication]

    def get(self, request):
        response, status = services.get_profile(user = request.user)
        return Response(response, status=status)

    def post(self, request):
        response, status = services.update_profile(request.user, request.data)
        return Response(response, status=status)



class UsersView(ReadOnlyModelViewSet):
    authentication_classes = [authentication.ExpiringTokenAuthentication]
    search_fields = ['name', 'user__email']
    filter_backends = (filters.SearchFilter,)
    queryset = Profile.objects.filter(user__is_active = True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileListSerializer
        return ProfileRetrieveSerializer
    
