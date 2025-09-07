import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

load_dotenv()
router = APIRouter()


# -------- Config --------              # where your raw docs live
PERSIST_DIR = "data/chroma"                # where Chroma will store the index
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_documents(texts: list[str]):
    docs = []
    for i, t in enumerate(texts):
        if not t.strip():
            continue
        docs.append(Document(
            page_content=t,
            metadata={"source": f"firebase_doc_{i}"}
        ))
    return docs


def load_DB(texts : List[str]):
    print("Loading documents...")
    documents = load_documents(texts=texts)
    if not documents:
        print(f"No documents found")
        return

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print("Building / updating Chroma index...")
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name="rag_docs",
    )
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print(f"Done. Persisted at: {PERSIST_DIR}")

class requestModel(BaseModel):
    input : Optional[List[str]]


router.post("/vectordb")
def main(query : requestModel):
    load_DB(query.input)
    
