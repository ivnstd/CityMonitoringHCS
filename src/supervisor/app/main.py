from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# import httpx
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api import models, database
from routers.messages import router as messages_router
from routers.map import router as map_router

from api.logger import logger

MAIN_HOST = 'http://0.0.0.0:8000'

app = FastAPI()
# scheduler = AsyncIOScheduler()  # Планировщик задач
models.Base.metadata.create_all(bind=database.engine)
# ----------------------------------------------------------------------------------------------------------------------


@app.on_event("startup")
async def startup_event():
    logger.info(f"Server started : {datetime.now()}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Server shutdown : {datetime.now()}")


# async def daily_data_update():
#     url = f"{MAIN_HOST}/"
#     params = {"is_new": "new"}
#     async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=300.0, write=100.0, pool=50.0)) as client:
#         response = await client.get(url, params=params)
#         logger.info(f"response : {response}")
#
# # Запуска задачи ежедневно в 00:00
# scheduler.add_job(daily_data_update, "cron", hour=0, minute=0)
# scheduler.start() # запуск планировщика
# ----------------------------------------------------------------------------------------------------------------------


# Директория статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(messages_router)
app.include_router(map_router)
