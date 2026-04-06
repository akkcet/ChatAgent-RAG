import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Set project root
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

# Import agent from backend package
from chat_agent import RetailChatAgent

st.set_page_config(page_title="Retail Chatbot")
st.title("🛒 Retail Ingredient Chatbot")

# Initialize the agent
if "agent" not in st.session_state:
    st.session_state.agent = RetailChatAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg, is_user in st.session_state.messages:
    st.chat_message("user" if is_user else "assistant").markdown(msg)

# Chat input
prompt = st.chat_input("Ask anything…")

if prompt:
    st.session_state.messages.append((prompt, True))
    st.chat_message("user").markdown(prompt)

    reply = st.session_state.agent.handle_message("local-user", prompt)
    
    

    st.session_state.messages.append((reply, False))

    st.chat_message("assistant").markdown(reply)