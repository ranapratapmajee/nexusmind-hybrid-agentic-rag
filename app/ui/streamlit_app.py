# app/ui/streamlit_app.py

import streamlit as st
import sys
from pathlib import Path

# Setup system environment anchors
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.main import initialize_nexus_system

st.set_page_config(
    page_title="NexusResearch V1",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def load_agent_runtime():
    return initialize_nexus_system()

agent = load_agent_runtime()

st.title("🤖 NexusResearch V1 — AI Assistant")
st.caption("Graph-Driven Hybrid Retrieval-Augmented Generation Engine")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display conversation histories
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])
        if "engine" in chat:
            st.caption(f"Engine: {chat['engine']} | Chunks: {chat['vectors']} | Triplets: {chat['graphs']}")

# Grab chat queries
if user_input := st.chat_input("Ask a research query..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("Executing Parallel Asynchronous GraphRAG Sweeps..."):
            response_payload = agent.execute_research_flow(user_input)
            
            st.markdown(response_payload["answer"])
            st.caption(
                f"Routed to: {response_payload['engine']} | "
                f"Vector Matches: {response_payload['vector_sources_count']} | "
                f"Graph Links: {response_payload['graph_triplets_count']}"
            )
            
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_payload["answer"],
        "engine": response_payload["engine"],
        "vectors": response_payload["vector_sources_count"],
        "graphs": response_payload["graph_triplets_count"]
    })