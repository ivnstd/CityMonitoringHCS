import os
import httpx
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
GEOCODE_ADDRESS_URL = "https://geocode-maps.yandex.ru/1.x"
AREA = "51.36797765022104,45.439861987792945~51.71308855448513,46.57488701220701"
CITY = "Саратов"
WEAK_ADDRESS = "Россия, Саратов"

async def geocoding(address):
    """ Геокодирование - получение координат объекта по его адресу """
    if not address:
        return None, None

    params = {
        "apikey": API_KEY,
        "geocode": f"{CITY}, {address}",
        "bbox": AREA,
        "format": "json"
    }

    # Отправка GET-запроса к API Yandex Maps
    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODE_ADDRESS_URL, params=params)
        response.raise_for_status()  # Проверка на ошибки

    try:
        # Получение координат из ответа
        data = response.json()
        feature_member = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coordinates = feature_member["Point"]["pos"]
        full_address = feature_member["metaDataProperty"]["GeocoderMetaData"]["text"]
    except Exception:
        return None, None

    # Возвращение адреса и координат
    if full_address != WEAK_ADDRESS:
        return full_address, coordinates
    else:
        return None, None
