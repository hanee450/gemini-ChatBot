import streamlit as st
from google import genai
from google.genai import types
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

# Render past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Single row, pinned to the bottom of the page ---
# Mic sits inside a small popover (so it never has to squeeze/clip inside a
# narrow column) + chat input (with built-in file attach) next to it.
with st.bottom:
    col_mic, col_input = st.columns([1, 8], vertical_alignment="center")

    with col_mic:
        with st.popover("🎤"):
            audio_value = st.audio_input("Record a voice message")

    with col_input:
        user_turn = st.chat_input(
            "Ask anything...",
            accept_file="multiple",
            file_type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "docx"],
        )

if user_turn or audio_value is not None:
    text_prompt = user_turn.text if user_turn else ""
    uploaded_files = user_turn.files if user_turn else []

    parts = []
    if text_prompt:
        parts.append(text_prompt)

    for f in uploaded_files:
        parts.append(types.Part.from_bytes(data=f.getvalue(), mime_type=f.type))

    if audio_value is not None:
        parts.append(
            types.Part.from_bytes(
                data=audio_value.getvalue(), mime_type=audio_value.type
            )
        )

    if parts:
        display_bits = []
        if text_prompt:
            display_bits.append(text_prompt)
        if uploaded_files:
            display_bits.append("📎 " + ", ".join(f.name for f in uploaded_files))
        if audio_value is not None:
            display_bits.append("🎤 Voice message")
        display_text = "\n\n".join(display_bits)

        st.session_state.messages.append({"role": "user", "content": display_text})

        with st.chat_message("user"):
            st.markdown(display_text)
            if audio_value is not None:
                st.audio(audio_value)

        with st.chat_message("assistant"):
            try:
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=parts,
                )
                answer = response.text
            except Exception as e:
                answer = f"⚠️ Error aaya: {e}"

            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
