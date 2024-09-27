import os
import uuid
import logging
import requests
from config import Config
from models.pydantic_models import SoundEffectRequest, SoundEffectResponse

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

def generate_sound_effect(sound_effect_request: SoundEffectRequest) -> SoundEffectResponse:
    if not Config.ELEVENLABS_API_KEY:
        logging.warning("ElevenLabs API key is not set. Skipping audio generation.")
        return SoundEffectResponse(audio_url=None)

    headers = {
        "xi-api-key": Config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": sound_effect_request.description,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        logging.info(f"Sending request to ElevenLabs API with data: {data}")
        response = requests.post(f"{ELEVENLABS_API_URL}/{Config.ELEVENLABS_VOICE_ID}", headers=headers, json=data)
        logging.info(f"Received response from ElevenLabs API. Status code: {response.status_code}")
        logging.info(f"Response headers: {response.headers}")
        logging.info(f"Response content: {response.content[:100]}...")  # Log first 100 bytes of content
        
        response.raise_for_status()
        
        # Save the audio data to a file in the root directory
        file_name = f"sound_effect_{uuid.uuid4()}.mp3"
        file_path = os.path.join(os.getcwd(), file_name)
        with open(file_path, 'wb') as audio_file:
            audio_file.write(response.content)

        logging.info(f"Sound effect generated and saved to: {file_path}")
        return SoundEffectResponse(audio_url=file_path)
    except requests.RequestException as e:
        logging.error(f"Error calling ElevenLabs API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response content: {e.response.content}")
        return SoundEffectResponse(audio_url=None)
