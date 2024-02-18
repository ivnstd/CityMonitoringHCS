import httpx
import asyncio

async def geocode(address):
    GEOCODE_ADDRESS_URL = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "apikey": "ff38a83a-f02f-47c8-9546-b021ff235e96",
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
        raise {"Ошибка геокодирования": e}
