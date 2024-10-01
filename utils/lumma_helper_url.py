import requests
import time
import logging
from config import Config
from models.pydantic_models import EnhancedPrompt, VideoGenerationResponse

def generate_video(enhanced_prompt: EnhancedPrompt, initial_image_url: str = None, first_frame_url: str = None, last_frame_url: str = None) -> VideoGenerationResponse:
    headers = {
        "Authorization": f"Bearer {Config.LUMMA_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": enhanced_prompt.prompt,
        "aspect_ratio": enhanced_prompt.aspect_ratio,
        "duration_seconds": enhanced_prompt.duration
    }

    if initial_image_url:
        data["keyframes"] = {
            "frame0": {
                "type": "image",
                "url": initial_image_url
            }
        }
    elif first_frame_url and last_frame_url:
        data["keyframes"] = {
            "frame0": {
                "type": "image",
                "url": first_frame_url
            },
            "frame1": {
                "type": "image",
                "url": last_frame_url
            }
        }

    logging.info(f"Sending initial request to Lumma API with data: {data}")

    response = requests.post("https://api.lumalabs.ai/dream-machine/v1/generations", headers=headers, json=data)
    response.raise_for_status()
    generation_id = response.json()["id"]

    logging.info(f"Video generation started. Generation ID: {generation_id}")

    video_url = None
    max_attempts = 60
    for attempt in range(max_attempts):
        logging.info(f"Checking video generation status. Attempt {attempt + 1}/{max_attempts}")
        status_response = requests.get(f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}", headers=headers)
        status_response.raise_for_status()
        status_data = status_response.json()

        if status_data["state"] == "completed":
            video_url = status_data["assets"]["video"]
            logging.info(f"Video generation completed. Video URL: {video_url}")
            break
        elif status_data["state"] == "failed":
            raise Exception(f"Video generation failed: {status_data.get('failure_reason', 'Unknown reason')}")
        
        logging.info(f"Video generation in progress. Current state: {status_data['state']}")
        time.sleep(5)

    if not video_url:
        raise Exception("Video generation timed out")

    return VideoGenerationResponse(video_url=video_url)