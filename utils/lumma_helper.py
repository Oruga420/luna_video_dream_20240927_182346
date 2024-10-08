import requests
import time
import logging
from config import Config
from models.pydantic_models import EnhancedPrompt, VideoGenerationResponse

def generate_video(enhanced_prompt: EnhancedPrompt, initial_image_path: str = None, final_image_path: str = None, url: str = None) -> VideoGenerationResponse:
    headers = {
        "Authorization": f"Bearer {Config.LUMMA_API_KEY}",
        "Content-Type": "application/json"
    }

    keyframes = {}
    if url:
        keyframes["frame0"] = {
            "type": "image",
            "url": url
        }
    elif initial_image_path:
        initial_image_url = upload_image(initial_image_path)
        keyframes["frame0"] = {
            "type": "image",
            "url": initial_image_url
        }
    
    if final_image_path:
        final_image_url = upload_image(final_image_path)
        keyframes["frame1"] = {
            "type": "image",
            "url": final_image_url
        }

    data = {
        "prompt": enhanced_prompt.prompt,
        "aspect_ratio": enhanced_prompt.aspect_ratio,
        "duration_seconds": enhanced_prompt.duration
    }

    if keyframes:
        data["keyframes"] = keyframes

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

def upload_image(image_path: str) -> str:
    # Implement image upload logic here
    # This function should upload the image to a CDN or storage service and return the URL
    # For now, we'll return a placeholder URL
    return f"https://example.com/uploaded_image_{image_path.split('/')[-1]}"
