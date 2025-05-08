# voice_assistant/text_to_speech.py
import logging
import json
import pyaudio
import elevenlabs
import soundfile as sf
import requests

from openai import OpenAI
from deepgram import DeepgramClient, SpeakOptions
from elevenlabs.client import ElevenLabs
from cartesia import Cartesia

from voice_assistant.config import Config
from voice_assistant.local_tts_generation import generate_audio_file_melotts

def text_to_speech(model: str, api_key:str, text:str, output_file_path:str, local_model_path:str=None):
    """
    Convert text to speech using the specified model.
    
    Args:
    model (str): The model to use for TTS ('openai', 'deepgram', 'elevenlabs', 'local').
    api_key (str): The API key for the TTS service.
    text (str): The text to convert to speech.
    output_file_path (str): The path to save the generated speech audio file.
    local_model_path (str): The path to the local model (if applicable).
    """
    
    try:
        if model == 'openai':
            client = OpenAI(api_key=api_key)
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )

            speech_response.stream_to_file(output_file_path)

        elif model == 'deepgram':
            client = DeepgramClient(api_key=api_key)
            options = SpeakOptions(
                model="aura-arcas-en", #"aura-luna-en", # https://developers.deepgram.com/docs/tts-models
                encoding="linear16",
                container="wav"
            )
            SPEAK_OPTIONS = {"text": text}
            response = client.speak.v("1").save(output_file_path, SPEAK_OPTIONS, options)
        
        elif model == 'elevenlabs':
            try:
                client = ElevenLabs(api_key=api_key)

                # Use your custom voice ID directly
                voice_id = "piTKgcLEGmPE4e6mEKli"
                logging.info(f"Using ElevenLabs custom voice ID: {voice_id}")

                # Generate audio using the selected voice ID
                audio = client.generate(
                    text=text,
                    voice=voice_id,
                    output_format="pcm_16000",  
                    model="eleven_turbo_v2"
                )

                # Save as WAV file
                temp_mp3_path = output_file_path + ".temp"
                elevenlabs.save(audio, temp_mp3_path)

                import io
                import numpy as np
                import soundfile as sf

                with open(temp_mp3_path, 'rb') as f:
                    audio_data = f.read()

                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                sf.write(output_file_path, audio_np, 16000)

                import os
                os.remove(temp_mp3_path)

                logging.info(f"ElevenLabs audio saved to {output_file_path} in WAV format")

            except Exception as e:
                logging.error(f"ElevenLabs error: {str(e)}")
                raise

        
        elif model == "cartesia":
            client = Cartesia(api_key=api_key)
            
            voice_id = "f114a467-c40a-4db8-964d-aaba89cd08fa"#"a0e99841-438c-4a64-b679-ae501e7d6091"
            voice = client.voices.get(id=voice_id)

            
            model_id = "sonic-english"

            
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }

            p = pyaudio.PyAudio()
            rate = 44100

            stream = None

            # Generate and stream audio
            for output in client.tts.sse(
                model_id=model_id,
                transcript=text,
                voice_embedding=voice["embedding"],
                stream=True,
                output_format=output_format,
            ):
                buffer = output["audio"]

                if stream is None:
                    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)

                # Write the audio data to the stream
                stream.write(buffer)
            
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()

        elif model == "melotts": # this is a local model
            generate_audio_file_melotts(text=text, filename=output_file_path)

        elif model == "piper":  # this is a local model
            try:
                response = requests.post(
                    f"{Config.PIPER_SERVER_URL}/synthesize/",
                    json={"text": text},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    with open(Config.PIPER_OUTPUT_FILE, "wb") as f:
                        f.write(response.content)
                    logging.info(f"Piper TTS output saved to {Config.PIPER_OUTPUT_FILE}")
                else:
                    logging.error(f"Piper TTS API error: {response.status_code} - {response.text}")

            except Exception as e:
                logging.error(f"Piper TTS request failed: {e}")
        
        elif model == 'local':
            with open(output_file_path, "wb") as f:
                f.write(b"Local TTS audio data")
        
        else:
            raise ValueError("Unsupported TTS model")
        
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")