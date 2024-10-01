import os
import time
import requests
from datetime import datetime, timedelta
import base64
from lumaai import LumaAI
from dotenv import load_dotenv

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file
env_path = os.path.join(os.path.dirname(script_dir), '.env')

# Load environment variables from .env file
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    raise FileNotFoundError(f"The .env file was not found at {env_path}")

# Get API keys from environment variables
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
LUMAAI_API_KEY = os.getenv("LUMAI_API_KEY")  # Note the change here to match your .env file

if not IMGBB_API_KEY or not LUMAAI_API_KEY:
    raise ValueError("Please ensure IMGBB_API_KEY and LUMAI_API_KEY are set in your .env file")

print("WARNING: Never share your .env file or API keys publicly. Keep them secure.")

def list_image_files():
    return [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

def choose_image(prompt):
    image_files = list_image_files()
    print("Available images:")
    for i, file in enumerate(image_files):
        print(f"{i + 1}. {file}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(image_files):
                return image_files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def upload_image(image_path):
    with open(image_path, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)
        if res.ok:
            return res.json()['data']['url']
        else:
            print(f"Failed to upload image: {res.text}")
            return None

def create_generation(client, generation_params):
    try:
        generation = client.generations.create(**generation_params)
        print("Generation started. Waiting for completion...")
        print(f"Generation ID: {generation.id}")
        timeout = datetime.now() + timedelta(minutes=5)
        while datetime.now() < timeout:
            status = client.generations.get(id=generation.id)
            if status.state == "completed":
                video_url = status.assets.video
                print("Generation completed successfully!")
                return video_url
            elif status.state == "failed":
                print(f"Generation failed. Reason: {status.failure_reason}")
                return None
            time.sleep(5)
        else:
            print("Generation timed out after 5 minutes. You can check its status later using the generation ID.")
            print(f"Generation ID: {generation.id}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def download_video(video_url):
    if video_url:
        response = requests.get(video_url, stream=True)
        output_file = "luma_generated_video.mp4"
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"Video downloaded and saved as {output_file}")
    else:
        print("Video URL not available. Generation may not have completed successfully.")

def main():
    client = LumaAI(auth_token=LUMAAI_API_KEY)
    print("Choose generation type:")
    print("1. Text to Video")
    print("2. Image to Video")
    print("3. Frame to Frame Video")
    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        prompt = input("Enter your prompt for text-to-video generation: ")
        aspect_ratio = input("Enter aspect ratio (e.g., 16:9, 4:3, 1:1): ")
        params = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio
        }
    elif choice == '2':
        image = choose_image("Choose an image for image-to-video generation (enter the number): ")
        image_url = upload_image(image)
        if not image_url:
            print("Failed to upload image. Exiting.")
            return
        prompt = input("Enter your prompt for image-to-video generation: ")
        params = {
            "prompt": prompt,
            "keyframes": {
                "frame0": {
                    "type": "image",
                    "url": image_url
                }
            }
        }
    elif choice == '3':
        start_image = choose_image("Choose the start image (enter the number): ")
        end_image = choose_image("Choose the end image (enter the number): ")
        start_image_url = upload_image(start_image)
        end_image_url = upload_image(end_image)
        if not start_image_url or not end_image_url:
            print("Failed to upload one or both images. Exiting.")
            return
        prompt = input("Enter your prompt for frame-to-frame video generation: ")
        params = {
            "prompt": prompt,
            "keyframes": {
                "frame0": {
                    "type": "image",
                    "url": start_image_url
                },
                "frame1": {
                    "type": "image",
                    "url": end_image_url
                }
            }
        }
    else:
        print("Invalid choice. Exiting.")
        return

    video_url = create_generation(client, params)
    download_video(video_url)

if __name__ == "__main__":
    main()