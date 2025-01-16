from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from core.models import Order
from user import models, utils
from user.functions import sync_with_oneC, import_stores, import_costTypes, create_store_inOneC, \
    second_create_store_inOneC
from django.db.models import Q


class ModelAdminAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['login', 'name', 'id']

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'user_type')}),
    )
    readonly_fields = ('id', 'user_type')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


@admin.action(description='Change user_type')
def change_user_type(self, request, qs: QuerySet):
    for i in qs:
        i.user_type = utils.AGENT
        i.save()


class AgentAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ['login', 'name', 'id', 'user_type']
    actions = [change_user_type]

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'passport_front', 'passport_back', 'birthdate', 'address', 'is_active',
                                         'phoneNumber', 'balance', 'costTypes', 'photo', 'user_type', 'oneC_code')}),
    )
    readonly_fields = ('id', 'user_type')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


@admin.action(description='Synchronize stores after first july')
def synchronizer(self, request, qs: QuerySet):
    sync = second_create_store_inOneC(qs)


@admin.action(description='Удалить магазины test')
def deleter(self, request, qs: QuerySet):
    stores_with_optovik_costType = models.Store.objects.filter(costType_id=8)
    stores_without_orders = stores_with_optovik_costType.filter(~Q(order__isnull=False))
    stores_without_orders = stores_with_optovik_costType.filter(order__isnull=True)
    iterator = 0
    for i in stores_without_orders:
        if iterator == 1:
            break
        i.delete()


@admin.action(description='Set costType')
def set_costType(self, request, qs: QuerySet):
    costType = models.CostType.objects.get(pk=1)
    stores = models.Store.objects.filter(costType__isnull=True)
    for i in stores:
        i.costType = costType
        i.save()


@admin.action(description='Set agent')
def set_agent(self, request, qs: QuerySet):
    stores = models.Store.objects.filter(store_agent__isnull=True)
    for i in stores:
        order = Order.objects.filter(store=i.id).first()
        if order:
            if order.agent is not None:
                i.store_agent = order.agent
                i.save()


class StoreAdmin(admin.ModelAdmin):
    search_fields = ('name', 'login')
    list_display = ['login', 'name', 'id', 'oneC_code', 'store_agent']
    actions = [set_costType, set_agent]

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'contactName', 'photo', 'phoneNumber', 'phoneNumber1', 'phoneNumber2',
                                         'phoneNumber3', 'score', 'address', 'lat', 'lon', 'costType', 'user_type',
                                         'dateCreated', 'area', 'documents', 'oneC_code', 'is_active', 'store_agent',
                                         'region')}),
    )
    readonly_fields = ('id', 'user_type', 'dateCreated')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


class DriverAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ['login', 'name', 'id', 'oneC_code']

    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'photo', 'passport_front', 'passport_back', 'oneC_code',
                                         'phoneNumber', 'balance', 'user_type', 'is_active')}),
    )
    readonly_fields = ('id', 'user_type')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        obj.save()


class UserLogsAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'user_id', 'dateCreated']


admin.site.register(models.ModelAdmin, ModelAdminAdmin)
admin.site.register(models.Manager, ModelAdminAdmin)
admin.site.register(models.Agent, AgentAdmin)
admin.site.register(models.Store, StoreAdmin)
admin.site.register(models.Driver, DriverAdmin)
admin.site.register(models.PlanStore)
admin.site.register(models.DayPlan)
admin.site.register(models.UsersLog, UserLogsAdmin)
