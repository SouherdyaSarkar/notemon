import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# -------- Config --------
PERSIST_DIR = "data/chroma"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-70b-versatile"   # or "mixtral-8x7b-32768"
TOP_K = 5


load_dotenv()
router = APIRouter()

# ---------- Build Chain ----------
def build_chain():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name="rag_docs",
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K})

    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=GROQ_MODEL,
        temperature=0.2,
    )

    template = """You are a helpful assistant. Use the provided context to answer the user question.
If the answer cannot be found in the context, say you don't know.

Context:
{context}

Question:
{question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# ---------- FastAPI Models ----------
class Query(BaseModel):
    question: str

class Answer(BaseModel):
    question: str
    answer: str

# ---------- API Route ----------
@router.post("/rag-context", response_model=Answer)
def ask(query: Query):
    chain = build_chain()
    answer = chain.invoke(query.question)
    return {"question": query.question, "answer": answer}
