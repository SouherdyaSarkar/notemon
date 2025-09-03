import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Optional, List

router = APIRouter()

class requestBody(BaseModel):
    context : str

class faqType(BaseModel):
    question : str
    hint : Optional[str]

class faqResponse(BaseModel):
    faqSet : List[faqType]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # or choose another available model
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


router.post("/faq",response_model=faqResponse)
def generate_summary(request: requestBody):
    messages = [
        ("system", "You are a helpful assistant."),
        ("human", request.query),
    ]
    result = llm.invoke(messages)
    return faqResponse(faqSet=result)