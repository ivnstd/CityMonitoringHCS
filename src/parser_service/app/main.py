from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import func
import uvloop
import os
import io
from typing import Optional, List
from datetime import datetime
from src.parser_service.app.api.tg_parser import get_messages, Message
# from src.parser_service.app.api import models, database, dependencies



app = FastAPI()
templates = Jinja2Templates(directory="src/parser_service/app/templates")

# # Создание всех таблиц, которые описаны в models.py
# models.Base.metadata.create_all(bind=database.engine)


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

@app.get("/new_messages/", response_model=List[Message])
async def get_new_message_list(last_message_id: int = Query(...)):
    # Получаем список сообщений
    messages = await get_messages(last_message_id)
    # Возвращаем список сообщений
    return messages




# ----------------------------------------------------------------------------------------------------------------------

# outages

if __name__ == "__main__":
    os.makedirs("downloaded_images", exist_ok=True)
    # uvloop.install()
