import logging
from utils.image_to_url_helper import upload_image
from config import Config

def upload_first_last_frames(first_image_path, last_image_path):
    try:
        first_image_url = upload_image(Config.IMAGEDB_API_KEY, image_path=first_image_path)
        print(f"First frame URL: {first_image_url}")
        
        last_image_url = upload_image(Config.IMAGEDB_API_KEY, image_path=last_image_path)
        print(f"Last frame URL: {last_image_url}")
        
        return first_image_url, last_image_url
    except Exception as e:
        logging.error(f"Error uploading images: {str(e)}")
        return None, None
