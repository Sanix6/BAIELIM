import base64
import requests
import json
from datetime import datetime, timedelta

from core import models


def get_next_monday():
    today = datetime.today()
    days_ahead = 0 - today.weekday() + 7
    next_monday = today + timedelta(days=days_ahead)
    return next_monday.date()


def remove_bom_from_json(json_data):
    json_text = json_data.decode('utf-8-sig')  # Декодируем текст в кодировке UTF-8-sig, удаляя BOM символы
    json_object = json.loads(json_text)  # Преобразуем текст JSON в объект Python
    return json_object


def remove_bom(data):
    bom_chars = [b'\xef\xbb\xbf', b'\xff\xfe']  # UTF-8 и UTF-16 BOM символы

    for bom in bom_chars:
        if data.startswith(bom):
            data = data[len(bom):]
            break

    return data


def post_request_to_OneC(data):
    site_url = 'http://212.112.127.164:8080/Exchange2025/hs/postTables/data'
    second_site_url = 'http://212.112.127.164:8080/Exchange2025organic/hs/postTables/data'
    username = 'Techtoo'
    password = '123'
    credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    send_data_json = json.dumps(data['БайЭлим'])
    send_data_json_bytes = send_data_json.encode('utf-8')

    send_data_json_bytes_without_bom = remove_bom(
        send_data_json_bytes)

    send_data_without_bom = json.loads(
        send_data_json_bytes_without_bom.decode('utf-8'))

    headers = {
        'Authorization': f'Basic {credentials}',
        "Content-Type": "application/json, charset=utf-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    item_request = requests.post(site_url, json=send_data_without_bom, headers=headers)
    f = open('bElim_req_body.txt', 'w')
    f.write(str(send_data_without_bom))
    new_items = item_request.json()
    f = open('bElim_response.txt', 'w')
    f.write(str(new_items))
    flag = False
    if new_items['result'] == 'OK':
        flag = True

    if len(data['Органик']['orders']) != 0:
        send_data_json = json.dumps(data['Органик'])  # Преобразование словаря send_data в JSON строку
        ssend_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты

        ssend_data_json_bytes_without_bom = remove_bom(
            ssend_data_json_bytes)  # Удаление BOM символов из данных

        ssend_data_without_bom = json.loads(
            ssend_data_json_bytes_without_bom.decode('utf-8'))

        second_item_request = requests.post(second_site_url, json=ssend_data_without_bom, headers=headers)
        f = open('organic_req_body.txt', 'w')
        f.write(str(ssend_data_without_bom))
        second_new_items = second_item_request.json()
        f = open('organic_response.txt', 'w')
        f.write(str(second_new_items))

        if second_new_items['result'] == 'OK':
            if flag:
                return 'success'

        return 'fail'
    else:
        if flag:
            return 'success'


def create_items_in_OneC(orders_id):
    orders = []
    orders_second = []
    orders_obj = []
    for order_id in orders_id:
        order = models.Order.objects.get(id=order_id)
        orders_obj.append(order)
        if order:
            # current_datetime = datetime.now()
            # created_date = order.dateCreated.strftime('%Y%m%d%H%M%S')

            current_datetime = order.dateCreated
            current_weekday = current_datetime.weekday()

            created_date = order.dateCreated.strftime('%Y%m%d%H%M%S')

            if order.shipping_date is None or order.shipping_date == '':
                additional_days = 2
                if current_weekday in (3, 4):  # Четверг - 3, Пятница - 4
                    additional_days = 4
                shipping_date = (order.dateCreated + timedelta(days=additional_days)).strftime('%Y%m%d%H%M%S')
            else:
                shipping_date = order.shipping_date.strftime('%Y%m%d%H%M%S')

            items = order.items.all()
            items_data = []
            second_items_data = []
            for i in items:
                if i.item.author == 'Органик':
                    item_data = {
                        "НаименованиеКод": i.item.code,
                        "Количество": f"{i.count}",
                        "цена": f"{i.soldCost}"
                    }
                    items_data.append(item_data)
                else:
                    second_item_data = {
                        "НаименованиеКод": i.item.code,
                        "Количество": f"{i.count}",
                        "цена": f"{i.soldCost}"
                    }
                    second_items_data.append(second_item_data)
            guid = '40000000-0000-0000-0000-'
            guid_id = order.id
            txt = str(guid_id).zfill(12)
            guid = guid + txt
            order_data = {
                'guid': guid,
                'номер': f'{order.id}',
                'дата': f'{created_date}',
                'ПокупательКод': f'{order.store.oneC_code}',
                'АгентКод': f'{order.agent.oneC_code}',
                'Комментарий': f"{order.comment}",
                'Товары': items_data,
                'ДатаОтгрузки': shipping_date,
                'ТипЦены': order.costType.one_guid
            }
            if len(items_data) != 0:
                orders.append(order_data)

            second_order_data = {
                'guid': guid,
                'номер': f'{order.id}',
                'дата': f'{created_date}',
                'ПокупательКод': f'{order.store.oneC_code}',
                'АгентКод': f'{order.agent.oneC_code}',
                'Комментарий': f"{order.comment}",
                'Товары': second_items_data,
                'ДатаОтгрузки': shipping_date,
                'ТипЦены': order.costType.one_guid
            }
            if len(second_items_data) != 0:
                orders_second.append(second_order_data)

    data = {
        "Table": "Заказы",
        "orders": orders
    }

    second_data = {
        "Table": "Заказы",
        "orders": orders_second
    }

    send_data = {'Органик': data, 'БайЭлим': second_data}
    response_data = post_request_to_OneC(send_data)
    f = open('send_data.txt', 'w')
    f.write(str(send_data))
    return response_data

# bc = models.CostType.objects.get(pk=1)
# bc_opt = models.CostType.objects.get(pk=9)
# opt = models.CostType.objects.get(pk=8)
# opt_alm_osh = models.CostType.objects.get(pk=5)
# skidka_svyshe = models.CostType.objects.get(pk=10)
# market_bez_nalog = models.CostType.objects.get(pk=7)


# def sync_items_price():
#     # items = models.Item.objects.all()
#     with open(f'/home/timur/baielim/shtrih_code.json', 'r') as input_file:
#         new_items = json.load(input_file)
#
#     oneC_items = new_items['Лист1']
#     for item in oneC_items:
#         our_item = models.Item.objects.filter(name=item['Товар']).first()
#         costs = []
#         if our_item:
#             if item['ВС'] is not None:
#                 first_cost = models.Cost.objects.create(cost=item['ВС'], costType=bc)
#                 costs.append(first_cost)
#             if item['ВС Опт'] is not None:
#                 second_cost = models.Cost.objects.create(cost=item['ВС Опт'], costType=bc_opt)
#                 costs.append(second_cost)
#             if item['Оптовые'] is not None:
#                 third_cost = models.Cost.objects.create(cost=item['Оптовые'], costType=opt)
#                 costs.append(third_cost)
#             if item['Оптовые Аламедин Ош Орто Сай'] is not None:
#                 fourth_cost = models.Cost.objects.create(cost=item['Оптовые Аламедин Ош Орто Сай'],
#                                                          costType=opt_alm_osh)
#                 costs.append(fourth_cost)
#             if item['со скидкой -свше 100кор.'] is not None:
#                 fifth_cost = models.Cost.objects.create(cost=item['со скидкой -свше 100кор.'], costType=skidka_svyshe)
#                 costs.append(fifth_cost)
#             if item['Маркеты без налогов'] is not None:
#                 sixth_cost = models.Cost.objects.create(cost=item['Маркеты без налогов'], costType=skidka_svyshe)
#                 costs.append(sixth_cost)
#             our_item.costs.set(costs)
#             our_item.save()
