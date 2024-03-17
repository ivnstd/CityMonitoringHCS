import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api import models, dependencies


NLP_HOST = 'http://0.0.0.0:8002'

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def get_message(source, local_id, db: Session = Depends(dependencies.get_db)):
    """ Получение сообщения из базы данных по его источнику и локальному идентификатору"""
    # TODO: перенести
    return (
        db.query(models.Message).filter(
            (models.Message.source == source) &
            (models.Message.local_id == local_id)
        ).first()
    )


@router.get("/processing/{source}/{local_id}")
async def get_processing_message(source: str, local_id: int, db: Session = Depends(dependencies.get_db)):
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=300.0, write=100.0, pool=50.0)) as client:
        message = await get_message(source, local_id, db)
        url = f"{NLP_HOST}/processing"
        params = {"message": message.text}
        response = await client.get(url, params=params)

        if response.status_code != 200:
            return HTMLResponse(content="Не удалось получить сообщения", status_code=response.status_code)

        result = response.json()
    return result
