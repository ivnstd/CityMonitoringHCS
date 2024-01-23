#!/bin/bash


source .venv/bin/activate
uvicorn src.citymonitoringhcs.main:app --reload
