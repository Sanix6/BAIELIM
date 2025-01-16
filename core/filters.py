from django_filters import FilterSet
from django_filters import rest_framework as filters
from core import models
from user.filters import CharFilterOR


class ItemFilter(FilterSet):
    category = filters.CharFilter('category')
    costs = CharFilterOR(field_name='costs', lookup_expr='in')
    isSale = filters.BooleanFilter('isSale')
    author = filters.CharFilter('author')
    costIn = filters.NumberFilter('costIn', lookup_expr='gt')

    class Meta:
        models = models.Item
        fields = ('category', 'costs', 'isSale', 'author', 'costIn')


class CostChangeHistoryFilter(FilterSet):
    item = filters.CharFilter('item')

    class Meta:
        models = models.CostChangeHistory
        fields = ('item', )


class OrderFilter(FilterSet):
    store = filters.CharFilter('store')
    agent = filters.CharFilter('agent')
    driver = filters.CharFilter('driver')
    status = filters.CharFilter('status')
    start_date = filters.DateFilter(field_name="dateCreated__date", lookup_expr='gte')
    end_date = filters.DateFilter(field_name="dateCreated__date", lookup_expr='lte')
    paymentStatuses = CharFilterOR(field_name='paymentStatus', lookup_expr='in')
    costType = filters.CharFilter('costType')
    items = CharFilterOR(field_name='items', lookup_expr='in')
    items_with_null_item = filters.BooleanFilter(method="filter_items_with_null_item", label="Товары с item=None")

    class Meta:
        models = models.Order
        fields = ('store', 'agent', 'driver', 'status', 'start_date', 'end_date', 'paymentStatuses', 'costType', 'items',
                  'items_with_null_item')

    def filter_items_with_null_item(self, queryset, name, value):
        """
        Фильтрует заказы, где связанные OrderItem имеют item=None.
        """
        if value:  # Если фильтр установлен в True
            return queryset.filter(items__item__isnull=True).distinct()
        return queryset


class TransactionFilter(FilterSet):
    agent = filters.CharFilter('agent')

    class Meta:
        models = models.Transaction
        fields = ('agent', )


class TransactionOrderFilter(FilterSet):
    order = filters.CharFilter('order')
    store = filters.CharFilter('order__store__id')

    class Meta:
        models = models.TransactionOrder
        fields = ('order', 'store')


class OrderHistoryFilter(FilterSet):
    order = filters.CharFilter('order')

    class Meta:
        models = models.OrderHistory
        fields = ('order', )


class ReturnOrderFilter(FilterSet):
    order = filters.CharFilter('order')

    class Meta:
        models = models.ReturnsOrder
        fields = ('order', )
