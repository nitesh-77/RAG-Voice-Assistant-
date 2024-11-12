import logging
import elevenlabs

from openai import OpenAI
from deepgram import DeepgramClient, SpeakOptions
from elevenlabs.client import ElevenLabs
# from cartesia.tts import CartesiaTTS
from cartesia import Cartesia
import pyaudio
import soundfile as sf
import json


from voice_assistant.local_tts_generation import generate_audio_file_melotts

def text_to_speech(model, api_key, text, output_file_path, local_model_path=None):
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
                voice="fable",
                input=text
            )

            speech_response.stream_to_file(output_file_path)
            # with open(output_file_path, "wb") as audio_file:
            #     audio_file.write(speech_response['data'])  # Ensure this correctly accesses the binary content

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
            ELEVENLABS_VOICE_ID = "Paul J."
            client = ElevenLabs(api_key=api_key)
            audio = client.generate(
                text=text, voice=ELEVENLABS_VOICE_ID, output_format="mp3_22050_32", model="eleven_turbo_v2"
            )
            elevenlabs.save(audio, output_file_path)
        elif model == "cartesia":
            # # config
            # with open('Barbershop Man.json') as f:
            #     voices = json.load(f)

            # # voice_id = voices["Barbershop Man"]["id"]
            # voice = voices["Barbershop Man"]["embedding"]
            # gen_cfg = dict(model_id="upbeat-moon", data_rtype='array', output_format='fp32')

            # # create client
            # client = CartesiaTTS(api_key=api_key)

            # # generate audio
            # output = client.generate(transcript=text, voice=voice, stream=False, **gen_cfg)

            # # save audio to file
            # buffer = output["audio"]
            # rate = output["sampling_rate"]
            # sf.write(output_file_path, buffer, rate) 

            client = Cartesia(api_key=api_key)
            # voice_name = "Barbershop Man"
            voice_id = "f114a467-c40a-4db8-964d-aaba89cd08fa"#"a0e99841-438c-4a64-b679-ae501e7d6091"
            voice = client.voices.get(id=voice_id)

            # You can check out our models at https://docs.cartesia.ai/getting-started/available-models
            model_id = "sonic-english"

            # You can find the supported `output_format`s at https://docs.cartesia.ai/api-reference/endpoints/stream-speech-server-sent-events
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

                if not stream:
                    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)

                # Write the audio data to the stream
                stream.write(buffer)

            stream.stop_stream()
            stream.close()
            p.terminate()



        elif model == "melotts": # this is a local model
            generate_audio_file_melotts(text=text, filename=output_file_path)
        elif model == 'local':
            # Placeholder for local TTS model
            with open(output_file_path, "wb") as f:
                f.write(b"Local TTS audio data")
        else:
            raise ValueError("Unsupported TTS model")
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")