# app.py

import streamlit as st
import time
import os
import logging
import threading
import tempfile
from datetime import datetime
import base64
import json


from voice_assistant.audio import record_audio, play_audio, stop_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.utils import delete_file
from voice_assistant.config import Config
from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to autoplay audio
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Function for recording state
def start_recording():
    with st.spinner("Recording..."):
        record_audio(Config.INPUT_AUDIO)
    return True

# Function to save API keys to .env file
def save_api_keys(keys_dict):
    try:
        
        env_path = '.env'
        env_content = {}
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value
        
        
        for key, value in keys_dict.items():
            if value:  
                env_content[key] = value
        
        
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        return True
    except Exception as e:
        logging.error(f"Error saving API keys: {e}")
        return False

# Main app function
def main():
    st.set_page_config(
        page_title="Spark Voice Assistant",
        page_icon="🎤",
        layout="wide",
    )
    st.markdown("""
        <style>
        * {
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif !important;
            color: #d1d5db;
        }

        .block-container {
            background-color: #0d0d0d;
            padding: 2rem;
            border-radius: 12px;
        }

        /* Title */
        .stMarkdown h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #f3f4f6;
            text-align: center;
        }

        /* Chat bubbles */
        .stChatMessage {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* Primary buttons */
        .stButton button {
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            background-color: #1f2937;  /* dark gray */
            color: #f3f4f6;
            font-weight: 500;
            border: 1px solid #374151;
        }
        .stButton button:hover {
            background-color: #374151;  /* slightly lighter gray */
            color: #f9fafb;
        }

        /* Stop button styling */
        div[data-testid="stButton"][aria-label="stop_button_top"] button {
            background-color: #ef4444 !important;
            color: white !important;
            border: none !important;
        }
        div[data-testid="stButton"][aria-label="stop_button_top"] button:hover {
            background-color: #dc2626 !important;
        }

        /* Inputs & dropdowns */
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            background-color: #1f2937 !important;
            color: #d1d5db !important;
            border: 1px solid #374151 !important;
        }

        section[tabindex] {
            background-color: #111827 !important;
            border: 1px solid #374151 !important;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)






    
    st.sidebar.title("Settings")
    
    
    tts_options = ["openai", "elevenlabs", "deepgram", "melotts", "cartesia", "local"]
    selected_tts = st.sidebar.selectbox(
        "Text-to-Speech Model",
        tts_options,
        index=tts_options.index(Config.TTS_MODEL) if Config.TTS_MODEL in tts_options else 0
    )
    
    
    if selected_tts == "openai":
        tts_voice = st.sidebar.selectbox(
            "OpenAI Voice",
            ["nova", "alloy", "echo", "fable", "onyx", "shimmer"],
            index=0
        )
    elif selected_tts == "elevenlabs":
        tts_voice = st.sidebar.selectbox(
            "ElevenLabs Voice",
            ["Paul J.", "Rachel", "Domi", "Adam", "Antoni", "Bella"],
            index=0
        )
    
    
    transcription_options = ["groq", "openai", "deepgram", "fastwhisperapi", "local"]
    selected_transcription = st.sidebar.selectbox(
        "Transcription Model",
        transcription_options,
        index=transcription_options.index(Config.TRANSCRIPTION_MODEL) if Config.TRANSCRIPTION_MODEL in transcription_options else 0
    )
    
    
    response_options = ["groq", "openai", "ollama", "local"]
    selected_response = st.sidebar.selectbox(
        "Response Model",
        response_options,
        index=response_options.index(Config.RESPONSE_MODEL) if Config.RESPONSE_MODEL in response_options else 0
    )
    
    
    if selected_response == "groq":
        llm_options = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
        selected_llm = st.sidebar.selectbox(
            "Groq LLM",
            llm_options,
            index=llm_options.index(Config.GROQ_LLM) if Config.GROQ_LLM in llm_options else 0
        )
    elif selected_response == "openai":
        llm_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        selected_llm = st.sidebar.selectbox(
            "OpenAI LLM",
            llm_options,
            index=llm_options.index(Config.OPENAI_LLM) if Config.OPENAI_LLM in llm_options else 0
        )
    elif selected_response == "ollama":
        llm_options = ["llama3:8b", "llama3:70b", "mistral:7b"]
        selected_llm = st.sidebar.selectbox(
            "Ollama LLM",
            llm_options,
            index=llm_options.index(Config.OLLAMA_LLM) if Config.OLLAMA_LLM in llm_options else 0
        )
    
    
    if st.sidebar.button("Apply Settings"):
        Config.TTS_MODEL = selected_tts
        Config.TRANSCRIPTION_MODEL = selected_transcription
        Config.RESPONSE_MODEL = selected_response
        
        if selected_response == "groq":
            Config.GROQ_LLM = selected_llm
        elif selected_response == "openai":
            Config.OPENAI_LLM = selected_llm
        elif selected_response == "ollama":
            Config.OLLAMA_LLM = selected_llm
            
        st.sidebar.success("Settings applied!")
    
    
    with st.sidebar.expander("API Keys", expanded=False):
        openai_key = st.text_input("OpenAI API Key", type="password", value=Config.OPENAI_API_KEY or "")
        groq_key = st.text_input("Groq API Key", type="password", value=Config.GROQ_API_KEY or "")
        deepgram_key = st.text_input("Deepgram API Key", type="password", value=Config.DEEPGRAM_API_KEY or "")
        elevenlabs_key = st.text_input("ElevenLabs API Key", type="password", value=Config.ELEVENLABS_API_KEY or "")
        cartesia_key = st.text_input("Cartesia API Key", type="password", value=Config.CARTESIA_API_KEY or "")
        
        if st.button("Save API Keys"):
            keys_dict = {
                "OPENAI_API_KEY": openai_key,
                "GROQ_API_KEY": groq_key,
                "DEEPGRAM_API_KEY": deepgram_key,
                "ELEVENLABS_API_KEY": elevenlabs_key,
                "CARTESIA_API_KEY": cartesia_key
            }
            if save_api_keys(keys_dict):
                st.success("API Keys saved to .env file!")
            else:
                st.error("Failed to save API keys.")

    # Service Status
    with st.sidebar.expander("Service Status", expanded=False):
        if st.button("Check FastWhisperAPI"):
            try:
                from voice_assistant.transcription import check_fastwhisperapi
                check_fastwhisperapi()
                st.success("FastWhisperAPI is running")
            except Exception as e:
                st.error(f"FastWhisperAPI is not running: {str(e)}")
        
        if st.button("Check MeloTTS"):
            try:
                import requests
                response = requests.get(f"http://localhost:{Config.TTS_PORT_LOCAL}/health")
                if response.status_code == 200:
                    st.success("MeloTTS is running")
                else:
                    st.error("MeloTTS is not responding properly")
            except Exception as e:
                st.error(f"MeloTTS is not running: {str(e)}")

    
    st.markdown("""
        <h1 style="text-align:center; margin-bottom: 0.5rem;">🤖 Spark Voice Assistant</h1>
        <p style="text-align:center; font-size: 1rem; color: #9ca3af;">
            Your personal assistant — ready to help.
        </p>
    """, unsafe_allow_html=True)


    
    # Metrics display row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Transcription", value=Config.TRANSCRIPTION_MODEL)
    with col2:
        st.metric(label="Response", value=Config.RESPONSE_MODEL)
    with col3:
        st.metric(label="TTS", value=Config.TTS_MODEL)

    
    # Stop speaking button
    stop_col = st.columns([1])[0]
    with stop_col:
        if st.button("🛑 Stop Speaking", key="stop_button_top", use_container_width=True):
            stop_audio()
            st.info("Playback stopped. You can now speak again.")

    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{
            "role": "system",
            "content": """You are spark, a comprehensive personal assistant with access to the user's calendar, emails, tasks, weather information, news, contacts, and expenses. 
            Use the provided functions to retrieve information and assist the user. Always provide thoughtful and detailed responses. Assume today's date is 2025-03-10"""
        }]
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm Spark"
        })
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🎤 Record", key="record_button", use_container_width=True):
            recording_complete = start_recording()
            
            if recording_complete:
                try:
                    
                    transcription_api_key = get_transcription_api_key()
                    
                    
                    with st.spinner("Transcribing audio..."):
                        user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, transcription_api_key, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)
                    
                    if not user_input:
                        st.error("No speech detected. Please try again.")
                    else:
                        
                        process_user_input(user_input, chat_container)
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    logging.error(f"An error occurred: {e}")
    
    
    user_input = st.chat_input("Or type your message here...")
    if user_input:
        process_user_input(user_input, chat_container)

