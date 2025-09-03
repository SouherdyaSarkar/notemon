import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

router = APIRouter()

class requestBody(BaseModel):
    context : str

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # or choose another available model
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

router.post("/minmdap")
def mind_map_json(request : requestBody):
    messages = [
        ("system", "You are a helpful assistant."),
        ("human", request.context),
    ]
    result = llm.invoke(messages)
    return result
