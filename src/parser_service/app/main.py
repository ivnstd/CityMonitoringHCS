from datetime import datetime
from typing import List

from fastapi import FastAPI, Query

from api.scheme import Message
from api.tg_parser import get_messages as get_tg_messages
from api.web_parser import get_messages as get_kvs_messages
from api.logger import logger


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Parser-service"}


@app.on_event("startup")
async def startup_event():
    logger.info(f"Server started : {datetime.now()}")
    logger.info(f"Uvicorn running in docker on : http://0.0.0.0:8001")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Server shutdown : {datetime.now()}")

# ----------------------------------------------------------------------------------------------------------------------


@app.get("/messages/tg/new/", response_model=List[Message])
async def get_new_tg_message_list(last_message_id: int = Query(...)):
    return await get_tg_messages(last_message_id)


@app.get("/messages/kvs/new/", response_model=List[Message])
async def get_new_kvs_message_list(last_message_id: int = Query(...)):
    return await get_kvs_messages(last_message_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8001, reload=True)
