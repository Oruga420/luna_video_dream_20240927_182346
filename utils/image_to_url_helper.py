import requests
import base64
import os

def upload_image(api_key, image_path=None, image_url=None):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
    }

    if image_path:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"The file {image_path} does not exist.")
        with open(image_path, "rb") as file:
            payload["image"] = base64.b64encode(file.read())
    elif image_url:
        payload["image"] = image_url
    else:
        raise ValueError("Either image_path or image_url must be provided")

    try:
        response = requests.post(url, payload)
        response.raise_for_status()
        json_data = response.json()
        if json_data["success"]:
            return json_data["data"]["url"]
        else:
            raise Exception(f"Upload failed: {json_data.get('error', {}).get('message', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error occurred: {str(e)}")
