from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uvloop
import os
from datetime import datetime
from src.parser_service.app.api.tg_parser import get_messages, Message
from src.parser_service.app.api import models, database, dependencies

app = FastAPI()

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

@app.get("/messages/", response_model=list[Message])
async def get_message_list(db: Session = Depends(dependencies.get_db)):
    # Выполняем запрос к базе данных для поиска максимального идентификатора сообщения
    last_message_id = db.query(func.max(models.Message.id)).scalar()

    # Получаем список сообщений
    messages = await get_messages(last_message_id)


    # Проходимся по списку сообщений и записываем каждое сообщение в базу данных
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
                                    image_path=message.image_path)
        db.add(db_message)

    # Сохраняем изменения в базе данных
    db.commit()
    # Возвращаем список сообщений
    return messages


@app.get("/messages/{message_id}")
async def read_item(message_id: int, db: Session = Depends(dependencies.get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


if __name__ == "__main__":
    os.makedirs("downloaded_images", exist_ok=True)
    uvloop.install()
