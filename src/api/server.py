import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
from src.core.orchestrator import Orchestrator

app = FastAPI(title="NexaMind API")

bot = Orchestrator()


class ChatRequest(BaseModel):
    query: str
    session_id: str


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):

    def event_stream():
        stream, _ = bot.run_stream(req.query, req.session_id)
        for token in stream:
            yield token

    return StreamingResponse(event_stream(), media_type="text/plain")


# IMPORTANT FIX
if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host="127.0.0.1",
        port=config.API_PORT,
        reload=True,
    )
