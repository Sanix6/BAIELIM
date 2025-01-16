from rest_framework import serializers

from category.serializers import CostTypeSerializer, CategorySerializer
from core import models
from django.contrib.auth import get_user_model, authenticate, password_validation

from user.serializers import AgentSerializer, DriverSerializer, StoreSerializerGet, \
    StoreSerializerOpen, DriverSerializerOpen, AdminSerializer, StoreSerializerForOrder, StoreSerializerForGet, \
    AgentSerializerOpen


class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cost
        fields = ('id', 'cost', 'costType', 'bonusAmount')


class CostSerializerGet(serializers.ModelSerializer):
    costType = CostTypeSerializer(read_only=True)

    class Meta:
        model = models.Cost
        fields = ('id', 'cost', 'costType', 'bonusAmount')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = ('id', 'name', 'photo', 'costIn', 'costs', 'category', 'quantity', 'code', 'author', 'weight',
                  'isSale', 'saleCost')


class ItemSerializerGet(serializers.ModelSerializer):
    costs = CostSerializerGet(many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = models.Item
        fields = ('id', 'name', 'photo', 'costIn', 'costs', 'category', 'quantity', 'code', 'author', 'weight',
                  'isSale', 'saleCost',)

    # def save(self, **kwargs):
    #     validated_data = {**self.validated_data, **kwargs}
    #     code = validated_data.get('code', '')
    #     instance = super().save(**kwargs)
    #     instance.code = code
    #     instance.save()
    #     return instance


class ItemAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = ('id', 'name', 'code')


class CostChangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CostChangeHistory
        fields = ('id', 'item', 'dateChanged', 'costs')


class CostChangeHistorySerializerGet(serializers.ModelSerializer):
    costs = CostSerializerGet(many=True)
    item = ItemSerializer(read_only=True)

    class Meta:
        model = models.CostChangeHistory
        fields = ('id', 'item', 'dateChanged', 'costs')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ('id', 'item', 'count', 'soldCost', 'costType')


class OrderItemSerializerGet(serializers.ModelSerializer):
    item = ItemSerializer()
    costType = CostTypeSerializer()

    class Meta:
        model = models.OrderItem
        fields = ('id', 'item', 'count', 'soldCost', 'costType')


class OrderItemSerializerGetSecond(serializers.ModelSerializer):
    item = ItemAllSerializer()
    # costType = CostTypeSerializer()

    class Meta:
        model = models.OrderItem
        fields = ('id', 'item', 'count', 'soldCost')
        # fields = ('id', 'item', 'count', 'soldCost', 'costType')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ('id', 'dateCreated', 'store', 'agent', 'driver', 'costType', 'items', 'totalCost', 'status',
                  'comment', 'dateDelivered', 'lat', 'lon', 'signature', 'photo', 'delComment', 'is_sync_oneC',
                  'paymentStatus', 'amountLeft', 'weight', 'shipping_date')


class OrderSerializerGet(serializers.ModelSerializer):
    store = StoreSerializerForOrder()
    agent = AgentSerializer()
    driver = DriverSerializer()
    costType = CostTypeSerializer()
    items = OrderItemSerializerGet(many=True)

    class Meta:
        model = models.Order
        fields = ('id', 'dateCreated', 'store', 'agent', 'driver', 'costType', 'items', 'totalCost', 'status',
                  'comment', 'dateDelivered', 'lat', 'lon', 'signature', 'photo', 'delComment', 'is_sync_oneC',
                  'paymentStatus', 'amountLeft', 'weight', 'shipping_date')


class OrderSerializerGetSecond(serializers.ModelSerializer):
    store = StoreSerializerForGet()
    agent = AgentSerializerOpen()
    driver = DriverSerializerOpen()
    costType = CostTypeSerializer()
    items = OrderItemSerializerGetSecond(many=True)

    class Meta:
        model = models.Order
        fields = ('id', 'dateCreated', 'store', 'agent', 'driver', 'costType', 'items', 'totalCost', 'status',
                  'is_sync_oneC', 'paymentStatus', 'shipping_date')


class OrderSerializerOpen(serializers.ModelSerializer):
    store = StoreSerializerOpen()

    class Meta:
        model = models.Order
        fields = ('id', 'store')


class ImportItemsSerializer(serializers.Serializer):
    # data = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))
    id = serializers.IntegerField()
    code = serializers.CharField()

    class Meta:
        fields = ('id', 'code')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('id', 'dateCreated', 'description', 'amount', 'agent')


