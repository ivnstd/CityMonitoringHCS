from datetime import datetime

from fastapi import FastAPI

from src.supervisor.app.api import models, database
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
