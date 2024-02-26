from datetime import datetime
from fastapi import FastAPI, Query

from src.nlp_service.app.api.processing import processing
from src.nlp_service.app.api.geocoder import geocoding
from src.supervisor.app.api.scheme import MessageDB
from typing import List


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "NLP-service"}

@app.on_event("startup")
async def startup_event():
    print('Server started :', datetime.now())


@app.on_event("shutdown")
async def shutdown_event():
    print('Server shutdown :', datetime.now())

# ----------------------------------------------------------------------------------------------------------------------


@app.get("/processing")
async def processing_message(message: str = Query(...)):
    return processing(message)


@app.get("/geocoding")
async def geocoding_message(address: str = Query(...)):
    return await geocoding(address)
