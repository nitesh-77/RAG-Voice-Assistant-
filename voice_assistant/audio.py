import pyaudio
import wave
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, duration=5, retries=3):
    """
    Record audio from the microphone and save it as a WAV file.

    Args:
    file_path (str): The path to save the recorded audio file.
    duration (int): Duration of the recording in seconds.
    retries (int): Number of retries if recording fails.
    """
    for attempt in range(retries):
        try:
            # Set up parameters for recording
            chunk = 1024  # Record in chunks of 1024 samples
            sample_format = pyaudio.paInt16  # 16 bits per sample
            channels = 1
            fs = 44100  # Record at 44100 samples per second

            p = pyaudio.PyAudio()  # Create an interface to PortAudio

            logging.info("Recording started")
            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=fs,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []  # Initialize array to store frames

            # Store data in chunks for the specified duration
            for _ in range(0, int(fs / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()

            logging.info("Recording complete")

            # Save the recorded data as a WAV file
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))
            wf.close()

            logging.info(f"Audio recorded and saved to {file_path}")

            # Verify that the file was created
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Recorded file not found: {file_path}")
            return
        except Exception as e:
            logging.error(f"Failed to record audio: {e}")
            if attempt == retries - 1:
                raise

    logging.error("Recording failed after all retries")

def play_audio(file_path):
    """
    Play an audio file using pyaudio.

    Args:
    file_path (str): The path to the audio file to play.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Set up parameters for playback
        chunk = 1024

        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(chunk)

        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()

        logging.info(f"Audio playback complete for {file_path}")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while playing audio: {e}")

def transcribe_audio(file_path):
    """
    Transcribe the audio file using an external API.

    Args:
    file_path (str): The path to the audio file to transcribe.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for transcription: {file_path}")

        logging.info(f"HTTP Request: POST https://api.groq.com/openai/v1/audio/transcriptions")
        # Simulate HTTP request
        # response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", files={'file': open(file_path, 'rb')})

        # Simulate response
        response = {"status_code": 400, "json": lambda: {'error': {'message': 'file is empty', 'type': 'invalid_request_error'}}}

        if response["status_code"] != 200:
            error_message = response["json"]().get('error', {}).get('message', 'Unknown error')
            raise ValueError(f"Error code: {response['status_code']} - {error_message}")

        logging.info("Transcription successful")
    except FileNotFoundError as e:
        logging.error(f"Failed to transcribe audio: {e}")
    except ValueError as e:
        logging.error(f"Failed to transcribe audio: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def main():
    file_path = "test.wav"

    if record_audio(file_path):
        transcribe_audio(file_path)
        try:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        except PermissionError as e:
            logging.error(f"Permission denied when trying to delete file: {e}")
        except Exception as e:
            logging.error(f"Failed to delete file: {e}")

if __name__ == "__main__":
    main()