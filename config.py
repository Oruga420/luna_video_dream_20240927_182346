import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LUMMA_API_KEY = os.getenv('LUMMA_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    IMAGEDB_API_KEY = os.getenv('IMAGEDB_API_KEY')
