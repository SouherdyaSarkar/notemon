# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

# Initialize the FastAPI app
app = FastAPI(
    title="NoteMon",
    description="Preliminary backend for notwmon",
    version="1.0.0"
)

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the NoteMon!"}
