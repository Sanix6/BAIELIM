from collections import defaultdict

import requests
import json
from django.shortcuts import render
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db.models import F, Sum, Count, Avg
from core import models, serializers, filters
from core.functions import get_next_monday, remove_bom, post_request_to_OneC, create_items_in_OneC
from user.models import DayPlan, PlanStore
# import datetime
from user.utils import DAYS_OF_WEEK
from django.db.models import Q

from rest_framework import pagination


class CostViewSet(viewsets.ModelViewSet):
    queryset = models.Cost.objects.all()
    serializer_class = serializers.CostSerializer

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.CostSerializerGet
        else:
            return serializers.CostSerializer


class ItemPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all().order_by('name')
    serializer_class = serializers.ItemSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.ItemFilter
    search_fields = ('name',)
    pagination_class = ItemPagination

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.ItemSerializerGet
        else:
            return serializers.ItemSerializer


class CostChangeHistoryViewSet(viewsets.ModelViewSet):
    queryset = models.CostChangeHistory.objects.all()
    serializer_class = serializers.CostChangeHistorySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.CostChangeHistoryFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.CostChangeHistorySerializerGet
        else:
            return serializers.CostChangeHistorySerializer

    def get_queryset(self):
        return self.queryset.order_by('-dateChanged')


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.OrderItemSerializerGet
        else:
            return serializers.OrderItemSerializer


class OrderPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.OrderFilter
    search_fields = ('store__name', 'store__phoneNumber', 'store__address', 'agent__name', 'agent__phoneNumber')

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.OrderSerializerGet
        else:
            return serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        request_items = request.data['items']
        items_data = []
        for i in request_items:
            try:
                item_serializer = serializers.OrderItemSerializer(data=i)
                item_serializer.is_valid(raise_exception=True)
                saved_item = item_serializer.save()
                items_data.append(saved_item.id)
            except:
                items_data.append(i)

        request.data['items'] = items_data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        items = instance.items.all()
        total_bonus_add = 0
        for i in items:
            i_sum = i.count * i.soldCost
            cost = i.item.costs.all().filter(costType=instance.costType).first()
            if cost:
                bonus_percentage = cost.bonusAmount
                bonus_add = i_sum * (bonus_percentage / 100)
                total_bonus_add += bonus_add
            # else:
            #     error = ValidationError({'costType': ['Невенрный costType!']})
            #     raise error
        try:
            agent = instance.agent
            agent.balance += total_bonus_add
            agent.save()
            description = f'Бонус за закза id={instance.id}'
            transaction = models.Transaction.objects.create(amount=total_bonus_add, agent=agent,
                                                            description=description)
        except:
            pass
            # raise ValidationError({'agent': ['Поле агент не был передан!']})

        self.perform_update(serializer)
        return Response(serializer.data)

        # instance = self.get_object()
        # orders_id = [instance.id]
        # oneC_status = create_items_in_OneC(orders_id)
        # if oneC_status == 'success':
        #
        #     if getattr(instance, '_prefetched_objects_cache', None):
        #         # If 'prefetch_related' has been applied to a queryset, we need to
        #         # forcibly invalidate the prefetch cache on the instance.
        #         instance._prefetched_objects_cache = {}
        #
        #     return Response(serializer.data)
        # else:
        #     return Response({'status': 'При синхронизации с 1С произошла ошибка! Данные были обнавлены только с сервера!'})


