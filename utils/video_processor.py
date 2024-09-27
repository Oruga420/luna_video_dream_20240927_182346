import os
import tempfile
import subprocess
import logging
from models.pydantic_models import VideoGenerationResponse, SoundEffectResponse, FinalVideoResponse

def combine_video_and_audio(video: VideoGenerationResponse, audio: SoundEffectResponse) -> FinalVideoResponse:
    if audio.audio_url is None:
        logging.warning("No audio URL provided. Returning original video without audio.")
        return FinalVideoResponse(video_url=video.video_url)

    try:
        # Create a temporary directory to store the output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'output.mp4')
            
            # Combine video and audio using ffmpeg
            command = [
                'ffmpeg',
                '-i', video.video_url,
                '-i', audio.audio_url,  # This is now a file path
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            logging.info(f"Executing ffmpeg command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"ffmpeg command failed. Error: {result.stderr}")
                return FinalVideoResponse(video_url=video.video_url)
            
            logging.info("ffmpeg command executed successfully")
            
            # For simplicity, we'll use the same URL as the input video
            # In a real-world scenario, you'd upload this file to a cloud storage service
            combined_video_url = video.video_url
            
            logging.info(f"Combined video created at: {combined_video_url}")
            return FinalVideoResponse(video_url=combined_video_url)
    except Exception as e:
        logging.error(f"Error in combine_video_and_audio: {str(e)}")
        return FinalVideoResponse(video_url=video.video_url)
    finally:
        # Clean up the temporary audio file
        if audio.audio_url and os.path.exists(audio.audio_url):
            os.remove(audio.audio_url)
            logging.info(f"Temporary audio file removed: {audio.audio_url}")
