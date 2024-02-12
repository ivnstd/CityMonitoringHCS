from pyrogram import Client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHAT = os.getenv("CHAT")


class Message(BaseModel):
    id: int
    date: datetime
    from_user: str
    text: Optional[str] = None
    image_path: Optional[str] = None


async def download_image(app, message):
    try:
        download_path = f"downloaded_images/{message.id}.jpg"
        photo = message.photo or (message.document and message.document.photo)
        # Получение информации о медиа
        file_id = photo.file_id
        file_path = await app.download_media(file_id, file_name=download_path)
        return file_path
    except:
        # Сообщение не содежит фотографии
        return None


async def process_message(app, message):
    downloaded_file_path = await download_image(app, message)
    text = message.caption if message.caption else message.text
    user = message.from_user.first_name if message.from_user else message.sender_chat.title
    return Message(
        id=message.id,
        date=message.date,
        from_user=user,
        text=text,
        image_path=downloaded_file_path
    )


async def get_limit(app, last_message_id):
    # Считываем из истории сообщений чата последнее сообщение, чтобы узнать его id
    async for message in app.get_chat_history(CHAT, limit=1):
        last_new_message_id = message.id

    # Вычисляем сколько сообщений необходимо спарсить, чтобы получить все новые сообщения
    limit = last_new_message_id - last_message_id
    print("последнее сообщение в чате:", last_new_message_id, "\nколичество новых сообщений:", limit)

    return limit


async def get_messages(last_message_id):
    app = Client("CM_HCS_account", api_id=API_ID, api_hash=API_HASH, phone_number=SESSION)
    async with app:
        limit = await get_limit(app, last_message_id)

        messages = []
        if limit > 0:
            async for message in app.get_chat_history(CHAT, limit=limit):
                message_info = await process_message(app, message)
                messages.append(message_info)

            print(messages)
            return messages
