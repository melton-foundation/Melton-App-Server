from rest_framework.response import Response
from rest_framework.viewsets import  GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.decorators import action, api_view, authentication_classes

from authentication import authentication
from store.models import StoreItem
from store.serializers import StoreItemReadSerializer
from store import services

class StoreAPI(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [authentication.ExpiringTokenAuthentication]
    queryset = StoreItem.objects.filter(active = True)
    serializer_class = StoreItemReadSerializer

    @action(methods = ['GET'], detail=True, url_path = 'name')
    def get_store_item_by_name(self, request, pk=None):
        serializer = self.serializer_class(self.queryset.filter(name__icontains = pk), many=True, context = {"request": request})
        return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([authentication.ExpiringTokenAuthentication])
def buy_store_item(request):
    response, response_status = services.buy_item(request.data, request.user)
    return Response(response, status=response_status)
