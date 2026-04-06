
from fastapi import FastAPI
from pydantic import BaseModel
from chat_agent import RetailChatAgent
import uvicorn

app = FastAPI()
agent = RetailChatAgent()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    return {"response": agent.handle_message(req.user_id, req.message)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
