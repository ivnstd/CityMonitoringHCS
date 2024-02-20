import os
import httpx
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
GEOCODE_ADDRESS_URL = "https://geocode-maps.yandex.ru/1.x"


async def geocode(address):
    """ Геокодирование - получение координат объекта по его адресу """

    params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"
    }

    try:
        # Отправка GET-запроса к API Yandex Maps
        async with httpx.AsyncClient() as client:
            response = await client.get(GEOCODE_ADDRESS_URL, params=params)
            response.raise_for_status()  # Проверка на ошибки

        # Получение координат из ответа
        data = response.json()
        coordinates = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        latitude, longitude = map(float, coordinates.split())

        # Возвращение координат
        return {"latitude": latitude, "longitude": longitude}
    except Exception as e:
        print(f"Ошибка геокодирования {e}")
        return None
