#!/bin/bash


source .venv/bin/activate
uvicorn src.nlp_service.app.main:app --host 0.0.0.0 --port 8001 --reload &
uvicorn src.parser_service.app.main:app --host 0.0.0.0 --port 8002 --reload &
