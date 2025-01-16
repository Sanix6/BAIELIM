from django.contrib import admin
from core import models
from django.db.models import QuerySet

# from core.functions import sync_items_price


# @admin.action(description='Synchronize items price')
# def synchronizer(self, request, qs: QuerySet):
#     sync = sync_items_price()


# class ItemAdmin(admin.ModelAdmin):
#     actions = [synchronizer]

@admin.action(description='Удалить карзины у которых пустой товар')
def change_totalCost(self, request, qs: QuerySet):
    orders = models.Order.objects.filter(dateCreated__date__gte='2024-09-13', dateCreated__date__lte='2024-09-16')
    # orders = models.Order.objects.filter(pk=6069)
    orders_id = []
    for i in orders:
        items = i.items.all()
        currentTotalCost = 0
        for j in items:
            currentTotalCost += j.count * j.soldCost
        if currentTotalCost != i.totalCost:
            i.totalCost = currentTotalCost
            i.save()
            orders_id.append(i.id)
    f = open('change_orders.txt', 'w')
    f.write(str(orders_id))

@admin.action(description='Set costType')
def setCostType(self, request, qs: QuerySet):
    costType = models.CostType.objects.get(pk=1)
    orders = models.Order.objects.filter(costType__isnull=True)
    for i in orders:
        i.costType = costType
        i.save()


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category',  'author', "quantity")
    list_filter = ('author', )
    search_fields = ['name', 'code', "author", "quantity"]


class OrderAdmin(admin.ModelAdmin):
    actions = [setCostType]


admin.site.register(models.Cost)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.CostChangeHistory)
admin.site.register(models.OrderItem)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Shablon)
admin.site.register(models.TransactionOrder)
admin.site.register(models.Transaction)
admin.site.register(models.OrderHistory)
admin.site.register(models.ReturnsOrder)
