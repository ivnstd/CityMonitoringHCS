import base64
import io
from typing import List

import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.supervisor.app.api import models, dependencies
from src.supervisor.app.api.scheme import MessageDB, MessagePlacemark


router = APIRouter()
templates = Jinja2Templates(directory="src/supervisor/app/templates")


async def get_data_messages(db: Session = Depends(dependencies.get_db)):
    data = db.query(models.Message).all()
    return data


@router.get("/map/data/", response_model=MessagePlacemark)
def get_data(db: Session = Depends(dependencies.get_db)):
    data = db.query(models.Message).all()
    if data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return data


@router.get("/map", response_class=HTMLResponse)
async def map(request: Request, db: Session = Depends(dependencies.get_db)):
    messages = await get_data_messages(db)
    filtered_messages = []
    for message in messages:
        filtered_message = {
            "problem": message.problem,
            "address": message.address,
            "coordinates": message.coordinates
        }
        filtered_messages.append(filtered_message)
    print(filtered_messages)
    return templates.TemplateResponse("map.html", {"request": request,
                                                   "messages": filtered_messages})
