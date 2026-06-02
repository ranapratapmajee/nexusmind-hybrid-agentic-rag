#!/bin/bash

echo "🚀 Starting NexusMind..."

# =========================================
# CONFIG
# =========================================
API_PORT=9000
UI_PORT=8502

# =========================================
# CLEAN OLD PROCESSES (IMPORTANT FIX)
# =========================================
echo "🧹 Cleaning old processes..."

pkill -f "uvicorn src.api.server:app" || true
pkill -f "streamlit run frontend/streamlit_app.py" || true

# free ports if stuck
lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$UI_PORT | xargs kill -9 2>/dev/null || true

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

echo "⏳ Waiting for ChromaDB..."
sleep 5

# =========================================
# Start FastAPI
# =========================================
echo "⚙️ Starting API on port $API_PORT..."
uv run uvicorn src.api.server:app \
    --host 127.0.0.1 \
    --port $API_PORT \
    --log-level warning &
API_PID=$!

sleep 2

# =========================================
# Start Streamlit UI
# =========================================
echo "🖥️ Starting UI on port $UI_PORT..."
uv run streamlit run frontend/streamlit_app.py \
    --server.port $UI_PORT \
    --server.headless true \
    --browser.gatherUsageStats false &
UI_PID=$!

sleep 3

# =========================================
# Open browser (SAFE SINGLE OPEN)
# =========================================
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$UI_PORT"
else
    echo "🌐 Open manually: http://localhost:$UI_PORT"
fi

# =========================================
# STATUS
# =========================================
echo ""
echo "✅ NexusMind is LIVE"
echo "🌐 UI : http://localhost:$UI_PORT"
echo "🔗 API: http://localhost:$API_PORT"
echo ""
echo "Press CTRL+C to stop..."

# =========================================
# CLEAN EXIT
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