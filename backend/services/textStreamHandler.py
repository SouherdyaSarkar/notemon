from fastapi import FastAPI, UploadFile, Form, APIRouter, Query
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import PyPDF2
from datetime import datetime
from typing import Optional
import time
import os

router = APIRouter()

# Resolve path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR, "..", "service_account_firebase", "notemon-f86a9-firebase-adminsdk-fbsvc-e355f62c57.json"
)


SERVICE_ACCOUNT_FILE = os.path.normpath(SERVICE_ACCOUNT_FILE)


# Init Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

db = firestore.client()
def generate_session_id(user_uid: str) -> str:
    ts = int(time.time() * 1000)
    # session_id format: <uid>_<timestamp>
    return f"{user_uid}_{ts}"


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile, uuid: str = Form(...), session_id: str = Form(...)):

    if session_id == "":
        session_id = generate_session_id(uuid)

    pdf_reader = PyPDF2.PdfReader(file.file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

    pdf_entry = {
        "filename": file.filename,
        "content": text,
        "uploaded_at": datetime.utcnow().isoformat()
    }

    db.collection("sessions").document(session_id).set(
        {"pdfs": firestore.ArrayUnion([pdf_entry])}, merge=True
    )

    return {"message": "PDF stored", "session_id": session_id}


@router.post("/add_text")
async def add_text(uuid: str = Form(...), input_text: str = Form(...), session_id: str = Form(...)):

    if session_id == "":
        session_id = generate_session_id(uuid)

    note_entry = {
        "text": input_text,
        "created_at": datetime.now().isoformat()
    }

    db.collection("sessions").document(session_id).set(
        {"inputs": firestore.ArrayUnion([note_entry])}, merge=True
    )

    return {"message": "Text stored", "session_id": session_id}


@router.get("/get_context")
async def get_context(session_id: str = Query(...)):

    doc = db.collection("sessions").document(session_id).get()
    if not doc.exists:
        return {"context": ""}

    data = doc.to_dict()
    pdfs = [pdf["content"] for pdf in data.get("pdfs", [])]
    inputs = [note["text"] for note in data.get("inputs", [])]

    combined = pdfs + inputs   # keep as array of strings
    combined_map = "\n".join(pdfs + inputs)
    return {"context_array": combined, "context_map" : combined_map}
