from rest_framework import status
from store.serializers import BuyTransactionSerializer, TransactionSerializer
from store.models import StoreItem, Transaction
from response.success.store import ItemBought
from response.errors.store import InsufficientPoints, ItemAlreadyOwned, ItemNotAvailable
from response.errors.common import _form_bad_request_response

def buy_item(data, user):
    serializer = BuyTransactionSerializer(data = data)
    if serializer.is_valid():
        item = get_item(item_id = serializer.data.get("itemId", None), item_name=serializer.data.get("itemName", None))
        user_points = 0
        if not user.profile.points is None:
            user_points = user.profile.points

        if item is None:
            response = ItemNotAvailable().to_dict()
            response_status = status.HTTP_404_NOT_FOUND
        elif item.points > user_points:
            response = InsufficientPoints(user, item).to_dict()
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif item_purchased(user, item):
            response = ItemAlreadyOwned().to_dict()
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            Transaction.objects.buy_item(user, item)
            response = ItemBought(user, item).to_dict()
            response_status = status.HTTP_200_OK
        
    else:
        response, response_status = _form_bad_request_response(serializer.errors)

    return response, response_status


def item_purchased(user, item):
    return Transaction.objects.is_purchased(user, item)


def get_item(item_id=None, item_name=None):
    item = None
    if not item_id is None:
        item = StoreItem.objects.filter(active = True).filter(pk = item_id)
    elif not item_name is None:
        item = StoreItem.objects.filter(active = True).filter(name__iexact = item_name)

    if not item is None and item:
        return item.first()
    else:
        return None
