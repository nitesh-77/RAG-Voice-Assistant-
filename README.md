# RAG - Voice Assistant 🎙️
A personal voice assistant application for experimenting with state-of-the-art transcription, response generation, and text-to-speech models. Supports OpenAI, Groq, Elevanlabs, CartesiaAI, and Deepgram APIs, plus local models via Ollama.
## Features 

- **Modular Design**: Easily switch between different models for transcription, response generation, and TTS.
- **Support for Multiple APIs**: Integrates with OpenAI, Groq, and Deepgram APIs, along with placeholders for local models.
- **Configuration Management**: Centralized configuration in `config.py` for easy setup and management.

## Setup Instructions  
1.**Clone the repository**

```shell
   git clone https://github.com/nitesh-77/RAG-Voice-Assistant-.git
```
2. 🐍 **Set up a virtual environment**

```shell
    conda create --name spark python=3.10
    conda activate spark
```
3. **Install the required packages**

```shell
   pip install -r requirements.txt
```
4. **Set up the environment variables**

Create a  `.env` file in the root directory and add your API keys:
```shell
    OPENAI_API_KEY=your_openai_api_key
    GROQ_API_KEY=your_groq_api_key
    DEEPGRAM_API_KEY=your_deepgram_api_key
    LOCAL_MODEL_PATH=path/to/local/model
```
5.  **Configure the models**

Edit config.py to select the models you want to use:

```shell
    class Config:
        # Model selection
        TRANSCRIPTION_MODEL = 'groq'  # Options: 'openai', 'groq', 'deepgram', 'fastwhisperapi' 'local'
        RESPONSE_MODEL = 'groq'       # Options: 'openai', 'groq', 'ollama', 'local'
        TTS_MODEL = 'deepgram'        # Options: 'openai', 'deepgram', 'elevenlabs', 'local', 'melotts'

        # API keys and paths
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
        LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH")
```
you can also install FastWhisperApi and run locally

6.  **Run the voice assistant**

```shell
   python run_voice_assistant.py
```






