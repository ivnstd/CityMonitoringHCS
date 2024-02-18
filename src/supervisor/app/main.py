from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import func
# import uvloop
import os
import io
from datetime import datetime
import asyncio
from datetime import datetime
import httpx
import json
from pydantic import BaseModel
from typing import Optional, List
import base64
from src.supervisor.app.api import models, database, dependencies, geocoder

PARSER_HOST = 'http://0.0.0.0:8001'

class Message(BaseModel):
    id: int
    date: datetime
    from_user: str
    text: Optional[str] = None
    image: Optional[bytes] = None


app = FastAPI()
templates = Jinja2Templates(directory="src/supervisor/app/templates")

# Создание всех таблиц, которые описаны в models.py
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
async def root():
    return {"message": "Supervisor"}


@app.on_event("startup")
async def startup_event():
    print('Server started :', datetime.now())


@app.on_event("shutdown")
async def shutdown_event():
    print('Server shutdown :', datetime.now())

# ----------------------------------------------------------------------------------------------------------------------


async def fetch_messages(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None


# ----------------------------------------------------------------------------------------------------------------------

@app.get("/new_messages/", response_model=List[Message], response_class=HTMLResponse)
async def get_new_message_list(request: Request, db: Session = Depends(dependencies.get_db)):

    # Выполняем запрос к базе данных для поиска максимального идентификатора сообщения
    last_message_id = db.query(func.max(models.Message.id)).scalar()

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=8.0, read=30.0, write=30.0, pool=30.0)) as client:
        url = f"{PARSER_HOST}/new_messages/"
        params = {"last_message_id": last_message_id}
        response = await client.get(url, params=params)

        if response.status_code != 200:
            return HTMLResponse(content="Failed to fetch messages", status_code=response.status_code)

        messages_json = response.json()
        messages = [parse_message(msg) for msg in messages_json]


        for message in messages:
            # Проверяем, существует ли сообщение с таким же ID уже в базе данных
            db_message = db.query(models.Message).filter(models.Message.id == message.id).first()
            if db_message:
                # Если сообщение существует, пропускаем его
                continue

            # Создаем новую запись сообщения в базе данных
            db_message = models.Message(id=message.id,
                                        date=message.date,
                                        from_user=message.from_user,
                                        text=message.text,
                                        image=message.image)
            db.add(db_message)

        # Сохраняем изменения в базе данных
        db.commit()
        return templates.TemplateResponse("message_list.html", {"request": request, "messages": messages})


def decode_image(image_data):
    if image_data:
        image_bytes = base64.b64decode(image_data)
    else:
        image_bytes = None
    return image_bytes


def parse_message(msg):
    return Message(
        id=msg["id"],
        date=msg["date"],
        from_user=msg["from_user"],
        text=msg.get("text"),
        image=decode_image(msg.get("image"))
    )

@app.get("/messages/{message_id}", response_class=HTMLResponse)
async def read_message(request: Request, message_id: int, db: Session = Depends(dependencies.get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    image_url = f"/messages/{message_id}/image" if message.image else None
    image_text = "No image available" if not message.image else None

    return templates.TemplateResponse("message.html",
                                      {"request": request,
                                       "author": message.from_user,
                                       "message": message.text,
                                       "image_url": image_url,
                                       "image_text": image_text})


@app.get("/messages/{message_id}/image")
async def get_message_image(message_id: int, db: Session = Depends(dependencies.get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.image:
        return StreamingResponse(io.BytesIO(message.image), media_type="image/jpg")
    else:
        return HTMLResponse(content="No image available")
