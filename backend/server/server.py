# server.py
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Import service routers
from services.voiceover import router as voiceover_router
from services.faq import router as faq_router
from services.mindmap import router as mindmap_router
from services.summariser import router as summariser_router
from services.textStreamHandler import router as textStreamRouter
from services.injest import router as chroma_injest_router
from services.rag_api import router as rag_api_router

# Initialize the FastAPI app
app = FastAPI(
    title="NoteMon",
    description="AI-powered note-taking and study assistant with TTS capabilities",
    version="1.0.0"
)

# Include routers
app.include_router(voiceover_router, prefix="/api", tags=["Voice & TTS"])
app.include_router(faq_router, prefix="/api", tags=["FAQ"])
app.include_router(mindmap_router, prefix="/api", tags=["Mind Map"])
app.include_router(summariser_router, prefix="/api", tags=["Summarizer"])
app.include_router(textStreamRouter, prefix="/api", tags=["text stream"])
app.include_router(chroma_injest_router, prefix="/api", tags=["ChromaDb"])
app.include_router(rag_api_router, prefix="/api", tags=["RAG"])

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the NoteMon!",
        "version": "1.0.0",
        "features": [
            "Text-to-Speech (TTS)",
            "FAQ Generation",
            "Mind Map Creation",
            "Text Summarization"
        ],
        "endpoints": {
            "tts": "/api/tts/",
            "faq": "/api/faq/",
            "mindmap": "/api/mindmap/",
            "summarizer": "/api/summarizer/"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "NoteMon Backend"}
