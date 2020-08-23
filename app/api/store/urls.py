from django.urls import path, include
from rest_framework import routers
from store.views import StoreAPI, buy_store_item


router = routers.SimpleRouter()
router.register(r'store', StoreAPI)

urlpatterns = router.urls

urlpatterns += [
    path('buy/', buy_store_item, name = 'buy_store_item'),
    path('buy', buy_store_item, name = 'buy_store_item')
]