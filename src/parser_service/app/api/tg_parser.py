import base64
import os
from dotenv import load_dotenv
from pyrogram import Client

from src.supervisor.app.api.scheme import Message


load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHAT = os.getenv("CHAT")

DIR_PATH = "downloaded_images"


async def download_image(app, message):
    """ Скачивание картинки из сообщения и ее кодирование """
    try:
        photo = message.photo or (message.document and message.document.photo)
        file_id = photo.file_id
        file_path = await app.download_media(file_id, file_name=f"{DIR_PATH}/{message.id}.jpg")

        with open(file_path, "rb") as file:
            file_data = file.read()

        # Кодируем данные изображения в строку Base64
        image_base64 = base64.b64encode(file_data).decode('utf-8')
        return image_base64
    except:
        return None
    finally:
        print(f"Сообщение TG:{message.id}")


async def process_message(app, message):
    """ Извлечение из сообщения необходимых данных """
    downloaded_file_data = await download_image(app, message)
    text = message.caption if message.caption else message.text
    user = message.from_user.first_name if message.from_user else message.sender_chat.title
    return Message(
        id=message.id,
        source="tg",
        date=message.date,
        from_user=user,
        text=text,
        image=downloaded_file_data
    )


async def get_limit(app, last_message_id):
    """ Определение колличества сообщений для парсинга """
    # Считывание из истории сообщений чата последнее сообщение, чтобы узнать его id
    async for message in app.get_chat_history(CHAT, limit=1):
        last_new_message_id = message.id

    # Вычисляем сколько сообщений необходимо спарсить, чтобы получить все новые сообщения
    limit = last_new_message_id - last_message_id
    print("Последнее сообщение в чате:", last_new_message_id, "\nКоличество новых сообщений:", limit)

    return limit


async def get_messages(last_message_id):
    """ Парсинг новых сообщений """
    app = Client("CM_HCS_account", api_id=API_ID, api_hash=API_HASH, phone_number=SESSION)
    async with app:
        limit = await get_limit(app, last_message_id)

        messages = []
        if limit > 0:
            async for message in app.get_chat_history(CHAT, limit=limit):
                message_info = await process_message(app, message)
                messages.append(message_info)

        return messages


if __name__ == "__main__":
    os.makedirs(DIR_PATH, exist_ok=True)
