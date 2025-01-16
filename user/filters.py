from django_filters import FilterSet
from django_filters import rest_framework as filters
from user import models
from django.db.models.functions import TruncDate
from django.db.models import Q


class CharFilterOR(filters.BaseInFilter, filters.CharFilter):
    pass


class AgentFilter(FilterSet):
    costTypes = CharFilterOR(field_name='costTypes', lookup_expr='in')
    oneC_code = filters.CharFilter('oneC_code')

    class Meta:
        models = models.Agent
        fields = ('costTypes', 'oneC_code')


class StoreFilter(FilterSet):
    costType = CharFilterOR(field_name='costType', lookup_expr='in')
    store_agent = filters.CharFilter('store_agent')
    region = filters.CharFilter('region')
    oneC_code = filters.CharFilter('oneC_code')
    dateCreated = filters.DateFilter(field_name='dateCreated', method='filter_by_date')
    start_date = filters.DateFilter(field_name='dateCreated__date', lookup_expr='gte')
    oneC_code_empty = filters.BooleanFilter(method='filter_oneC_code_empty')
    order_empty = filters.BooleanFilter(method='filter_order_empty')
    costType_empty = filters.BooleanFilter(method='filter_costType_empty')
    store_is_empty = filters.BooleanFilter(method='filter_store_is_empty')
    end_month = filters.DateFilter(field_name='dateCreated__date', lookup_expr='lte')

    class Meta:
        models = models.Store
        fields = ('costType', 'store_agent', 'region', 'oneC_code', 'dateCreated', 'start_date', 'oneC_code_empty',
                  'order_empty', 'store_is_empty', 'end_month')

    def filter_by_date(self, queryset, name, value):
        queryset = queryset.annotate(date=TruncDate('dateCreated'))
        return queryset.filter(date=value)

    def filter_store_is_empty(self, queryset, name, value):
        queryset = queryset.filter(store_agent__isnull=True)
        return queryset

    def filter_costType_empty(self, queryset, name, value):
        if value is False:
            stores_with_zero_lat_lon = queryset.all()
            stores_without_orders = stores_with_zero_lat_lon.filter(~Q(costType__isnull=True))
            stores_without_orders = stores_with_zero_lat_lon.filter(costType__isnull=False)
        else:
            stores_with_zero_lat_lon = queryset.all()
            stores_without_orders = stores_with_zero_lat_lon.filter(~Q(costType__isnull=False))
            stores_without_orders = stores_with_zero_lat_lon.filter(costType__isnull=True)

        return stores_without_orders

    def filter_oneC_code_empty(self, queryset, name, value):
        return queryset.filter(oneC_code__isnull=True) | queryset.filter(oneC_code='')

    def filter_order_empty(self, queryset, name, value):
        if value is False:
            stores_with_zero_lat_lon = queryset.all()
            stores_without_orders = stores_with_zero_lat_lon.filter(~Q(order__isnull=True))
            stores_without_orders = stores_with_zero_lat_lon.filter(order__isnull=False).distinct()
        else:
            stores_with_zero_lat_lon = queryset.all()
            stores_without_orders = stores_with_zero_lat_lon.filter(~Q(order__isnull=False))
            stores_without_orders = stores_with_zero_lat_lon.filter(order__isnull=True).distinct()

        return stores_without_orders


class DayPlanFilter(FilterSet):
    day = filters.CharFilter('day')
    agent = filters.CharFilter('agent')
    status = filters.CharFilter('status')
    dateVisit = filters.DateFilter('dateVisit')

    class Meta:
        models = models.DayPlan
        fields = ('day', 'agent', 'status', 'dateVisit')


class StorePlanFilter(FilterSet):
    store = filters.CharFilter('store')

    class Meta:
        models = models.PlanStore
        fields = ('store', )
