import base64
import requests, json

from baiElim.settings import BASE_DIR
from core.views import remove_bom
from user import models


def sync_with_oneC():
    site_url = 'http://212.112.127.164:8080/Exchange2025/hs/getTables/data'
    data = {"Table": "Покупатели"}
    username = 'Techtoo'
    password = '123'
    credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    send_data_json = json.dumps(data)  
    send_data_json_bytes = send_data_json.encode('utf-8') 

    send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes) 

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
    new_stores = store_request.json()

    try:
        for store in new_stores:
            existing_store = models.Store.objects.filter(oneC_code=store['Код']).first()
            if not existing_store:
                new_store = models.Store.objects.create(
                    name=store['Наименование'], login=store['Код'], oneC_code=store['Код']
                )
                new_store.set_password(store['Код'])
                new_store.save()
            else:
                pass
        return 'success'
        # existing_store.name = store['Наименование']
        # existing_store.save()
    except:
        return 'wrong'


def import_stores():
    with open(f'/home/timur/baielim/stores.json', 'r') as input_file:
        new_stores = json.load(input_file)
    # new_stores = store_request.json()

    for store in new_stores:
        new_store = models.Store.objects.create(
            name=store['Наименование'], login=store['Код'], oneC_code=store['Код']
        )
        new_store.set_password(store['Код'])
        new_store.save()
        # existing_store = models.Store.objects.filter(oneC_code=store['Код']).first()
        # if not existing_store:
        #
        # else:
        #     pass
    return 'success'


def import_costTypes():
    with open(f'/home/timur/baielim/storlor_epta.json', 'r') as input_file:
        data = json.load(input_file)
        # agent = models.Agent.objects.get(pk=59)
        cost_type = models.CostType.objects.get(pk=8)


        for items in data:
            for store in data[items]:
                store = models.Store.objects.filter(oneC_code=store['Код']).first()
                if store:
                    store.costType = cost_type
                    store.save()

                # code = store['Код']
                # name = store['Наименование']
                # is_costType = store['Тип цен осн дог']
                # if is_costType:
                #     if store['Тип цен осн дог'] == 'ВС':
                #         cost_type = models.CostType.objects.get(pk=1)
                #     elif store['Тип цен осн дог'] == 'ВС опт':
                #         cost_type = models.CostType.objects.get(pk=9)
                #     elif store['Тип цен осн дог'] == 'Оптовые':
                #         cost_type = models.CostType.objects.get(pk=8)
                #     elif store['Тип цен осн дог'] == 'Маркеты с налогами':
                #         cost_type = models.CostType.objects.get(pk=7)
                #     elif store['Тип цен осн дог'] == 'Оптовая Аламед,Ош,Орто-Са':
                #         cost_type = models.CostType.objects.get(pk=5)
                #     else:
                #         cost_type = None
                # try:
                #     our_store = models.Store.objects.filter(oneC_code=code).first()
                #     if our_store:
                #         if is_costType:
                #             our_store.costType = cost_type
                #         # our_store.store_agent = agent
                #         our_store.save()
                #     else:
                #         new_store = models.Store.objects.create(
                #             login=code, name=name,
                #             oneC_code=code, store_agent_id=59
                #         )
                #         if is_costType:
                #             new_store.costType = cost_type
                #         new_store.set_password(code)
                #         new_store.save()
                # except:
                #     pass


def sync_with_oneC():
    stores = models.Store.objects.all().filter(dateCreated__date__gte='2024-07-01')
    data = []
    for store in stores:
        if store.name:
            name = store.name
        else:
            name = ''

        if store.address:
            address = store.address
        else:
            address = ''

        if store.phoneNumber:
            phoneNumber = store.phoneNumber
        else:
            phoneNumber = ''

        if store.store_agent:
            agent_name = store.store_agent.name
        else:
            agent_name = ''
        data_store = {
            "guid": store.guid,
            "Код": store.oneC_code,
            "Наименование": f"{name}, {address}, {phoneNumber}",
            "Комментарий": f'{agent_name}'
        }
        data.append(data_store)
    send_data = {
        "Table": "Покупатели",
        "Покупатели": data
    }

    site_url = 'http://212.112.127.164:8080/Exchange2025/hs/postTables/data'
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



