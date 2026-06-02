import uuid

import requests
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://127.0.0.1:9000/chat/stream"

st.set_page_config(page_title="NexusMind", layout="wide")

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>

    .user-bubble {
        background: #DCF8C6;
        padding: 10px 14px;
        border-radius: 14px;
        max-width: 70%;
        font-size: 15px;
        line-height: 1.5;
        float: right;
        clear: both;
    }

    .assistant-bubble {
        background: #F6F6F6;
        padding: 12px 14px;
        border-radius: 14px;
        max-width: 75%;
        font-size: 15px;
        line-height: 1.6;
        border-left: 3px solid #7C3AED;
        float: left;
        clear: both;
    }

    .system-indicator {
        color: #8A8A8A;
        font-size: 12px;
        font-style: italic;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "current_session" not in st.session_state:
    st.session_state.current_session = str(uuid.uuid4())

if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

if st.session_state.current_session not in st.session_state.sessions:
    st.session_state.sessions[st.session_state.current_session] = []

messages = st.session_state.sessions[st.session_state.current_session]

# =========================================================
# FIRST GREETING
# =========================================================
if len(messages) == 0:
    messages.append(
        {
            "role": "assistant",
            "content": "👋 Hi, I am **Nexa**. How can I help you today?",
        }
    )

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🧠 Nexa Sessions")

    if st.button("➕ New Chat"):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = [
            {
                "role": "assistant",
                "content": "👋 Hi, I am **Nexa**. How can I help you today?",
            }
        ]
        st.session_state.current_session = new_id
        st.rerun()

    st.divider()

    for sid in list(st.session_state.sessions.keys()):
        if st.button(f"💬 {sid[:6]}", key=sid):
            st.session_state.current_session = sid
            st.rerun()

# =========================================================
# HEADER
# =========================================================
st.title("🧠 NexusMind — Nexa AI Assistant")
st.caption("Agentic RAG Orchestrator with Streaming Responses")

# =========================================================
# INPUT (PHASE 1)
# =========================================================
user_input = st.chat_input("Message Nexa...")

if user_input and not st.session_state.is_streaming:
    messages.append({"role": "user", "content": user_input})

    st.session_state.pending_query = user_input
    st.session_state.is_streaming = True

    st.rerun()

# =========================================================
# CHAT RENDER (ALWAYS FIRST)
# =========================================================
for msg in messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='assistant-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

# =========================================================
# STREAMING (PHASE 2 - AFTER RENDER FIX)
# =========================================================
if st.session_state.is_streaming:
    query = st.session_state.pending_query

    full_response = ""

    system_placeholder = st.empty()
    response_placeholder = st.empty()

    try:
        with requests.post(
            API_URL,
            json={
                "query": query,
                "session_id": st.session_state.current_session,
            },
            stream=True,
        ) as r:
            for chunk in r.iter_content(chunk_size=64):
                if chunk:
                    system_placeholder.markdown(
                        "<div class='system-indicator'>"
                        "🧠 Nexa is thinking • routing • retrieving context..."
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    full_response += chunk.decode("utf-8")

                    response_placeholder.markdown(
                        f"<div class='assistant-bubble'>{full_response}</div>",
                        unsafe_allow_html=True,
                    )

    except Exception as e:
        full_response = f"⚠️ Error: {str(e)}"

    system_placeholder.empty()

    messages.append({"role": "assistant", "content": full_response})

    st.session_state.is_streaming = False
    st.session_state.pending_query = ""

    st.rerun()