def process_user_input(user_input, chat_container):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    
    if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
        with chat_container:
            with st.chat_message("assistant"):
                st.write("Goodbye! It was nice chatting with you.")
        st.session_state.chat_history.append({"role": "assistant", "content": "Goodbye! It was nice chatting with you."})
        return
    
    # Generate response with a spinner to show loading
    with st.spinner("Thinking..."):
        try:
            
            response_api_key = get_response_api_key()
            
            
            response_text = generate_response(Config.RESPONSE_MODEL, response_api_key, st.session_state.chat_history, Config.LOCAL_MODEL_PATH)
            
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(response_text)
            
            
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            
            
            if Config.TTS_MODEL in ['openai', 'elevenlabs', 'melotts', 'cartesia']:
                output_file = 'output.mp3'
            else:
                output_file = 'output.wav'
            
            
            tts_api_key = get_tts_api_key()
            
            
            with st.spinner("Generating audio response..."):
                text_to_speech(Config.TTS_MODEL, tts_api_key, response_text, output_file, Config.LOCAL_MODEL_PATH)
                
                
                if Config.TTS_MODEL != "cartesia":
                    autoplay_audio(output_file)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"An error occurred: {e}")
            
    # Optionally clean up files (commented out to match your original behavior)
    # delete_file(Config.INPUT_AUDIO)
    # if Config.TTS_MODEL != "cartesia":
    #     delete_file(output_file)

if __name__ == "__main__":
    main()