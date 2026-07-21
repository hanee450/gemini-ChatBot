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

# --- Attachments row: file upload + voice recording ---
col1, col2 = st.columns([3, 2])

with col1:
    uploaded_files = st.file_uploader(
        "Attach files",
        type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

with col2:
    audio_value = st.audio_input("Record a voice message", label_visibility="collapsed")

prompt = st.chat_input("Ask anything...")

# Build the list of Gemini "parts" from files/audio, reused whichever way the
# user triggers a send (typed text and/or attachments).
def build_parts(text_prompt):
    parts = []

    if text_prompt:
        parts.append(text_prompt)

    if uploaded_files:
        for f in uploaded_files:
            parts.append(
                types.Part.from_bytes(data=f.getvalue(), mime_type=f.type)
            )

    if audio_value is not None:
        parts.append(
            types.Part.from_bytes(
                data=audio_value.getvalue(), mime_type=audio_value.type
            )
        )

    return parts


# Trigger a turn either when the user types + hits enter, OR when they've
# recorded audio / attached a file and there's no typed prompt yet but they
# still want to send it. We treat "prompt submitted" as the send signal for
# text, and give a separate "Send attachment" button for audio/file-only sends.
send_attachment_only = False
if (uploaded_files or audio_value is not None) and not prompt:
    send_attachment_only = st.button("Send attachment")

if prompt or send_attachment_only:
    parts = build_parts(prompt)

    if not parts:
        st.stop()

    # Build a readable label for the chat history (files/audio don't have
    # literal text, so we describe what was sent)
    display_bits = []
    if prompt:
        display_bits.append(prompt)
    if uploaded_files:
        display_bits.append(
            "📎 " + ", ".join(f.name for f in uploaded_files)
        )
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

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
