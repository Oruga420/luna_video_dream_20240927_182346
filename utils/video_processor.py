import os
import tempfile
import subprocess
import logging
import uuid
import shutil
from typing import Optional
from models.pydantic_models import VideoGenerationResponse, SoundEffectResponse, FinalVideoResponse

def combine_video_and_audio(video: VideoGenerationResponse, audio: SoundEffectResponse) -> FinalVideoResponse:
    if audio.audio_url is None:
        logging.warning("No audio URL provided. Returning original video without audio.")
        return FinalVideoResponse(video_url=video.video_url, audio_url=None)

    try:
        # Create a temporary directory to store the output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_filename = f'output_{uuid.uuid4()}.mp4'
            temp_output_path = os.path.join(temp_dir, output_filename)
            
            # Combine video and audio using ffmpeg
            command = [
                'ffmpeg',
                '-i', video.video_url,
                '-i', audio.audio_url,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                temp_output_path
            ]
            
            logging.info(f"Executing ffmpeg command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"ffmpeg command failed. Error: {result.stderr}")
                return FinalVideoResponse(video_url=video.video_url, audio_url=audio.audio_url)
            
            logging.info("ffmpeg command executed successfully")
            
            # Move the output file to a permanent location
            final_output_path = os.path.join(os.getcwd(), output_filename)
            shutil.move(temp_output_path, final_output_path)
            
            # Convert the local file paths to URLs
            combined_video_url = f"/download_combined/{output_filename}"
            audio_url = f"/download_audio/{os.path.basename(audio.audio_url)}"
            
            logging.info(f"Combined video created at: {combined_video_url}")
            return FinalVideoResponse(video_url=combined_video_url, audio_url=audio_url)
    except Exception as e:
        logging.error(f"Error in combine_video_and_audio: {str(e)}")
        return FinalVideoResponse(video_url=video.video_url, audio_url=audio.audio_url)
    finally:
        # Clean up the temporary audio file
        if audio.audio_url and os.path.exists(audio.audio_url):
            os.remove(audio.audio_url)
            logging.info(f"Temporary audio file removed: {audio.audio_url}")
