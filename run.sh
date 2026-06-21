#!/bin/bash

# Ensure script halts immediately if any sub-command fails
set -e

# Clear console window for crisp log scanning
clear

echo "=================================================================="
echo "🚀 INITIALIZING NEXUSMIND GRAPH-RAG AUTOMATION WORKSPACE"
echo "=================================================================="

# 1. Check if Docker is active and containers are live using corrected Compose target names
echo "Checking core database service instances (ChromaDB & Neo4j)..."
if ! docker ps | grep -q "neo4j_container" || ! docker ps | grep -q "chromadb_container"; then
    echo "⚠️  CRITICAL FAULT: Core Docker instances are offline!"
    echo "Bootstrapping compose environment cluster..."
    # Ensure containers are brought up if they don't exist yet, instead of just running start
    docker compose up -d
    sleep 3
else
    echo "✅ Docker infrastructure containers verified online."
fi

# 2. Check if Ollama is running and has the models pulled
echo "Verifying local M4 Ollama intelligence core..."
if ! nc -z localhost 11434; then
    echo "❌ CRITICAL FAULT: Ollama is not running on your Mac!"
    echo "Please open the Ollama app or run 'ollama serve' in another terminal."
    exit 1
fi

# Optional: Trigger quick ingestion checks
# Uncomment the line below if you want to auto-run ingestion on startup:
# uv run ingest_book.py

echo "------------------------------------------------------------------"
echo "🖥️  LAUNCHING STREAMLIT USER INTERFACE CHAT DASHBOARD"
echo "------------------------------------------------------------------"

# 3. Launch Streamlit and suppress the verbose file watcher warnings
uv run streamlit run app/ui/streamlit_app.py --server.fileWatcherType none
