import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LUMMA_API_KEY = os.getenv("LUMMA_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "qMfbtjrTDTlGtBy52G6E")
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
