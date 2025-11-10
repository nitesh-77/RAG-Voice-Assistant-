import logging
import time
import os
import wave
import numpy as np
from openai import OpenAI
from cartesia import Cartesia
from elevenlabs.client import ElevenLabs
from voice_assistant.local_tts_generation import generate_audio_file_melotts

logging.basicConfig(level=logging.INFO)

def text_to_speech(model, api_key, text, output_file_path, local_model_path=None):
    """Generate speech from text using specified TTS model"""
    start_time = time.time()
    logging.info(f"🚀 Starting {model.upper()} TTS")
    
    try:
        if model == "openai":
            result = openai_tts(api_key, text, output_file_path)
        elif model == "elevenlabs":
            result = elevenlabs_tts(api_key, text, output_file_path)
        elif model == "cartesia":
            result = cartesia_tts(api_key, text, output_file_path)
        elif model == "melotts":
            result = melotts_tts(api_key, text, output_file_path)
        else:
            raise ValueError(f"Unknown TTS model: {model}")
        
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"✅ {model.upper()} TTS completed in: {total_time:.2f}s")
        return result
    
    except Exception as e:
        logging.error(f"❌ {model} TTS error: {e}")
        raise

def elevenlabs_tts(api_key, text, output_file_path):
    """Ultrafast ElevenLabs TTS - Performance optimized"""
    client = ElevenLabs(api_key=api_key)
    
    # Get fastest available voice
    voices = client.voices.get_all()
    selected_voice = voices.voices[0] if len(voices.voices) > 0 else None
    
    if not selected_voice:
        raise Exception("No voices available in ElevenLabs")
    
    logging.info(f"🎤 ElevenLabs voice: {selected_voice.name}")
    
    # Generate audio with speed optimization - using text_to_speech method
    # Updated to newer model that's available on free tier
    audio_content = client.text_to_speech.convert(
        voice_id=selected_voice.voice_id,
        text=text,
        model_id="eleven_turbo_v2_5",
        output_format="mp3_44100_128"
    )

    # Save as MP3 - handle generator input
    with open(output_file_path, 'wb') as f:
        if hasattr(audio_content, 'content'):
            f.write(audio_content.content)
        elif hasattr(audio_content, '__iter__'):
            # Handle generator/iterator
            f.write(b''.join(audio_content))
        else:
            f.write(audio_content)
    
    return output_file_path

def cartesia_tts(api_key, text, output_file_path):
    """Optimized Cartesia TTS with voice caching"""
    client = Cartesia(api_key=api_key)
    
    # Cached voice
    voice_id = "f114a467-c40a-4db8-964d-aaba89cd08fa"
    voice = client.voices.get(id=voice_id)
    
    # Prepare voice parameters
    from cartesia.tts.requests.tts_request_embedding_specifier import TtsRequestEmbeddingSpecifierParams
    voice_params = TtsRequestEmbeddingSpecifierParams(embedding=voice.embedding)
    
    # Speed-optimized format
    from cartesia.tts.requests.output_format import OutputFormat_RawParams
    output_format = OutputFormat_RawParams(container='raw', encoding='pcm_f32le', sample_rate=22050)
    
    # Generate audio
    audio_bytes = b''.join(client.tts.bytes(
        model_id='sonic-english',
        transcript=text,
        voice=voice_params,
        output_format=output_format,
    ))
    
    # Convert PCM to WAV
    audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
    audio_16bit = (audio_array * 32767).astype(np.int16)
    
    with wave.open(output_file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes(audio_16bit.tobytes())
    
    return output_file_path

def openai_tts(api_key, text, output_file_path):
    """Standard OpenAI TTS"""
    client = OpenAI(api_key=api_key)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    
    response.stream_to_file(output_file_path)
    return output_file_path

def melotts_tts(api_key, text, output_file_path):
    """MeloTTS local generation"""
    generate_audio_file_melotts(text=text, filename=output_file_path)
    return output_file_path