class CustomPaginationOrder(pagination.PageNumberPagination):
    page_size = 80
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class OrderViewSetSecond(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializerGetSecond
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.OrderFilter
    search_fields = ('store__name', 'store__phoneNumber', 'store__address', 'agent__name', 'agent__phoneNumber')
    pagination_class = CustomPaginationOrder


class ReturnOrderViewSet(viewsets.ModelViewSet):
    queryset = models.ReturnsOrder.objects.all()
    serializer_class = serializers.ReturnOrderSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.ReturnOrderFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.ReturnOrderSerializerGet
        else:
            return serializers.ReturnOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_data = serializer.save()
        headers = self.get_success_headers(serializer.data)
        order = serializer.validated_data['order']
        # order = models.Order.objects.get(pk=order_id)
        cart_items = order.items.all()
        returned_items = saved_data.returnedItems.all()
        order_totalCost = 0

        for i in cart_items:
            for j in returned_items:
                if i.item == j.item:
                    i.count -= j.quantity
                i.save()
            order_totalCost += i.count * i.soldCost
        new_amountLeft = order.totalCost - order_totalCost
        order.totalCost = order_totalCost
        order.amountLeft -= new_amountLeft
        order.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_returned_items = list(instance.returnedItems.all())

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_data = serializer.save()

        # Работа с заказом
        order = serializer.validated_data['order']
        cart_items = order.items.all()
        # returned_items = updated_data.returnedItems.all()
        returned_items = models.ReturnsItem.objects.filter(returnedOrder=instance)
        order_totalCost = 0

        # Словарь для хранения старых значений quantity
        old_quantity_map = {item.item.id: item.quantity for item in old_returned_items}

        for i in cart_items:
            for j in returned_items:
                if i.item == j.item:
                    # Считаем разницу между старым и новым quantity
                    old_quantity = old_quantity_map.get(j.item.id, 0)
                    difference = j.quantity - old_quantity

                    i.count -= difference
                    i.save()

            # Пересчет общей стоимости заказа
            order_totalCost += i.count * i.soldCost

        # Корректировка суммы заказа
        new_amountLeft = order.totalCost - order_totalCost
        order.totalCost = order_totalCost
        order.amountLeft -= new_amountLeft
        order.save()

        # Очистка кэша предвыборки, если он есть
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ReturnItemViewSet(viewsets.ModelViewSet):
    queryset = models.ReturnsItem.objects.all()
    serializer_class = serializers.ReturnItemsSerializer

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.ReturnItemsSerializerGet
        else:
            return serializers.ReturnItemsSerializer


class ImportItemsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=serializers.ImportItemsSerializer())
    def post(self, request):
        new_items = request.data
        return Response(new_items)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.TransactionFilter

    def get_queryset(self):
        return self.queryset.order_by('-dateCreated')

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.TransactionSerializerGet
        else:
            return serializers.TransactionSerializer


class ShablonViewSet(viewsets.ModelViewSet):
    queryset = models.Shablon.objects.all()
    serializer_class = serializers.ShablonSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('agent',)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.ShablonSerializerGet
        else:
            return serializers.ShablonSerializer


