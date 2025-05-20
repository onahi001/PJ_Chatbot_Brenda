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

    # --- UI Setup ---
    st.set_page_config(page_title="Brenda Chatbot", layout="wide")
    st.title("💬 PJ Chatbot")
    
    # --- Detect system theme ---
    if "theme" not in st.session_state:
        if st.get_option("theme.base") == "dark":
            st.session_state.theme ="dark"
        else:
            st.session_state.theme = "light"
    theme = st.session_state.theme
       
    # ---Setting theme colours ---
    if theme == "dark":
        user_chat_BG = "background-color:#333333; color:white;"
        brenda_chat_BG = "background-color:#444444; color:white;"
    else:
        user_chat_BG = "background-color:#DCF8C6;"
        brenda_chat_BG = "background-color:#F1F0F0;"
    
    # --- Creating a theme toggle ---
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    if dark_mode:
        user_chat_BG = "background-color:#333333; color:white;"
        brenda_chat_BG = "background-color:#444444; color:white;"
        sub_colour = "#007BFF"
    else:
        user_chat_BG = "background-color:#DCF8C6;"
        brenda_chat_BG = "background-color:#F1F0F0;"
        sub_colour = "#0F52BA"
        
    # --- Thread selection ---
    #if "threads" not in st.session_state:
    #    st.session_state.threads = {}
        
    #thread_names = list(st.session_state.threads.keys())
    
    st.subheader("Hey! I am Brenda.")
    st.markdown(f'''<h6 style="color:{sub_colour};">
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
                st.markdown(f"""<div style='{user_chat_BG} padding:10px; 
                        border-radius:10px; text-align: left; max-width: 45%; 
                        margin-right: auto;'>{msg['question']}</div>""",
                        unsafe_allow_html=True)
            with st.chat_message("Brenda"):
                st.markdown(f"""<div style='{brenda_chat_BG} padding:10px; 
                        border-radius:10px; text-align: right; max-width: 75%; 
                        margin-left: auto; white-space: pre-wrap; position: relative;'>
                        <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" 
                        style="position:absolute; top:5px; right:5px;">📋</button>
                        <div>{msg['answer']}</div>
                        </div>""",
                        unsafe_allow_html=True)
                
        # --- Implementation of a scroll to bottom ---
        scroll_anchor = "scroll-anchor"
        st.markdown(f"<div id='{scroll_anchor}'></div>", unsafe_allow_html=True)
        st.markdown("""
            <script>
                const anchor = window.parent.document.getElementById('{scroll_anchor}');
                if (anchor) anchor.scrollIntoView({ behavior: 'smooth' });
            </script>)
        """, unsafe_allow_html=True)
    
    # --- Handle new input ---    
    if user_input and "chat" in st.session_state:
        with st.chat_message("User"):
            st.markdown(f"""<div style='{user_chat_BG} padding:10px; 
                        border-radius:10px; text-align: left; max-width: 45%; 
                        margin-right: auto;'>{user_input}</div>""",
                        unsafe_allow_html=True)
        with st.spinner("Brenda is thinking..."):
            response = Chatbot_Google_LLM.BrendaBrain(st.session_state.chat, user_input)
        
        with st.chat_message("Brenda: "):
            st.markdown(f"""<div style='{brenda_chat_BG} padding:10px; 
                        border-radius:10px; text-align: right; max-width: 75%; 
                        margin-left: auto; white-space: pre-wrap; position: relative;'>
                        <button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" 
                        style="position:absolute; top:5px; right:5px;">📋</button>
                        <div>{response}</div>
                        </div>""",
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
                    "Choose a message", ["Relationship Myths", "Demands of Faith",
                                         "Be Sober & Be Vigilant", "Business Beyond Grace",
                                         "Crossover Service 2024", "I Am, I Can & I Have",
                                         "Handling Post Traumatic Experiences",
                                         "The Origin of the Blessing",
                                         "2025 Outpouring Day One", "2025 Outpouring Day Two"]
                )
                
                if st.button("Submit"):
                    message_text = Processor.json_processor_with_time(
                        f"data/Messages/{menu_option}.json")
                    close_popup_1()
                    
        with col_2:
            st.button("📚 Series", on_click=open_popup_2)
            
            if st.session_state.show_popup_2:
                choice = st.selectbox(
                    "Choose a Series", ["Parables of Jesus", "SOS",
                                        "Bible Perspective on Marriage",
                                        "Spiritual Growth", "The Honour Code"
                                        ]
                )
                
                if st.button("Submit"):
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

