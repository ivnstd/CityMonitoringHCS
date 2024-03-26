from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import models, database
from routers.messages import router as messages_router
from routers.map import router as map_router

from api.logger import logger


app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)
# ----------------------------------------------------------------------------------------------------------------------


@app.get("/")
async def root():
    return {"message": "Supervisor"}


@app.on_event("startup")
async def startup_event():
    logger.info(f"Server started : {datetime.now()}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Server shutdown : {datetime.now()}")
# ----------------------------------------------------------------------------------------------------------------------


# Директория статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(messages_router)
app.include_router(map_router)
