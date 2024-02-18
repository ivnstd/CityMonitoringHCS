from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, Query

from src.parser_service.app.api.tg_parser import get_messages, Message


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

@app.get("/new_messages/", response_model=List[Message])
async def get_new_message_list(last_message_id: int = Query(...)):
    messages = await get_messages(last_message_id)
    return messages