class CreatePlanView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=serializers.CreatePlanSerializer())
    def post(self, request):
        next_mon = get_next_monday()
        next_sun = next_mon + timedelta(days=6)
        try:
            shablon = models.Shablon.objects.get(pk=request.data['shablon'])
        except models.Shablon.DoesNotExist:
            shablon = None
        if shablon is not None:
            agent_id = shablon.agent.id
            dayPlan = DayPlan.objects.filter(dateVisit__gte=next_mon, dateVisit__lte=next_sun,
                                             agent_id=agent_id)
            if dayPlan:
                raise ValidationError({'dateVisit': 'Данный агент в указанный период времени занят!'})
            else:
                monday_stores_plan = []
                for store in shablon.monStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    monday_stores_plan.append(storesPlan)

                tuesday_stores_plan = []
                for store in shablon.tueStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    tuesday_stores_plan.append(storesPlan)

                wednesday_stores_plan = []
                for store in shablon.wedStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    wednesday_stores_plan.append(storesPlan)

                thursday_stores_plan = []
                for store in shablon.thuStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    thursday_stores_plan.append(storesPlan)

                friday_stores_plan = []
                for store in shablon.friStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    friday_stores_plan.append(storesPlan)

                saturday_stores_plan = []
                for store in shablon.satStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    saturday_stores_plan.append(storesPlan)

                sunday_stores_plan = []
                for store in shablon.sunStores.all():
                    storesPlan = PlanStore.objects.create(store=store, status='new', photo='', madeOrder=True)
                    sunday_stores_plan.append(storesPlan)

                drivers = [shablon.monDriver, shablon.tueDriver, shablon.wedDriver, shablon.thuDriver,
                           shablon.friDriver, shablon.satDriver, shablon.sunDriver]
                stores_plans = [monday_stores_plan, tuesday_stores_plan, wednesday_stores_plan, thursday_stores_plan,
                                friday_stores_plan, saturday_stores_plan, sunday_stores_plan]

                for i in range(7):
                    date_visit = next_mon + timedelta(days=i)
                    day_of_week = DAYS_OF_WEEK[i][0]

                    day_plan = DayPlan.objects.create(day=day_of_week, agent_id=agent_id, status='new',
                                                      driver=drivers[i], dateVisit=date_visit)
                    day_plan.stores_plan.set(stores_plans[i])
                    day_plan.save()

            return Response({'message': 'success'}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError({'shablon': 'Указанный шаблон не существует, ID шаблона был неправильно передан!'})


class SynchronizeItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.data['target'] == 'synchronize':
            site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
            second_site_url = 'http://212.112.127.164:8080/Exchange2025organic/hs/getTables/data'
            data = {"Table": "Остатки"}
            username = 'Techtoo'
            password = '123'
            credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            send_data_json = json.dumps(data)  # Преобразование словаря send_data в JSON строку
            send_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты

            send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)  # Удаление BOM символов из данных

            send_data_without_bom = json.loads(
                send_data_json_bytes_without_bom.decode('utf-8'))  # Преобразование данных в объект Python

            headers = {
                'Authorization': f'Basic {credentials}',
                "Content-Type": "application/json, charset=utf-8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
            item_request = requests.post(site_url, json=send_data_without_bom, headers=headers)

            new_items = item_request.json()
            try:
                for item in new_items:
                    # existing_item = models.Item.objects.filter(name=item['Наименование']).first()
                    # if existing_item:
                    #     existing_item.code = item['НаименованиеКод']
                    #     existing_item.save()
                    #     existing_item.quantity = item['КоличествоОстаток']
                    #     existing_item.save()
                    # else:
                    #     pass
                    existing_item = models.Item.objects.filter(code=item['НаименованиеКод']).first()
                    if not existing_item:
                        new_item = models.Item.objects.create(name=item['Наименование'], code=item['НаименованиеКод'],
                                                              quantity=item['КоличествоОстаток'], photo='', costIn=0,
                                                              category=None, author='Бай Элим')
                    else:
                        existing_item.quantity = item['КоличествоОстаток']
                        existing_item.save()

                item_request = requests.post(second_site_url, json=send_data_without_bom, headers=headers)
                second_new_items = item_request.json()

                for item in second_new_items:
                    existing_item = models.Item.objects.filter(code=item['НаименованиеКод']).first()
                    if not existing_item:
                        new_item = models.Item.objects.create(name=item['Наименование'], code=item['НаименованиеКод'],
                                                              quantity=item['КоличествоОстаток'], photo='', costIn=0,
                                                              category=None, author='Органик')
                    else:
                        existing_item.quantity = item['КоличествоОстаток']
                        existing_item.save()
                return Response({"status": 'ok'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'status': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SynchronizeAgentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.data['target'] == 'synchronize':
            site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
            data = {"Table": "Агенты"}
            username = 'Techtoo'
            password = '123'
            credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            send_data_json = json.dumps(data)  # Преобразование словаря send_data в JSON строку
            send_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты

            send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)  # Удаление BOM символов из данных

            send_data_without_bom = json.loads(
                send_data_json_bytes_without_bom.decode('utf-8'))  # Преобразование данных в объект Python

            headers = {
                'Authorization': f'Basic {credentials}',
                "Content-Type": "application/json, charset=utf-8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
            agent_request = requests.post(site_url, json=send_data_without_bom, headers=headers)
            new_agents = agent_request.json()

            try:
                for agent in new_agents:
                    existing_agent = models.Agent.objects.filter(oneC_code=agent['Код']).first()
                    if not existing_agent:
                        new_agent = models.Agent.objects.create(
                            name=agent['Наименование'], login=agent['Код'], oneC_code=agent['Код']
                        )
                        new_agent.set_password(agent['Код'])
                        new_agent.save()
                    else:
                        existing_agent.name = agent['Наименование']
                        existing_agent.save()
                return Response({"status": 'ok'}, status=status.HTTP_200_OK)
            except:
                return Response({'status': 'wrong data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SynchronizeDriversView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if request.data['target'] == 'synchronize':
            site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
            data = {"Table": "Водители"}
            username = 'Techtoo'
            password = '123'
            credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            send_data_json = json.dumps(data)  # Преобразование словаря send_data в JSON строку
            send_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты

            send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)  # Удаление BOM символов из данных

            send_data_without_bom = json.loads(
                send_data_json_bytes_without_bom.decode('utf-8'))  # Преобразование данных в объект Python

            headers = {
                'Authorization': f'Basic {credentials}',
                "Content-Type": "application/json, charset=utf-8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
            driver_request = requests.post(site_url, json=send_data_without_bom, headers=headers)
            new_drivers = driver_request.json()

            try:
                for driver in new_drivers:
                    existing_driver = models.Driver.objects.filter(oneC_code=driver['Код']).first()
                    if not existing_driver:
                        new_driver = models.Driver.objects.create(
                            name=driver['Наименование'], login=driver['Код'], oneC_code=driver['Код']
                        )
                        new_driver.set_password(driver['Код'])
                        new_driver.save()
                    else:
                        existing_driver.name = driver['Наименование']
                        existing_driver.save()
                return Response({"status": 'ok'}, status=status.HTTP_200_OK)
            except:
                return Response({'status': 'wrong data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SynchronizeStoresView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if request.data['target'] == 'synchronize':
            site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
            data = {"Table": "Покупатели"}
            username = 'Techtoo'
            password = '123'
            credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            send_data_json = json.dumps(data)  # Преобразование словаря send_data в JSON строку
            send_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты

            send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)  # Удаление BOM символов из данных

            send_data_without_bom = json.loads(
                send_data_json_bytes_without_bom.decode('utf-8'))  # Преобразование данных в объект Python

            headers = {
                'Authorization': f'Basic {credentials}',
                "Content-Type": "application/json, charset=utf-8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
            store_request = requests.post(site_url, json=send_data_without_bom, headers=headers)
            # with open('/home/timur/baielim/stores.json', 'r', encoding='utf-8') as file:
            #     store_request = json.load(file)

            new_stores = store_request.json()

            try:
                for store in new_stores:
                    existing_store = models.Store.objects.filter(oneC_code=store['Код']).first()
                    if existing_store:
                        existing_store.guid = store['Guid']
                        existing_store.save()
                    if not existing_store:
                        new_store = models.Store.objects.create(
                            name=store['Наименование'], login=store['Код'], oneC_code=store['Код'], guid=store['Guid']
                        )
                        new_store.set_password(store['Код'])
                        new_store.save()
                    else:
                        existing_store.guid = store['Guid']
                        existing_store.save()
                return Response({"status": 'ok'}, status=status.HTTP_200_OK)
            except:
                return Response({'status': 'wrong data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class SynchronizeOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        orders_id = request.data['orders']
        response_data = create_items_in_OneC(orders_id)
        # orders = []
        # orders_obj = []
        # for order_id in orders_id:
        #     order = models.Order.objects.get(id=order_id)
        #     orders_obj.append(order)
        #     if order:
        #         # current_datetime = datetime.now()
        #         current_datetime = order.dateCreated
        #         current_weekday = current_datetime.weekday()
        #
        #         created_date = order.dateCreated.strftime('%Y%m%d%H%M%S')
        #
        #         if order.shipping_date is None or order.shipping_date == '':
        #             additional_days = 2
        #             if current_weekday in (3, 4):  # Четверг - 3, Пятница - 4
        #                 additional_days = 4
        #             shipping_date = (order.dateCreated + timedelta(days=additional_days)).strftime('%Y%m%d%H%M%S')
        #         else:
        #             shipping_date = order.shipping_date.strftime('%Y%m%d%H%M%S')
        #
        #         items = order.items.all()
        #         items_data = []
        #         for i in items:
        #             item_data = {
        #                 "НаименованиеКод": f"{i.item.code}",
        #                 "Количество": f"{i.count}",
        #                 "цена": f"{i.soldCost}"
        #             }
        #             items_data.append(item_data)
        #         guid = '00000000-0000-0000-0000-'
        #         guid_id = order.id
        #         txt = str(guid_id).zfill(12)
        #         guid = guid + txt
        #         order_data = {
        #             'guid': guid,
        #             'номер': f'{order.id}',
        #             'дата': f'{created_date}',
        #             'ПокупательКод': f'{order.store.oneC_code}',
        #             'АгентКод': f'{order.agent.oneC_code}',
        #             'Комментарий': f"{order.comment}",
        #             'Товары': items_data,
        #             'ДатаОтгрузки': shipping_date,
        #             'ТипЦены': order.costType.one_guid
        #         }
        #         orders.append(order_data)
        #
        # data = {
        #     "Table": "Заказы",
        #     "orders": orders
        # }
        # file = open('debug.txt', 'w')
        # file.write(str(data))
        #
        # response_data = post_request_to_OneC(data)
        if response_data == 'success':
            for local_id in orders_id:
                order = models.Order.objects.get(id=local_id)
                order.is_sync_oneC = True
                order.save()
            return Response({'response': response_data}, status=status.HTTP_200_OK)
        else:
            return Response({'response': response_data}, status=status.HTTP_400_BAD_REQUEST)


class TransactionOrderViewSet(viewsets.ModelViewSet):
    queryset = models.TransactionOrder.objects.all()
    serializer_class = serializers.TransactionOrderSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.TransactionOrderFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.TransactionOrderSerializerGet
        else:
            return serializers.TransactionOrderSerializer


class CountOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        data = request.data
        order_status = data.get('status')
        store_id = data.get('store')
        agent_id = data.get('agent')
        driver_id = data.get('driver')
        payment_statuses = data.get('paymentStatuses')
        costType_id = data.get('costType')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        orders = models.Order.objects.all()
        if order_status:
            orders = orders.filter(status=order_status)
        if store_id:
            orders = orders.filter(store_id=store_id)
        if agent_id:
            orders = orders.filter(agent_id=agent_id)
        if driver_id:
            orders = orders.filter(driver_id=driver_id)
        if payment_statuses:
            pay_statuses = payment_statuses.split(',')
            orders = orders.filter(paymentStatus__in=pay_statuses)
        if costType_id:
            orders = orders.filter(costType_id=costType_id)
        try:
            # start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            # end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if start_date and end_date:
                if start_date == end_date:
                    orders = orders.filter(dateCreated__date=start_date)
                else:
                    orders = orders.filter(dateCreated__date__gte=start_date, dateCreated__date__lte=end_date)

        except ValueError:
            return Response({'status': 'error date!'}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = orders.aggregate(total_cost=Sum('totalCost'))['total_cost'] or 0

        # Сначала получаем все связанные элементы заказов и затем агрегируем их количество
        items_count = orders.aggregate(items_count=Sum('items__count'))['items_count'] or 0

        # total_cost = 0
        # items_count = 0
        # for order in orders:
        #     total_cost += order.totalCost
        #     items = order.items.all()
        #     for item in items:
        #         items_count += item.count

        return Response({'totalCost': total_cost, 'itemsCount': items_count})


class OrderHistoryViewSet(viewsets.ModelViewSet):
    queryset = models.OrderHistory.objects.all()
    serializer_class = serializers.OrderHistorySerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.OrderHistoryFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.OrderHistorySerializerGet
        else:
            return serializers.OrderHistorySerializer


from django.db.models import Count
from django.db.models.functions import TruncDate


class OrdersStatisticView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        data = request.data
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        store_id = data.get('store')
        agent_id = data.get('agent')
        cost_type_id = data.get('costType')
        if not (end_date and start_date):
            end_date = datetime.today()
            start_date = end_date - timedelta(days=30)

        orders = models.Order.objects.all().filter(dateCreated__gte=start_date, dateCreated__lte=end_date)
        if cost_type_id:
            orders = orders.filter(costType_id=cost_type_id)

        if store_id and agent_id:
            agent_name = None
            orders = orders.filter(agent_id=agent_id)
            agent = models.Agent.objects.get(id=agent_id)
            agent_name = agent.name
            store_name = None
            orders = orders.filter(store_id=store_id)
            store = models.Store.objects.get(id=store_id)
            store_name = store.name
            grouped_orders = orders.annotate(date=TruncDate('dateCreated')).values(
                'date', 'store__name', 'agent__name', ).annotate(
                count=Count('id'), total_cost=Sum('totalCost')).order_by('date')

        elif store_id:
            store_name = None
            orders = orders.filter(store_id=store_id)
            store = models.Store.objects.get(id=store_id)
            store_name = store.name
            grouped_orders = orders.annotate(date=TruncDate('dateCreated')).values(
                'date', ).annotate(count=Count('id'), total_cost=Sum('totalCost')).order_by('date')

        elif agent_id:
            agent_name = None
            orders = orders.filter(agent_id=agent_id)
            agent = models.Agent.objects.get(id=agent_id)
            agent_name = agent.name
            grouped_orders = orders.annotate(date=TruncDate('dateCreated')).values(
                'date',).annotate(count=Count('id'), total_cost=Sum('totalCost')).order_by('date')

        else:
            # grouped_orders = (orders.annotate(date=TruncDate('dateCreated')).values(
            #     'date', ).annotate(count=Count('id')).order_by('date'))

            grouped_orders = (orders.annotate(date=TruncDate('dateCreated')).values('date').annotate(
                count=Count('id'), total_cost=Sum('totalCost')).order_by('date'))

        return Response({'data': grouped_orders}, status=status.HTTP_200_OK)


class GetAllItemsView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request):
        queryset = models.Item.objects.all()
        serializer = serializers.ItemAllSerializer(queryset, many=True)
        return Response(serializer.data)


class ItemCountView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        filters = Q()  # Инициализация пустого Q объекта для накопления фильтров

        order_status = data.get('status')
        store_id = data.get('store')
        agent_id = data.get('agent')
        driver_id = data.get('driver')
        payment_statuses = data.get('paymentStatuses')
        costType_id = data.get('costType')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Применение фильтров, если параметры переданы
        if order_status:
            filters &= Q(status=order_status)
        if store_id:
            filters &= Q(store_id=store_id)
        if agent_id:
            filters &= Q(agent_id=agent_id)
        if driver_id:
            filters &= Q(driver_id=driver_id)
        if payment_statuses:
            pay_statuses = payment_statuses.split(',')
            filters &= Q(paymentStatus__in=pay_statuses)
        if costType_id:
            filters &= Q(costType_id=costType_id)

        # Фильтрация по диапазону дат
        if start_date and end_date:
            try:
                if start_date == end_date:
                    filters &= Q(dateCreated__date=start_date)
                else:
                    filters &= Q(dateCreated__date__gte=start_date, dateCreated__date__lte=end_date)
            except ValueError:
                return Response({'status': 'Некорректная дата!'}, status=status.HTTP_400_BAD_REQUEST)

        # Применение всех фильтров
        orders = models.Order.objects.filter(filters)

        # Сбор данных по элементам заказов
        item_data = {}
        for order in orders.prefetch_related('items__item'):  # Используем prefetch_related для оптимизации запросов
            for item in order.items.all():
                item_name = getattr(item.item, 'name', 'Пустой')
                if item_name not in item_data:
                    item_data[item_name] = {'count': 0, 'totalCost': 0}
                item_data[item_name]['count'] += item.count
                item_data[item_name]['totalCost'] += (item.soldCost * item.count)

        return Response(item_data, status=status.HTTP_200_OK)

    # def post(self, request):
    #     data = request.data
    #     order_status = data.get('status')
    #     store_id = data.get('store')
    #     agent_id = data.get('agent')
    #     driver_id = data.get('driver')
    #     payment_statuses = data.get('paymentStatuses')
    #     costType_id = data.get('costType')
    #     start_date = data.get('start_date')
    #     end_date = data.get('end_date')
    #     orders = models.Order.objects.all()
    #     if order_status:
    #         orders = orders.filter(status=order_status)
    #         return Response({'testing': 'ok', 'orders': len(orders)})
    #     if store_id:
    #         orders = orders.filter(store_id=store_id)
    #     if agent_id:
    #         orders = orders.filter(agent_id=agent_id)
    #     if driver_id:
    #         orders = orders.filter(driver_id=driver_id)
    #     if payment_statuses:
    #         pay_statuses = payment_statuses.split(',')
    #         orders = orders.filter(paymentStatus__in=pay_statuses)
    #     if costType_id:
    #         orders = orders.filter(costType_id=costType_id)
    #     try:
    #         if start_date and end_date:
    #             if start_date == end_date:
    #                 orders = orders.filter(dateCreated__date=start_date)
    #             else:
    #                 orders = orders.filter(dateCreated__date__gte=start_date, dateCreated__date__lte=end_date)
    #
    #     except ValueError:
    #         return Response({'status': 'error date!'}, status=status.HTTP_400_BAD_REQUEST)
    #     item_data = {}
    #
    #     for order in orders:
    #         for item in order.items.all():
    #             try:
    #                 item_name = item.item.name
    #             except:
    #                 item_name = "Пустой"
    #             if item_name not in item_data:
    #                 item_data[item_name] = {'count': 0, 'totalCost': 0}
    #             item_data[item_name]['count'] += item.count
    #             item_data[item_name]['totalCost'] += (item.soldCost * item.count)
    #     return Response(item_data, status=status.HTTP_200_OK)


class TotalCountOfOrdersView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get(self, request):
        orders = models.Order.objects.all()

        response_data = {}
        active_orders = orders.filter(status='new')
        active_orders_count = active_orders.count()
        active_orders_sum = active_orders.aggregate(Sum('totalCost'))
        response_data['active_orders'] = {'count': active_orders_count, 'sum': active_orders_sum}

        archived_orders = orders.filter(status='archive')
        archived_orders_count = archived_orders.count()
        archived_orders_sum = archived_orders.aggregate(Sum('totalCost'))
        response_data['archive_orders'] = {'count': archived_orders_count, 'sum': archived_orders_sum}

        today_orders = orders.filter(dateCreated__date=timezone.now().date())
        today_orders_count = today_orders.count()
        today_orders_sum = today_orders.aggregate(Sum('totalCost'))
        response_data[f'today'] = {'count': today_orders_count, 'sum': today_orders_sum}
        return Response(response_data, status=status.HTTP_200_OK)


class MarginalityView(APIView):
    permission_classes = (permissions.AllowAny, )
    authentication_classes = (JWTAuthentication, )

    def get(self, request):
        # items = models.Item.objects.filter(costIn__gt=0)
        items = models.Item.objects.annotate(num_costs=Count('costs')).filter(num_costs__gt=0)
        response_data = []

        for item in items:
            data = {'name': item.name, 'marginality': 0}
            costs = item.costs.all().filter(cost__gt=0)
            if costs:
                avg_cost = costs.aggregate(avg_cost=Avg('cost'))['avg_cost']
            else:
                avg_cost = 0
            # avg_cost = cost.aggregate(Sum('cost')) / len(cost)
            marginality = avg_cost - item.costIn
            data['marginality'] = marginality
            response_data.append(data)

        return Response({'data': response_data}, status=status.HTTP_200_OK)


class SynchronizeCostView(APIView):
    permission_classes = (permissions.AllowAny, )
    authentication_classes = (JWTAuthentication, )

    def post(self, request):
        site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
        second_site_url = 'http://212.112.127.164:8080/Exchange2025organic/hs/getTables/data'
        today_start = datetime.now().strftime('%Y%m%d') + '000000'
        data = {"Table": "Прайс", "DateStart": today_start}
        username = 'Techtoo'
        password = '123'
        credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
        send_data_json = json.dumps(data)
        send_data_json_bytes = send_data_json.encode('utf-8')
        send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)
        send_data_without_bom = json.loads(
            send_data_json_bytes_without_bom.decode('utf-8'))
        headers = {
            'Authorization': f'Basic {credentials}',
            "Content-Type": "application/json, charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        cost_request = requests.post(site_url, json=send_data_without_bom, headers=headers)

        organic_cost_request = requests.post(second_site_url, json=send_data_without_bom, headers=headers)

        new_costs = cost_request.json()
        organic_new_cost = organic_cost_request.json()

        for i in new_costs:
            item = models.Item.objects.filter(code=i.get('НоменклатураКод')).first()
            if item is not None:
                costs = item.costs.all().filter(costType__one_guid=i.get('GuidТипЦен'))

                if len(costs) > 0:
                    cost_ob = costs.first()
                    cost_ob.cost = i.get('Цена')
                    cost_ob.save()
            else:
                pass

        for j in organic_new_cost:
            item = models.Item.objects.filter(code=j.get('НоменклатураКод')).first()
            if item is not None:
                costs = item.costs.all().filter(costType__guid_organic=j.get('GuidТипЦен'))

                if len(costs) > 0:
                    cost_ob = costs.first()
                    cost_ob.cost = j.get('Цена')
                    cost_ob.save()
            else:
                pass

        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class DriversItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        driver_id = request.data.get('driver')
        orders = models.Order.objects.filter(driver_id=driver_id, status='new').prefetch_related('items__item')
        response_data = defaultdict(int)
        response = []

        for order in orders:
            for item in order.items.all():
                if item.item and item.item.name:
                    response_data[item.item.name] += item.count
                else:
                    response_data['Unknown Item'] += item.count

        for i in response_data:
            response.append({'name': i, 'count': response_data[i]})

        return Response(response)


class ListOfStoresSellingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        total_start = request.data.get('totalStart')
        total_end = request.data.get('totalEnd')
        dateStart = request.data.get('dateStart')
        dateEnd = request.data.get('dateEnd')

        try:
            total_start = float(total_start) if total_start else 0
            total_end = float(total_end) if total_end else float('inf')

            orders = models.Order.objects.all()

            if dateStart and dateEnd:
                orders = orders.filter(dateCreated__date__range=(dateStart, dateEnd))

            orders = orders.values('store__name').annotate(total=Sum('totalCost')).filter(
                total__gte=total_start, total__lte=total_end
            )

            response_data = [{'storeName': order['store__name'], 'total': order['total']} for order in orders]

            return Response({'data': response_data}, status=200)

        except ValueError:
            return Response({'error': 'Invalid totalStart or totalEnd'}, status=400)


class DriversStoresView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response({"error": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        orders = models.Order.objects.filter(status='new', driver_id=driver_id)
        if not orders.exists():
            return Response({"error": "No orders found for the given driver_id"}, status=status.HTTP_404_NOT_FOUND)

        items_data = (
            models.OrderItem.objects.filter(order__in=orders)
            .values("item__name")
            .annotate(quantity=Sum("count"))
            .order_by("item__name")
        )

        response_data = [{"item": item["item__name"], "quantity": int(item["quantity"])} for item in items_data]

        return Response(response_data, status=status.HTTP_200_OK)


class OrdersByDateAndCostAPIView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        date_start = request.data.get('dateStart')
        date_end = request.data.get('dateEnd')
        start_sum = request.data.get('startSum')
        end_sum = request.data.get('endSum')

        if not date_start or not date_end or start_sum is None or end_sum is None:
            return Response({"error": "dateStart, endDate, startSum, and endSum are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            orders = models.Order.objects.filter(
                dateCreated__date__range=[date_start, date_end]
            ).values('store__id', 'store__name', 'store__address').annotate(
                soldCost=Sum('totalCost')
            ).filter(soldCost__gte=start_sum, soldCost__lte=end_sum)

            # Формирование ответа
            response_data = [
                {
                    "store": {
                        "id": order['store__id'],
                        "name": order['store__name'],
                        "address": order['store__address']
                    },
                    "soldCost": order['soldCost']
                }
                for order in orders
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

