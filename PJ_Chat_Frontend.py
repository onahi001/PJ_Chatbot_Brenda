import streamlit as st
import Processor
import Chatbot_Google_LLM
import youtube_processor as yp
import datetime
import json

# --- UI Setup ---

# Function to design the front (first thing on sight)
def front():
    # Initialise session state variables for each pop-up
    if "show_popup_1" not in st.session_state:
        st.session_state.show_popup_1 = False
    if "show_popup_2" not in st.session_state:
        st.session_state.show_popup_2 = False
        
    st.set_page_config(page_title="Brenda Chatbot", layout="wide")
    st.title("💬 PJ Chatbot")
    st.subheader("Hey! I am Brenda.")
    st.markdown('''<h6 style="color:blue;">
                An assistant for you on some of pastor jackson messages. 
                You can ask me questions on selected messages.</h5>''',
                unsafe_allow_html=True)
    st.markdown("Choose a message and start chatting!")
    message_text = input_display()
    
    # --- Start Chat ---
    if message_text:
        if "chat" not in st.session_state:
            st.session_state.chat = Chatbot_Google_LLM.Model_Setup(message_text)
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
    # Chat input
    user_input = st.chat_input(
        "Hello!\nI am Brenda and I am ready to be of help.")
    
    # --- Display all previous messages ---
    if "messages"  in st.session_state:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message("User"):
                st.markdown(f"""<div style='background-color:#DCF8C6; padding:10px; 
                        border-radius:10px; text-align: left; max-width: 45%; 
                        margin-right: auto;'>{msg['question']}</div>""",
                        unsafe_allow_html=True)
            with st.chat_message("Brenda"):
                st.markdown(f"""<div style='background-color:#F1F0F0; padding:10px; 
                        border-radius:10px; text-align: right; max-width: 75%; 
                        margin-left: auto;'>{msg['answer']}</div>""",
                        unsafe_allow_html=True)
                
        # --- Implementation of a scroll to bottom ---
        st.markdown("""
            <script>
                var chatContainer = window.parent.document.querySelector('.main');
                if (chatContainer){
                    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behaviour: 'smooth'});
                }
            </script>)
        """, unsafe_allow_html=True)
    
    # --- Handle new input ---    
    if user_input and "chat" in st.session_state:
        with st.chat_message("User"):
            st.markdown(f"""<div style='background-color:#DCF8C6; padding:10px; 
                        border-radius:10px; text-align: left; max-width: 45%; 
                        margin-right: auto;'>{user_input}</div>""",
                        unsafe_allow_html=True)
        with st.spinner("Brenda is thinking..."):
            response = Chatbot_Google_LLM.BrendaBrain(st.session_state.chat, user_input)
        
        with st.chat_message("Brenda: "):
            st.markdown(f"""<div style='background-color:#F1F0F0; padding:10px; 
                        border-radius:10px; text-align: right; max-width: 90%; 
                        margin-left: auto;'>{response}</div>""",
                        unsafe_allow_html=True)
        
        # --- Feedback ---
        feedback = st.radio("Was this helpful?", ["👍 Yes", "👎 No"],
                            horizontal=True, key=f"feedback_{len(st.session_state.messages)}")
        
        # Store full message, reply, and feedback
        feedback_data = ({
            "question": user_input,
            "answer": response,
            "feedback": feedback,
            "timestamp": datetime.datetime.now().isoformat()
        })
        st.session_state.messages.append(feedback_data)
        
        # Append feedback to developer log
        with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_data) + "\n")

    # Append
    # --- Reset chat ---
    if st.button("🔄 Reset Chat"):
        if "chat" in st.session_state:
            del st.session_state.chat
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()
        
        
# Functions to control pop-ups separately
def open_popup_1():
    st.session_state.show_popup_1 = True    #Open one popup
    st.session_state.show_popup_2 = False   #Closes other popup
def open_popup_2():
    st.session_state.show_popup_1 = False
    st.session_state.show_popup_2 = True
    
def close_popup_1():
    st.session_state.show_popup_1 = False
def close_popup_2():
    st.session_state.show_popup_2 = False
    
# --- Function to control input logic
def input_display():
    # --- Message Selection ---
    message_source = st.radio("Select Message Source:", 
                            ["📂 Choose from server", "🔗 Provide a Youtube Message Link"])

    # Load context based on option
    message_text = ""

    if message_source == "📂 Choose from server":
        col_1, col_2 = st.columns(2)
        vectorstore = None
        
        with col_1:
            st.button("📖 Messages", on_click=open_popup_1)
            
            if st.session_state.show_popup_1:
                menu_option = st.radio(
                    "Choose a message", ["Relationship Myth", "Demands of Faith", 
                                         "2025 Outpouring Day 1", "2025 Outpouring Day 2"]
                )
                
                if st.button("Submit"):
                    if menu_option == "Relationship Myth":
                        message_text = Processor.json_processor_with_time(
                            "data/Messages/Relationship_Myths.json")
                    if menu_option == "Demands of Faith":
                        message_text = Processor.json_processor_with_time(
                            "data/Messages/Demands_of_Faith.json")
                    if menu_option == "2025 Outpouring Day 1":
                        message_text = Processor.json_processor_with_time(
                            "data/Messages/2025_Outpouring_Day_one.json")
                    if menu_option == "2025 Outpouring Day 2.json":
                        message_text = Processor.json_processor_with_time(
                            "data/Messages/2025_Outpouring_Day_two.json")
                    close_popup_1()
                    
        with col_2:
            st.button("📚 Series", on_click=open_popup_2)
            
            if st.session_state.show_popup_2:
                choice = st.selectbox(
                    "Choose a Series", ["Parables of Jesus", "SOS"]
                )
                
                if st.button("Submit (2)"):
                    print(choice)
                    message_text = Processor.json_processor_with_time(
                        f"data/{choice}/merged_{choice}.json"
                    )
                    close_popup_2()
                    
    # If the using the link option
    elif message_source == "🔗 Provide a Youtube Message Link":
        url = st.text_input("Paste your link here (Youtube Message)")
        if url:
            message_file, error = yp.message_processor(url)
            if error:
                st.error(error)
            else:
                message_text = Processor.json_processor_with_time(message_file)
    # test link = https://www.youtube.com/watch?v=DcCpLlIyEKY
    return message_text

