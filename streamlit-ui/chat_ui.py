import streamlit as st
st.set_page_config(page_title="Retail Chatbot (Direct Mode)")

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# ---- Load backend and env ----

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Load .env
load_dotenv(ROOT_DIR / ".env")

# Debug
st.write("DEBUG KEY:", os.getenv("AZURE_OPENAI_KEY"))
st.write("DEBUG ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))

from backend.chat_agent import RetailChatAgent

# ---- UI ----

st.title("🛒 Retail Chatbot — Direct Agent Mode (No FastAPI)")
print("here1")
# State
if "agent" not in st.session_state:
    st.session_state.agent = RetailChatAgent()
print("here2")
if "messages" not in st.session_state:
    st.session_state.messages = []
print("here3")
# Display previous messages
for msg, is_user in st.session_state.messages:
    st.chat_message("user" if is_user else "assistant").markdown(msg)
print("here4")
# Chat input
prompt = st.chat_input("Ask anything…")

if prompt:
    print("here5")
    st.session_state.messages.append((prompt, True))
    st.chat_message("user").markdown(prompt)
    print("here6")
    reply = st.session_state.agent.handle_message("local-user", prompt)
    st.session_state.messages.append((reply, False))
    print("here7")
    st.chat_message("assistant").markdown(reply)
    print("here8")