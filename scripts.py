import sys
import os
import django
import pandas as pd
from .models import Store  

# Настройка окружения Django
sys.path.append("/home/timur/baielim")  # Корневая директория проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baiElim.settings')
django.setup()

def export_stores_to_excel():
    try:
        # Получаем данные из модели
        stores = Store.objects.all()

        # Преобразуем объекты модели в список словарей
        data = []
        for store in stores:
            data.append({
                "ID": store.id,
                "Контактное имя": store.contactName,
                "Район": store.region.name if store.region else "Не указан",
                "GUID": store.guid,
            })

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # Сохраняем данные в Excel
        df.to_excel("stores.xlsx", index=False, engine="openpyxl")
        print("Данные успешно экспортированы в файл stores.xlsx")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Вызов функции
if __name__ == "__main__":
    export_stores_to_excel()
