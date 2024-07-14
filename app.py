from fastapi import FastAPI
from pydantic import BaseModel 
from agent import ChatBot


app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    user_message: str
    history: list[dict[str, str]]


@app.post("/send_message/")
async def send_message(chat_request: ChatRequest):
    bot = ChatBot()
    result = bot(chat_request.user_message, history=chat_request.history)
    return result

