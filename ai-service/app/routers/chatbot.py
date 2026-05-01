from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas.chatbot import ChatbotRequest, ChatbotResponse
from app.services.chatbot import generate_chatbot_response


router = APIRouter(tags=["chatbot"])


@router.post("/chatbot", response_model=ChatbotResponse)
def chatbot(request: ChatbotRequest, session: Session = Depends(get_session)) -> ChatbotResponse:
    return generate_chatbot_response(session=session, payload=request)
