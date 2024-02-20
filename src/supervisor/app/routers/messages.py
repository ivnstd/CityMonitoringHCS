import base64
import io
from typing import List

import httpx
from fastapi import APIRouter, BackgroundTasks, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.supervisor.app.api import models, dependencies
from src.supervisor.app.api.scheme import MessageDB


PARSER_HOST = 'http://0.0.0.0:8001'

router = APIRouter()
templates = Jinja2Templates(directory="src/supervisor/app/templates")

# ----------------------------------------------------------------------------------------------------------------------
async def get_last_message_id(source, db: Session = Depends(dependencies.get_db)):
    """ Определение идентификатора последнего полученного сообщения """
    return (
        db.query(func.max(models.Message.local_id))
        .filter(models.Message.source == source)
        .scalar()
    )


async def get_message(source, local_id, db: Session = Depends(dependencies.get_db)):
    """ Получение сообщения из базы данных по его источнику и локальному идентификатору"""
    return (
        db.query(models.Message).filter(
            (models.Message.source == source) &
            (models.Message.local_id == local_id)
        ).first()
    )


def decode_image(image_data):
    """ Декодирование изображения из строки в байты """
    if image_data:
        image_bytes = base64.b64decode(image_data)
    else:
        image_bytes = None
    return image_bytes


def parse_message(message):
    """ Обработка полученного сообщения перед записью в базу данных """
    return MessageDB(
        local_id=message["id"],
        source=message["source"],
        date=message["date"],
        from_user=message["from_user"],
        text=message.get("text"),
        image=decode_image(message.get("image"))
    )

# ----------------------------------------------------------------------------------------------------------------------


@router.get("/messages/{source}/new/", response_model=List[MessageDB], response_class=HTMLResponse)
async def get_new_source_message_list(source: str, request: Request, db: Session = Depends(dependencies.get_db)):
    """ Получение еще новых сообщений, их запись в базу данных """

    last_message_id = await get_last_message_id(source, db)

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=300.0, write=100.0, pool=50.0)) as client:
        url = f"{PARSER_HOST}/messages/{source}/new/"
        params = {"last_message_id": last_message_id}
        response = await client.get(url, params=params)

        if response.status_code != 200:
            return HTMLResponse(content="Не удалось получить сообщения", status_code=response.status_code)

        messages_json = response.json()
        messages = [parse_message(msg) for msg in messages_json]

        for message in messages:
            # Пропускаем запись сообщения, если оно уже существует в базе данных
            db_message = await get_message(message.source, message.local_id, db)
            if db_message:
                continue

            # Создаем новую запись сообщения в базе данных
            db_message = models.Message(**dict(message))
            db.add(db_message)
            db.commit()
        return templates.TemplateResponse("message_list.html", {"request": request,
                                                                "source": source,
                                                                "messages": messages})


@router.get("/messages/{source}/{local_id}", response_class=HTMLResponse)
async def read_message(request: Request, source: str, local_id: int, db: Session = Depends(dependencies.get_db)):
    """ Получение информации о конкретном сообщении """
    message = await get_message(source, local_id, db)

    if message is None:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    image_url = f"/messages/{source}/{local_id}/image" if message.image else None

    return templates.TemplateResponse("message.html",
                                      {"request": request,
                                       "id": message.local_id,
                                       "source": message.source,
                                       "author": message.from_user,
                                       "date": message.date,
                                       "message": message.text,
                                       "image_url": image_url})


@router.get("/messages/{source}/{local_id}/image")
async def get_message_image(source: str, local_id: int, db: Session = Depends(dependencies.get_db)):
    """ Получение картинки из конкретного сообщения """
    message = await get_message(source, local_id, db)

    if message is None:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    if message.image:
        return StreamingResponse(io.BytesIO(message.image), media_type="image/jpg")
    else:
        return HTMLResponse(content="Фото отсутствует")
