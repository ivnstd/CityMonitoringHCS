from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, BackgroundTasks, Request, Depends, HTTPException, Query

from src.supervisor.app.api import models, database
from src.supervisor.app.api.geocoder import geocode
from src.supervisor.app.routers.messages import router as messages_router


app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)
# ----------------------------------------------------------------------------------------------------------------------


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
app.include_router(messages_router)
