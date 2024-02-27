import os
import httpx
from dotenv import load_dotenv
import asyncio

load_dotenv()

API_KEY = os.getenv("API_KEY")
GEOCODE_ADDRESS_URL = "https://geocode-maps.yandex.ru/1.x"
AREA = "51.36797765022104,45.439861987792945~51.71308855448513,46.57488701220701"

async def geocoding(address):
    """ Геокодирование - получение координат объекта по его адресу """

    params = {
        "apikey": API_KEY,
        "geocode": "Саратов, " + address,
        "bbox": AREA,
        "format": "json"
    }

    try:
        # Отправка GET-запроса к API Yandex Maps
        async with httpx.AsyncClient() as client:
            response = await client.get(GEOCODE_ADDRESS_URL, params=params)
            response.raise_for_status()  # Проверка на ошибки

        # Получение координат из ответа
        data = response.json()
        feature_member = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coordinates = feature_member["Point"]["pos"]
        full_address = feature_member["metaDataProperty"]["GeocoderMetaData"]["text"]
        # latitude, longitude = map(float, coordinates.split())

        # Возвращение адреса и координат
        return full_address, coordinates
    except Exception as e:
        print(f"Ошибка геокодирования {e}")
        return None, None


# async def main():
#     # print(await geocoding("Лунная 5 Саратов"))
#     print(await geocoding(None))
#
# asyncio.run(main())