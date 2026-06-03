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
        float: right;
        clear: both;
    }

    .assistant-bubble {
        background: #F6F6F6;
        padding: 12px 14px;
        border-radius: 14px;
        max-width: 75%;
        font-size: 15px;
        border-left: 3px solid #7C3AED;
        float: left;
        clear: both;
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

if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

if "trace_steps" not in st.session_state:
    st.session_state.trace_steps = []

messages = st.session_state.sessions.setdefault(st.session_state.current_session, [])

# =========================================================
# GREETING
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
        st.session_state.current_session = str(uuid.uuid4())
        st.session_state.sessions[st.session_state.current_session] = []
        st.session_state.trace_steps = []
        st.rerun()

# =========================================================
# HEADER
# =========================================================
st.title("🧠 NexusMind — Nexa AI Assistant")
st.caption("Live Thinking + Streaming Answer")

# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Message Nexa...")

if user_input and not st.session_state.is_streaming:
    messages.append({"role": "user", "content": user_input})

    st.session_state.pending_query = user_input
    st.session_state.is_streaming = True
    st.session_state.trace_steps = []

    st.rerun()

# =========================================================
# CHAT RENDER
# =========================================================
for msg in messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='assistant-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

# =========================================================
# STREAMING LOGIC (FINAL + BUFFER SAFE)
# =========================================================
if st.session_state.is_streaming:
    query = st.session_state.pending_query

    full_response = ""
    buffer = ""

    thinking_box = st.empty()
    answer_box = st.empty()

    try:
        with requests.post(
            API_URL,
            json={
                "query": query,
                "session_id": st.session_state.current_session,
            },
            stream=True,
        ) as r:
            for chunk in r.iter_content(chunk_size=128):
                if not chunk:
                    continue

                buffer += chunk.decode("utf-8")

                # process complete events only
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if not line.strip():
                        continue

                    parts = line.split("|", 2)
                    if len(parts) < 3:
                        continue

                    event_type, source, content = parts

                    # =========================
                    # EVENT (THINKING / TRACE)
                    # =========================
                    if event_type == "EVENT":
                        step = f"{source}: {content}"
                        st.session_state.trace_steps.append(step)

                        thinking_box.markdown(
                            "🧠 **Thinking:**\n"
                            + "\n".join(
                                [f"- {s}" for s in st.session_state.trace_steps]
                            )
                        )

                    # =========================
                    # TOKEN STREAM
                    # =========================
                    elif event_type == "TOKEN":
                        full_response += content

                        answer_box.markdown(
                            f"<div class='assistant-bubble'>{full_response}</div>",
                            unsafe_allow_html=True,
                        )

                    # =========================
                    # FINAL RESPONSE
                    # =========================
                    elif event_type == "FINAL":
                        full_response = content

    except Exception as e:
        full_response = f"⚠️ Error: {str(e)}"

    # =====================================================
    # SAVE FINAL MESSAGE
    # =====================================================
    messages.append({"role": "assistant", "content": full_response})

    st.session_state.is_streaming = False
    st.session_state.pending_query = ""

    st.rerun()

# =========================================================
# TRACE PANEL
# =========================================================
if st.session_state.trace_steps:
    with st.expander("🧠 Trace", expanded=False):
        for i, step in enumerate(st.session_state.trace_steps, 1):
            st.markdown(f"`{i}. {step}`")
