import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import datetime


# File to save the chat
LOG_FILE = "chat_history_log.txt"

# Function to Log the history of chat
def log_to_file(question, answer, feedback="n/a"):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n--- {datetime.datetime.now()} ---\n")
        log_file.write(f"User: {question}\n")
        log_file.write(f"Brenda: {answer}\n")
        log_file.write(f"Feedback: {feedback}\n")
        
# Function to clear the chat history and begin fresh chat
def reset_chat(initial_context, model):
    return model.start_chat (history = [
        {"role": "user", "parts":[
            f"""You are Brenda, a kind, knowledgeable preacher who helps people
                explore spiritual truths as found in the transcript of the preacher. 
                You answer question using the tone of the speaker and the pattern of 
                speaker and do not provide any answers which cannot be gotten from the 
                transcript aside quoting biblical scriptures. Use this content to answer 
                their questions with insight, clarity and gentleness. Speak like the preacher 
                who delivered the message. Speak to the audience directly in first person, using 
                a pastoral and clear tone. Refer to the transcript as 'the message' throughout. 
                Refer to the preacher using the name of preacher. For this chatbot, most of the 
                time the preacher is Pastor Jackson Adebisi.
                Give Biblical references a biblical scripture was used:\n\n  {initial_context}"""
            ]
        },
        {"role": "model", "parts": ["""Understood. I will speak as the preacher who is Pastor 
                                    Jackson and refer to the transcript as the message."""]}
    ])
    

def Model_Setup(message_text):   
    # Loading the variables from .env
    load_dotenv()

    # Getting the API key from the environment
    api_key = (
        os.getenv("GEMINI_API_KEY") or
        st.secrets.get("GEMINI_API_KEY")
    )

    # checking and ensuring that api key is present
    if not api_key:
        raise ValueError("Missing Gemini Api Key in .env file.\n Check it is assigned to GEMINI_API_KEY")

    # configuring the Gemini Model
    genai.configure(api_key=api_key)

    # Selecting a large context window
    model_name = 'gemini-1.5-flash'

    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(
        history=[
            {"role": "user", "parts":[
                f"""You are Brenda, a kind, knowledgeable assistant who helps people
                    explore spiritual truths as found in the transcript of the preacher. 
                    You answer question using the tone of the speaker and the pattern of 
                    speaker and do not provide any answers which cannot be gotten from the 
                    transcript aside quoting biblical scriptures. Use this content to answer 
                    their questions with insight, clarity and gentleness. Give Biblical 
                    references where the preacher used a biblical scripture:\n\n  {message_text}"""
                ]
            },
            {"role": "model", "parts": ["Got it! I'm ready to be of great help"]}
        ]
    )
    return chat

# Main chatbot loop
def BrendaBrain(model_chat, user_input):
    response = model_chat.send_message(user_input)
    return response.text
