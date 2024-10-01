import os
import tempfile
from elevenlabs.client import ElevenLabs
from config import Config
from models.pydantic_models import SoundEffectResponse

def generate_sound_effect(text: str):
    try:
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        result = client.text_to_sound_effects.convert(
            text=text,
            duration_seconds=10,  # Adjust this value as needed
            prompt_influence=0.3,  # Adjust this value as needed
        )
        
        # Save the result to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        for chunk in result:
            temp_file.write(chunk)
        temp_file.close()
        
        return SoundEffectResponse(audio_url=temp_file.name)
    except Exception as e:
        print(f"Error generating sound effect: {str(e)}")
        return SoundEffectResponse(audio_url=None)
