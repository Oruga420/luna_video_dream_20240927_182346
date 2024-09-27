import time
import logging
import requests
from config import Config
from models.pydantic_models import EnhancedPrompt, VideoGenerationResponse

LUMMA_API_URL = "https://api.lumalabs.ai/dream-machine/v1/generations"
MAX_RETRIES = 60  # 5 minutes with 5-second intervals
RETRY_INTERVAL = 15  # seconds

def generate_video(enhanced_prompt: EnhancedPrompt) -> VideoGenerationResponse:
    headers = {
        "Authorization": f"Bearer {Config.LUMMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": enhanced_prompt.prompt,
        "aspect_ratio": enhanced_prompt.aspect_ratio,
        "duration_seconds": enhanced_prompt.duration
    }
    
    try:
        # Initial request to start video generation
        logging.info(f"Sending initial request to Lumma API with data: {data}")
        response = requests.post(LUMMA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        generation_id = result['id']
        logging.info(f"Video generation started. Generation ID: {generation_id}")
        
        # Polling loop
        for attempt in range(MAX_RETRIES):
            time.sleep(RETRY_INTERVAL)
            logging.info(f"Checking video generation status. Attempt {attempt + 1}/{MAX_RETRIES}")
            status_response = requests.get(f"{LUMMA_API_URL}/{generation_id}", headers=headers)
            status_response.raise_for_status()
            status_result = status_response.json()
            
            if status_result['state'] == 'completed':
                video_url = status_result['assets']['video']
                logging.info(f"Video generation completed. Video URL: {video_url}")
                return VideoGenerationResponse(video_url=video_url, audio_url=None)
            elif status_result['state'] == 'failed':
                failure_reason = status_result.get('failure_reason', 'Unknown reason')
                logging.error(f"Video generation failed: {failure_reason}")
                raise Exception(f"Video generation failed: {failure_reason}")
            else:
                logging.info(f"Video generation in progress. Current state: {status_result['state']}")
        
        logging.error("Video generation timed out")
        raise Exception("Video generation timed out")
    except requests.RequestException as e:
        logging.error(f"Error calling Lumma API: {str(e)}")
        raise Exception(f"Error calling Lumma API: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in generate_video: {str(e)}")
        raise Exception(f"Unexpected error in generate_video: {str(e)}")
