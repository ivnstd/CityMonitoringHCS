from datetime import datetime
from fastapi import FastAPI

from src.supervisor.app.api import models, database
from src.supervisor.app.routers.messages import router as messages_router
from src.supervisor.app.routers.processing import router as processing_router
from src.supervisor.app.routers.map import router as map_router

from src.supervisor.app.logger import logger


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
app.include_router(messages_router)
app.include_router(processing_router)
app.include_router(map_router)
