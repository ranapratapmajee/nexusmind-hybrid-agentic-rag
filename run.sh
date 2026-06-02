#!/bin/bash

echo "🚀 Starting NexusMind..."

# =========================================
# CONFIG
# =========================================
API_PORT=9000
UI_PORT=8502

# =========================================
# Sync dependencies
# =========================================
echo "📦 Syncing dependencies..."
uv sync

# =========================================
# Start ChromaDB (Docker)
# =========================================
echo "🐳 Starting ChromaDB..."
docker compose up -d

# Wait for DB to initialize
echo "⏳ Waiting for ChromaDB..."
sleep 5

# =========================================
# Start FastAPI (NO RELOAD → CLEAN)
# =========================================
echo "⚙️ Starting API on port $API_PORT..."
uv run uvicorn src.api.server:app --port $API_PORT &
API_PID=$!

# =========================================
# Start Streamlit UI
# =========================================
echo "🖥️ Starting UI on port $UI_PORT..."
uv run streamlit run frontend/streamlit_app.py --server.port $UI_PORT &
UI_PID=$!

# =========================================
# Open browser (ONLY ONCE)
# =========================================
sleep 3
open http://localhost:$UI_PORT

echo ""
echo "✅ NexusMind is LIVE"
echo "🌐 UI:  http://localhost:$UI_PORT"
echo "🔗 API: http://localhost:$API_PORT"
echo ""
echo "Press CTRL+C to stop..."

# =========================================
# Graceful shutdown
# =========================================
cleanup() {
    echo ""
    echo "🛑 Stopping services..."

    kill $API_PID 2>/dev/null
    kill $UI_PID 2>/dev/null

    echo "🐳 Stopping Docker..."
    docker compose down

    echo "👋 NexusMind stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

wait