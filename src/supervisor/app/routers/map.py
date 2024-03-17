from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import base64
from app.api import models, dependencies
from app.api.scheme import MessagePlacemark


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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
        date = message.date.date().strftime("%d.%m.%Y")

        image = message.image
        if image:
            image_base64 = base64.b64encode(image).decode('utf-8')
            image = f'data:image;base64,{image_base64}'

        filtered_message = {
            "date": date,
            "problem": message.problem,
            "address": message.address,
            "coordinates": message.coordinates,
            "image": image
        }
        filtered_messages.append(filtered_message)

    return templates.TemplateResponse("map.html", {"request": request,
                                                   "messages": filtered_messages})
