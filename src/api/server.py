import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
from src.core.orchestrator import Orchestrator

# =========================================================
# APP INIT
# =========================================================
app = FastAPI(title="NexusMind API")

bot = Orchestrator()


# =========================================================
# REQUEST MODEL
# =========================================================
class ChatRequest(BaseModel):
    query: str
    session_id: str


# =========================================================
# STREAM CHAT (REAL EVENT STREAM)
# =========================================================
@app.post("/chat/stream")
def chat_stream(req: ChatRequest):

    def event_stream():

        # REAL STREAM FROM ORCHESTRATOR
        for event in bot.run_stream(req.query, req.session_id):
            # -------------------------------------------------
            # THINKING EVENTS
            # -------------------------------------------------
            if isinstance(event, str) and event.startswith("EVENT|"):
                yield event + "\n"
                continue

            # -------------------------------------------------
            # TOKEN STREAM
            # -------------------------------------------------
            if isinstance(event, str) and event.startswith("TOKEN|"):
                yield event + "\n"
                continue

            # -------------------------------------------------
            # FINAL TRACE
            # -------------------------------------------------
            if isinstance(event, str) and event.startswith("TRACE|"):
                yield event + "\n"
                continue

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
    )


# =========================================================
# RUN SERVER
# =========================================================
if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host="127.0.0.1",
        port=config.API_PORT,
        reload=True,
    )
