from datetime import datetime
from typing import List

from fastapi import FastAPI, Query

from src.parser_service.app.api.tg_parser import get_messages as get_tg_messages, Message
from src.parser_service.app.api.web_parser import get_messages as get_kvs_messages


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Parser-service"}


@app.on_event("startup")
async def startup_event():
    print('Server started :', datetime.now())


@app.on_event("shutdown")
async def shutdown_event():
    print('Server shutdown :', datetime.now())

# ----------------------------------------------------------------------------------------------------------------------


@app.get("/messages/tg/new/", response_model=List[Message])
async def get_new_tg_message_list(last_message_id: int = Query(...)):
    return await get_tg_messages(last_message_id)


@app.get("/messages/kvs/new/", response_model=List[Message])
async def get_new_kvs_message_list(last_message_id: int = Query(...)):
    return await get_kvs_messages(last_message_id)