def create_store_inOneC(id, name, agent_name, phoneNumber, address):
    site_url = 'http://212.112.127.164:8080/Exchange2025/hs/postTables/data'
    second_site_url = 'http://212.112.127.164:8080/Exchange2025organic/hs/postTables/data'
    guid = '00000000-0000-0000-0000-'
    txt = str(id).zfill(12)
    guid = guid + txt
    int_code = 10000 + id
    code = name[0:3] + str(int_code)
    if len(code) < 9:
        result_string = code.ljust(9, 'x')
    else:
        result_string = code[:9]
    data = {
        "Table": "Покупатели",
        "Покупатели": [{
            "Guid": guid,
            "Код": result_string,
            "Наименование": f"{name}, {address}, {phoneNumber}",
            "Комментарий": f'{agent_name}'
        }]
    }
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
    store_organic_request = requests.post(second_site_url, json=send_data_without_bom, headers=headers)

    logs = models.UsersLog.objects.create(user_name=name, user_id=id, request_body=str(data),
                                          bElim_response_body=str(store_request.json()),
                                          organic_response_body=str(store_organic_request.json()))
    response = store_request.json()
    response_code = store_request.status_code
    second_response_code = store_organic_request.status_code
    response_data = {'code': [response_code, second_response_code], 'response': response, 'data': data}
    return response_data


def create_stores_inOneC(stores):
    site_url = 'http://212.112.127.164:8080/Exchange2025/hs/postTables/data'
    second_site_url = 'http://212.112.127.164:8080/Exchange2025organic/hs/postTables/data'
    send_stores = []
    for store in stores:
        guid = '00000000-0000-0000-0000-'
        txt = str(store.id).zfill(12)
        guid = guid + txt
        int_code = 10000 + store.id
        code = store.name[0:3] + str(int_code)
        if len(code) < 9:
            result_string = code.ljust(9, 'x')
        else:
            result_string = code[:9]
        send_store = {
            "Guid": guid,
            "Код": result_string,
            "Наименование": f"{store.name}, {store.address}, {store.phoneNumber}",
            "Комментарий": f'{store.store_agent}'
        }
        send_stores.append(send_store)

    data = {
        "Table": "Покупатели",
        "Покупатели": send_stores
    }
    # username = 'Techtoo'
    # password = '123'
    # credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    # send_data_json = json.dumps(data)  # Преобразование словаря send_data в JSON строку
    # send_data_json_bytes = send_data_json.encode('utf-8')  # Кодирование JSON строки в байты
    #
    # send_data_json_bytes_without_bom = remove_bom(send_data_json_bytes)  # Удаление BOM символов из данных
    #
    # send_data_without_bom = json.loads(
    #     send_data_json_bytes_without_bom.decode('utf-8'))  # Преобразование данных в объект Python
    #
    # headers = {
    #     'Authorization': f'Basic {credentials}',
    #     "Content-Type": "application/json, charset=utf-8",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Accept": "*/*",
    #     "Connection": "keep-alive",
    # }
    # store_request = requests.post(site_url, json=send_data_without_bom, headers=headers)
    # store_organic_request = requests.post(second_site_url, json=send_data_without_bom, headers=headers)
    #
    # logs = models.UsersLog.objects.create(user_name=name, user_id=id, request_body=str(data),
    #                                       bElim_response_body=str(store_request.json()),
    #                                       organic_response_body=str(store_organic_request.json()))
    # response = store_request.json()
    # response_code = store_request.status_code
    # second_response_code = store_organic_request.status_code
    # response_data = {'code': [response_code, second_response_code], 'response': response}
    return data



def second_create_store_inOneC(objects):
    for i in objects:
        int_code = 10000 + i.id
        code = i.name[0:3] + str(int_code)
        if len(code) < 9:
            result_string = code.ljust(9, 'x')
        else:
            result_string = code[:9]
        i.oneC_code = result_string
        i.save()
