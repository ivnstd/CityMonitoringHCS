from datetime import datetime
from fastapi import FastAPI, Query

from api.processing import processing
from api.geocoder import geocoding
from api.logger import logger


app = FastAPI()
# ----------------------------------------------------------------------------------------------------------------------


@app.get("/")
async def root():
    return {"message": "NLP-service"}


@app.on_event("startup")
async def startup_event():
    logger.info(f"Server started : {datetime.now()}")
    logger.info("Uvicorn running in docker on : http://0.0.0.0:8002")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Server shutdown : {datetime.now()}")

# ----------------------------------------------------------------------------------------------------------------------


@app.get("/processing")
async def processing_message(message: str = Query(...)):
    return processing(message)


@app.get("/geocoding")
async def geocoding_message(address: str = Query(...)):
    return await geocoding(address)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8002, reload=True)
