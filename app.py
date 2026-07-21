import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()  # .env file ko load karta hai (local ke liye)

# Local .env se try karo, warna Streamlit Cloud ke Secrets se
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

client = genai.Client(api_key=api_key)

st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")

st.title("🤖 Gemini AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
            )
            answer = response.text
        except Exception as e:
            answer = f"⚠️ Error aaya: {e}"

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
