import threading

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
from src.core.event_bus import EventBus
from src.core.orchestrator import Orchestrator

# =========================================================
# APP INIT
# =========================================================
app = FastAPI(title="NexusMind API")

bot = Orchestrator()
event_bus = EventBus()


# =========================================================
# REQUEST MODEL
# =========================================================
class ChatRequest(BaseModel):
    query: str
    session_id: str


# =========================================================
# STREAM CHAT (EVENTBUS TRUE PIPELINE)
# =========================================================
@app.post("/chat/stream")
def chat_stream(req: ChatRequest):

    def run_orchestrator():
        """
        Runs orchestrator in background
        (producer of events)
        """
        try:
            bot.run(req.query, req.session_id)
        except Exception as e:
            event_bus.emit(
                session_id=req.session_id,
                event_type="EVENT",
                source="server",
                content=f"Orchestrator error: {str(e)}",
            )

    # run orchestrator async (non-blocking)
    threading.Thread(target=run_orchestrator).start()

    # stream from EventBus (consumer)
    return StreamingResponse(
        event_bus.stream(req.session_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
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
