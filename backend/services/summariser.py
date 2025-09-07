import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

router = APIRouter()

# Request body model
class QueryModel(BaseModel):
    query: str

class response(BaseModel):
    query : str
    response : str


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # or choose another available model
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

router.post("/summarize",response_model=response)
def generate_summary(request: QueryModel):
    messages = [
        ("system", """You are a helpful assistant. Summarise the given text body keeping all the points and context 
         intact and make it properly comprehensive"""),
        ("human", request.query),
    ]
    result = llm.invoke(messages)
    return response(prompt=request.query, response=result.content)