class TransactionSerializerGet(serializers.ModelSerializer):
    agent = AgentSerializer()

    class Meta:
        model = models.Transaction
        fields = ('id', 'dateCreated', 'description', 'amount', 'agent')


class ShablonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Shablon
        fields = ('id', 'agent', 'monStores', 'monDriver', 'tueStores', 'tueDriver', 'wedStores', 'wedDriver',
                  'thuStores', 'thuDriver', 'friStores', 'friDriver', 'satStores', 'satDriver', 'sunStores', 'sunDriver')


class ShablonSerializerGet(serializers.ModelSerializer):
    agent = AgentSerializer()
    monStores = StoreSerializerOpen(many=True, )
    monDriver = DriverSerializerOpen()
    tueStores = StoreSerializerOpen(many=True, )
    tueDriver = DriverSerializerOpen()
    wedStores = StoreSerializerOpen(many=True, )
    wedDriver = DriverSerializerOpen()
    thuStores = StoreSerializerOpen(many=True, )
    thuDriver = DriverSerializerOpen()
    friStores = StoreSerializerOpen(many=True, )
    friDriver = DriverSerializerOpen()
    satStores = StoreSerializerOpen(many=True, )
    satDriver = DriverSerializerOpen()
    sunStores = StoreSerializerOpen(many=True, )
    sunDriver = DriverSerializerOpen()

    class Meta:
        model = models.Shablon
        fields = ('id', 'agent', 'monStores', 'monDriver', 'tueStores', 'tueDriver', 'wedStores', 'wedDriver',
                  'thuStores', 'thuDriver', 'friStores', 'friDriver', 'satStores', 'satDriver', 'sunStores', 'sunDriver')


class CreatePlanSerializer(serializers.Serializer):
    shablon = serializers.PrimaryKeyRelatedField(queryset=models.Shablon.objects.all())

    class Meta:
        fields = ('shablon', )


class TransactionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransactionOrder
        fields = ('id', 'sum', 'comment', 'order', 'dateCreated')


class TransactionOrderSerializerGet(serializers.ModelSerializer):
    order = OrderSerializerOpen()

    class Meta:
        model = models.TransactionOrder
        fields = ('id', 'sum', 'comment', 'order', 'dateCreated')


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderHistory
        fields = ('id', 'order', 'description', 'addedItems', 'removeItems', 'admin', 'dateCreated')


class OrderHistorySerializerGet(serializers.ModelSerializer):
    order = OrderSerializer()
    addedItems = OrderItemSerializerGet(many=True)
    removeItems = OrderItemSerializerGet(many=True)
    admin = AdminSerializer()

    class Meta:
        model = models.OrderHistory
        fields = ('id', 'order', 'description', 'addedItems', 'removeItems', 'admin', 'dateCreated')


class ReturnItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReturnsItem
        fields = ('id', 'item', 'quantity', 'soldCost')


class ReturnItemsSerializerGet(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = models.ReturnsItem
        fields = ('id', 'item', 'quantity', 'soldCost')


class ReturnOrderSerializer(serializers.ModelSerializer):
    returnedItems = ReturnItemsSerializer(many=True)

    class Meta:
        model = models.ReturnsOrder
        fields = ('id', 'order', 'returnedItems', 'comment')

    def create(self, validated_data):
        items = validated_data.pop("returnedItems", None)
        returnedOrder = models.ReturnsOrder.objects.create(**validated_data)

        if items:
            for i in items:
                models.ReturnsItem.objects.create(returnedOrder=returnedOrder, **i)
        return returnedOrder

    def update(self, instance, validated_data):
        # Извлекаем связанные объекты returnedItems из данных
        items = validated_data.pop("returnedItems", None)

        # Обновляем основные поля экземпляра ReturnsOrder
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items:
            # Удаляем старые связанные элементы
            instance.returnedItems.all().delete()

            # Создаем новые связанные элементы
            for item_data in items:
                models.ReturnsItem.objects.create(returnedOrder=instance, **item_data)

        return instance


class ReturnOrderSerializerGet(serializers.ModelSerializer):
    returnedItems = ReturnItemsSerializerGet(many=True)

    class Meta:
        model = models.ReturnsOrder
        fields = ('id', 'order', 'returnedItems', 'comment')

    def create(self, validated_data):
        items = validated_data.pop("returnedItems", None)
        returnedOrder = models.ReturnsOrder.objects.create(**validated_data)

        if items:
            for i in items:
                models.ReturnsItem.objects.create(returnedOrder=returnedOrder, **i)
        return returnedOrder
