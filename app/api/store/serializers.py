from rest_framework import serializers

from store.models import StoreItem, Transaction


class StoreItemReadSerializer(serializers.ModelSerializer):
    purchased = serializers.SerializerMethodField(
        "is_purchased_by_user", read_only=True
    )

    def is_purchased_by_user(self, item):
        is_purchased = False
        if "request" in self.context:
            item = self.Meta.model.objects.get(pk=item.id)
            is_purchased = Transaction.objects.is_purchased(
                self.context.get("request").user, item
            )

        return is_purchased

    previewImage = serializers.ImageField(source="preview_image", read_only=True)

    class Meta:
        model = StoreItem
        fields = (
            "id",
            "name",
            "previewImage",
            "description",
            "points",
            "active",
            "purchased",
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("user", "item", "points", "transaction_type")


class BuyTransactionSerializer(serializers.Serializer):
    itemId = serializers.IntegerField(required=False)
    itemName = serializers.CharField(required=False, max_length=100)

    def validate(self, attrs):
        if "itemId" not in attrs and "itemName" not in attrs:
            raise serializers.ValidationError(
                "Either itemId or itemName field should be specified."
            )

        return attrs
