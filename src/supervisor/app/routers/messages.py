import base64
import io
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import models, dependencies
from app.api.scheme import MessageDB, MessagePlacemark
from app.api.filters import is_from_administration, remove_duplicate_messages


PARSER_HOST = 'http://0.0.0.0:8001'
NLP_HOST = 'http://0.0.0.0:8002'


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
# ----------------------------------------------------------------------------------------------------------------------


async def get_last_message_id(source, db: Session = Depends(dependencies.get_db)):
    """ Определение идентификатора последнего полученного сообщения """
    return (
        db.query(func.max(models.Message.local_id))
        .filter(models.Message.source == source)
        .scalar()
    )


async def get_messages(source: str, db: Session = Depends(dependencies.get_db)):
    """ Получение всех сообщений из базы данных по заданному ресурсу """
    return db.query(models.Message).filter(models.Message.source == source).all()


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


async def get_processing_message(text, source):
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=300.0, write=100.0, pool=50.0)) as client:
        if source == "kvs":
            address = text
            problem = "Водоснабжение"
        else:
            address = await client.get(f"{NLP_HOST}/processing/address", params={"message": text})
            problem = await client.get(f"{NLP_HOST}/processing/problem", params={"message": text})
            address = address.json()
            problem = problem.json()

        address_and_coordinates = await client.get(f"{NLP_HOST}/geocoding", params={"address": address})
        address, coordinates = address_and_coordinates.json()

        return address, problem, coordinates
# ----------------------------------------------------------------------------------------------------------------------


@router.get("/messages/{source}/new/", response_class=HTMLResponse)
async def get_new_source_message_list(source: str, request: Request, db: Session = Depends(dependencies.get_db)):
    """ Получение еще новых сообщений, их запись в базу данных """

    last_message_id = await get_last_message_id(source, db)
    meaningful_messages = []

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
            if db_message or is_from_administration(message.from_user):
                continue

            address, problem, coordinates = await get_processing_message(message.text, message.source)
            if not all([address, problem, coordinates]):
                continue

            message = MessagePlacemark(**dict(message),
                                              address=address,
                                              problem=problem,
                                              coordinates=coordinates)
            meaningful_messages.append(message)

            # Создаем новую запись сообщения в базе данных
            db_message = models.Message(**dict(message))
            db.add(db_message)
            db.commit()
    return templates.TemplateResponse("message_list.html", {"request": request,
                                                            "source": source,
                                                            "category": "new",
                                                            "messages": meaningful_messages})


@router.get("/messages/{source}/", response_class=HTMLResponse)
async def read_messages(source: str, request: Request, db: Session = Depends(dependencies.get_db)):
    """ Получение информации о всех сообщениях с конкретного ресурса """
    await remove_duplicate_messages(db)

    messages = await get_messages(source, db)
    return templates.TemplateResponse("message_list.html", {"request": request,
                                                            "category": "all",
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
                                       "message": message,
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
