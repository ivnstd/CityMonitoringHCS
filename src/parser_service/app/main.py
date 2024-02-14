from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import func
import uvloop
import os
import io
from datetime import datetime
from src.parser_service.app.api.tg_parser import get_messages, Message
from src.parser_service.app.api import models, database, dependencies



app = FastAPI()
templates = Jinja2Templates(directory="src/parser_service/app/templates")

# Создание всех таблиц, которые описаны в models.py
models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
async def root():
    return {"message": "Parser-service"}


@app.on_event("startup")
async def startup_event():
    print('Server started :', datetime.now())


@app.on_event("shutdown")
async def shutdown_event():
    print('Server shutdown :', datetime.now())

# ----------------------------------------------------------------------------------------------------------------------

@app.get("/messages/", response_class=HTMLResponse)
async def get_message_list(request: Request, db: Session = Depends(dependencies.get_db)):
    # Выполняем запрос к базе данных для поиска максимального идентификатора сообщения
    last_message_id = db.query(func.max(models.Message.id)).scalar()
    print(last_message_id)

    # Получаем список сообщений
    messages = await get_messages(last_message_id)


    # Проходимся по списку сообщений и записываем каждое сообщение в базу данных
    for message in messages:
        try:
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
        except Exception as e:
            print(f"Failed to write image: {e}")
            return None

    # Сохраняем изменения в базе данных
    db.commit()
    # Возвращаем список сообщений
    return templates.TemplateResponse("message_list.html", {"request": request, "messages": messages})


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



if __name__ == "__main__":
    os.makedirs("downloaded_images", exist_ok=True)
    uvloop.install()
