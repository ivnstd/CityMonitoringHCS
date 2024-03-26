from datetime import datetime
from fastapi import FastAPI, Query

from api.processing import get_address, get_problem
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


@app.get("/processing/address")
async def processing_address(message: str = Query(...)):
    return get_address(message)


@app.get("/processing/problem")
async def processing_problem(message: str = Query(...)):
    return get_problem(message)


@app.get("/geocoding")
async def geocoding_message(address: str = Query(...)):
    return await geocoding(address)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8002, reload=True)
