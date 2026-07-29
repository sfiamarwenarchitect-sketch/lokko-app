#!/bin/bash
cd /Users/shaddek/lokko-mvp/backend
python3 -m venv .venv
.venv/bin/pip install fastapi uvicorn sqlalchemy pydantic