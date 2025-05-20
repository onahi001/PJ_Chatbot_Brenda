import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import datetime
import requests
import json
import pandas as pd

# --- Load API key from .env ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key not found. Please set GEMINI_API_KEY in .env")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# --- UI Setup ---
st.set_page_config(page_title="Brenda Chatbot", layout="wide")
st.title("💬 Brenda Chatbot")

# --- Detect system theme ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark" if st.get_option("theme.base") == "dark" else "light"
theme = st.session_state.theme

if theme == "dark":
    user_bubble_style = "background-color:#333333; color:white;"
    bot_bubble_style = "background-color:#444444; color:white;"
else:
    user_bubble_style = "background-color:#DCF8C6;"
    bot_bubble_style = "background-color:#F1F0F0;"

# --- Sidebar thread selection ---
with st.sidebar:
    st.header("🧵 Threads")
    if "threads" not in st.session_state:
        st.session_state.threads = {}

    thread_names = list(st.session_state.threads.keys())
    selected_thread = st.selectbox("Select thread", thread_names + ["➕ New thread"])

    if selected_thread == "➕ New thread":
        new_name = st.text_input("Enter new thread name")
        if new_name and new_name not in st.session_state.threads:
            st.session_state.threads[new_name] = []
            selected_thread = new_name
            st.experimental_rerun()
    elif selected_thread and selected_thread not in st.session_state.threads:
        st.session_state.threads[selected_thread] = []

# --- Context selection ---
st.markdown("Choose a context and start chatting! 🙋‍♀️")
context_source = st.radio("Select context source:", ["📖 Book", "🎞️ Series"])

context_text = ""
if context_source == "📖 Book":
    context_files = [f for f in os.listdir("contexts") if f.endswith(".txt")]
    selected_file = st.selectbox("Choose a message file:", context_files)
    if selected_file:
        with open(os.path.join("contexts", selected_file), "r", encoding="utf-8") as f:
            context_text = f.read()
elif context_source == "🎞️ Series":
    url = st.text_input("Paste your link here (must return raw text):")
    if url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                context_text = response.text
            else:
                st.warning("Couldn't fetch the content from the URL.")
        except Exception as e:
            st.error(f"Error fetching content: {e}")

if context_text:
    st.session_state.context_text = context_text

if "context_text" in st.session_state:
    if "chat" not in st.session_state:
        ctx = st.session_state.context_text
        st.session_state.chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [
                    f"You are the preacher who delivered this message. "
                    "When responding, speak in the first person and directly to the audience. "
                    "Refer to the transcript as 'the message'. Be pastoral, clear, and personal. "
                    f"Here is the message:\n\n{ctx}"
                ]
            },
            {
                "role": "model",
                "parts": ["Understood. I will speak as the preacher and refer to the transcript as the message."]
            }
        ])

# --- Chat input ---
user_input = st.chat_input("Ask a question about the message...")

# --- Display all messages in selected thread ---
scroll_anchor = "scroll-anchor"
if selected_thread in st.session_state.threads:
    for i, msg in enumerate(st.session_state.threads[selected_thread]):
        with st.chat_message("user"):
            st.markdown(f"<div style='{user_bubble_style} padding:10px; border-radius:10px; text-align: right; max-width: 75%; margin-left: auto;'>{msg['question']}</div>", unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(f"<div style='{bot_bubble_style} padding:10px; border-radius:10px; text-align: left; max-width: 75%; margin-right: auto;'>\n<pre style='margin:0; white-space:pre-wrap;'>{msg['answer']}</pre></div>", unsafe_allow_html=True)
            st.code(msg['answer'], language="markdown", line_numbers=False)

    st.markdown(f"<div id='{scroll_anchor}'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <script>
        const anchor = window.parent.document.getElementById('{scroll_anchor}');
        if (anchor) anchor.scrollIntoView({ behavior: 'smooth' });
        </script>
        """,
        unsafe_allow_html=True
    )

# --- Handle new input ---
if user_input and "chat" in st.session_state:
    if any(bad in user_input.lower() for bad in ["kill", "hate", "sex"]):
        st.warning("This question is not allowed.")
    else:
        with st.chat_message("user"):
            st.markdown(f"<div style='{user_bubble_style} padding:10px; border-radius:10px; text-align: right; max-width: 75%; margin-left: auto;'>{user_input}</div>", unsafe_allow_html=True)

        with st.spinner("Brenda is thinking..."):
            response = st.session_state.chat.send_message(user_input)
            assistant_reply = response.text

        with st.chat_message("assistant"):
            st.markdown(f"<div style='{bot_bubble_style} padding:10px; border-radius:10px; text-align: left; max-width: 75%; margin-right: auto;'>\n<pre style='margin:0; white-space:pre-wrap;'>{assistant_reply}</pre></div>", unsafe_allow_html=True)
            st.code(assistant_reply, language="markdown", line_numbers=False)

        feedback = st.radio("Was this helpful?", ["👍 Yes", "👎 No"], index=None, horizontal=True, key=f"feedback_{len(st.session_state.threads[selected_thread])}")
        text_feedback = st.text_area("Optional feedback", placeholder="Leave a comment (optional)...", key=f"textfeedback_{len(st.session_state.threads[selected_thread])}")

        entry = {
            "question": user_input,
            "answer": assistant_reply,
            "feedback": feedback,
            "text_feedback": text_feedback,
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.threads[selected_thread].append(entry)

        with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

# --- Export session ---
if selected_thread in st.session_state.threads and st.session_state.threads[selected_thread]:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬇️ Export as JSON"):
            json_data = json.dumps(st.session_state.threads[selected_thread], indent=2)
            st.download_button("Download JSON", data=json_data, file_name="chat_session.json", mime="application/json")
    with col2:
        if st.button("⬇️ Export as CSV"):
            df = pd.DataFrame(st.session_state.threads[selected_thread])
            csv_data = df.to_csv(index=False)
            st.download_button("Download CSV", data=csv_data, file_name="chat_session.csv", mime="text/csv")

# --- Reset chat ---
if st.button("🔄 Reset Chat"):
    for key in ["chat", "context_text"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
