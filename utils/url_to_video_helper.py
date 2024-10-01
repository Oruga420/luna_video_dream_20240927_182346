import requests
import time
from config import Config
from models.pydantic_models import VideoGenerationResponse

def generate_video_from_url(url: str, prompt: str) -> VideoGenerationResponse:
    headers = {
        "Authorization": f"Bearer {Config.LUMMA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "keyframes": {
            "frame0": {
                "type": "image",
                "url": url
            }
        }
    }

    response = requests.post("https://api.lumalabs.ai/dream-machine/v1/generations", headers=headers, json=payload)
    response.raise_for_status()
    generation_id = response.json()["id"]

    video_url = None
    max_attempts = 60
    for attempt in range(max_attempts):
        status_response = requests.get(f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}", headers=headers)
        status_response.raise_for_status()
        status_data = status_response.json()

        if status_data["state"] == "completed":
            video_url = status_data["assets"]["video"]
            break
        elif status_data["state"] == "failed":
            raise Exception(f"Video generation failed: {status_data.get('failure_reason', 'Unknown reason')}")
        
        time.sleep(5)

    if not video_url:
        raise Exception("Video generation timed out")

    return VideoGenerationResponse(video_url=video_url)
