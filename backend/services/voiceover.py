from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
import pyttsx3
import uuid
import os

router = APIRouter()
engine = pyttsx3.init()

@router.get("/speak")
def speak(text: str = Query(...)):
    filename = f"speech_{uuid.uuid4().hex}.wav"
    engine.save_to_file(text, filename)
    engine.runAndWait()

    return FileResponse(
        path=filename,
        filename="speech.wav",
        media_type="audio/wav"
    )
