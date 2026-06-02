import uuid

import requests
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://127.0.0.1:9000/chat/stream"

st.set_page_config(
    page_title="NexusMind",
    layout="wide",
)

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# =========================================================
# TITLE
# =========================================================
st.title("NexusMind: Self-Optimizing Hybrid RAG & Local Agentic Orchestrator")

# =========================================================
# CHAT DISPLAY (MAIN AREA)
# =========================================================
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # RIGHT SIDE
            col1, col2 = st.columns([1, 2])
            with col2:
                st.markdown(
                    f"""
                    <div style='text-align: right; background:#DCF8C6; padding:10px; border-radius:10px; margin:5px'>
                    {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            # LEFT SIDE
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(
                    f"""
                    <div style='text-align: left; background:#F1F0F0; padding:10px; border-radius:10px; margin:5px'>
                    {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# =========================================================
# INPUT (BOTTOM - LIKE CHATGPT)
# =========================================================
user_input = st.chat_input("Type your message...")

if user_input:
    # store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # display immediately
    st.rerun()

# =========================================================
# RESPONSE HANDLING (STREAM)
# =========================================================
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_msg = st.session_state.messages[-1]["content"]

    response_text = ""

    try:
        with requests.post(
            API_URL,
            json={
                "query": last_user_msg,
                "session_id": st.session_state.session_id,
            },
            stream=True,
        ) as r:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    response_text += chunk.decode("utf-8")

    except Exception as e:
        response_text = f"⚠️ Error: {str(e)}"

    # store assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    st.rerun()
