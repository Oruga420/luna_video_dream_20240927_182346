import logging
from flask import Flask, render_template, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
import os
import requests
from models.pydantic_models import VideoGenerationRequest, FinalVideoResponse
from utils.openai_helper import generate_enhanced_prompt, generate_sound_effect_description
from utils.lumma_helper_url import generate_video
from utils.elevenlabs_helper import generate_sound_effect
from utils.video_processor import combine_video_and_audio
from utils.image_to_url_helper import upload_image
from utils.first_last_helper import upload_first_last_frames
from config import Config

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def test_api_connections():
    # Test OpenAI API
    try:
        generate_enhanced_prompt("Test prompt")
        logging.info("OpenAI API connection successful")
    except Exception as e:
        logging.error(f"OpenAI API connection failed: {str(e)}")

    # Test Lumma API
    try:
        headers = {"Authorization": f"Bearer {Config.LUMMA_API_KEY}"}
        response = requests.get("https://api.lumalabs.ai/dream-machine/v1/generations", headers=headers)
        response.raise_for_status()
        logging.info("Lumma API connection successful")
    except Exception as e:
        logging.error(f"Lumma API connection failed: {str(e)}")

    # Test ElevenLabs API
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        client.text_to_sound_effects.convert(text="Test", duration_seconds=1)
        logging.info("ElevenLabs API connection successful")
    except Exception as e:
        logging.error(f"ElevenLabs API connection failed: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_video', methods=['POST'])
def generate_video_route():
    try:
        input_type = request.form.get('input_type')
        prompt = request.form.get('prompt')
        sound_effect_enabled = request.form.get('sound_effect_enabled') == 'true'
        
        initial_image_url = None
        first_frame_url = None
        last_frame_url = None
        
        if input_type == 'image_text':
            if 'initial_image' not in request.files:
                return jsonify({"error": "No initial image provided"}), 400
            initial_image = request.files['initial_image']
            if initial_image and allowed_file(initial_image.filename):
                initial_image_filename = secure_filename(initial_image.filename)
                initial_image_path = os.path.join(app.config['UPLOAD_FOLDER'], initial_image_filename)
                initial_image.save(initial_image_path)
                initial_image_url = upload_image(Config.IMAGEDB_API_KEY, image_path=initial_image_path)
                logging.info(f"ImageDB returned URL: {initial_image_url}")
            else:
                return jsonify({"error": "Invalid initial image file"}), 400
        elif input_type == 'url':
            initial_image_url = request.form.get('url')
            if not initial_image_url:
                return jsonify({"error": "No URL provided"}), 400
        elif input_type == 'first_last_frame':
            if 'first_frame' not in request.files or 'last_frame' not in request.files:
                return jsonify({"error": "Both first and last frame images are required"}), 400
            first_frame = request.files['first_frame']
            last_frame = request.files['last_frame']
            if first_frame and last_frame and allowed_file(first_frame.filename) and allowed_file(last_frame.filename):
                first_frame_filename = secure_filename(first_frame.filename)
                last_frame_filename = secure_filename(last_frame.filename)
                first_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], first_frame_filename)
                last_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], last_frame_filename)
                first_frame.save(first_frame_path)
                last_frame.save(last_frame_path)
                first_frame_url, last_frame_url = upload_first_last_frames(first_frame_path, last_frame_path)
                logging.info(f"First frame URL: {first_frame_url}, Last frame URL: {last_frame_url}")
            else:
                return jsonify({"error": "Invalid first or last frame image file"}), 400
        
        # Generate enhanced prompt using OpenAI
        enhanced_prompt = generate_enhanced_prompt(prompt)
        logging.info("Step 1: Generated enhanced prompt using OpenAI")
        
        # Generate video using Lumma API
        logging.info("Step 2: Generating video")
        video_response = generate_video(enhanced_prompt, initial_image_url=initial_image_url, first_frame_url=first_frame_url, last_frame_url=last_frame_url)
        logging.info("Step 3: Video generation completed")
        
        if sound_effect_enabled:
            # Generate sound effect description using OpenAI
            logging.info("Step 4: Generating sound effect description using OpenAI")
            sound_effect_description = generate_sound_effect_description(enhanced_prompt.prompt)
            
            # Generate sound effect using ElevenLabs API
            logging.info("Step 5: Generating sound effect using ElevenLabs API")
            sound_effect_response = generate_sound_effect(sound_effect_description.description)
            
            if sound_effect_response.audio_url is None:
                logging.warning("Sound effect generation failed. Returning video without audio.")
                return jsonify({"combined_video_url": video_response.video_url, "separate_audio_url": None})
            
            # Combine video and audio
            logging.info("Step 6: Mixing video and sound effect")
            final_video = combine_video_and_audio(video_response, sound_effect_response)
            
            return jsonify({
                "combined_video_url": final_video.video_url,
                "separate_audio_url": final_video.audio_url
            })
        else:
            # If sound effect is disabled, return only the video URL
            return jsonify({
                "combined_video_url": video_response.video_url,
                "separate_audio_url": None
            })
    
    except Exception as e:
        logging.error(f"Error in generate_video_route: {str(e)}")
        error_message = "An unexpected error occurred during video generation."
        if "Prompt processing failed" in str(e):
            error_message = "The video prompt was too complex. Please try a simpler description."
        elif "API key" in str(e):
            error_message = "There was an issue with the API authentication. Please try again later."
        elif "Invalid cross-device link" in str(e):
            error_message = "An error occurred while processing the video. Please try again."
        elif "audio_url" in str(e):
            error_message = "An error occurred while generating or processing the audio. Please try again."
        return jsonify({"error": error_message}), 500

@app.route('/download_combined/<path:filename>', methods=['GET'])
def download_combined(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            # If the file doesn't exist locally, it might be a remote URL
            response = requests.get(filename, stream=True)
            response.raise_for_status()
            return response.content, 200, {
                'Content-Type': response.headers['Content-Type'],
                'Content-Disposition': f'attachment; filename={os.path.basename(filename)}'
            }
    except Exception as e:
        logging.error(f"Error in download_combined: {str(e)}")
        abort(404, description="File not found or unable to download.")

@app.route('/download_audio/<path:filename>', methods=['GET'])
def download_audio(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            # If the file doesn't exist locally, it might be a remote URL
            response = requests.get(filename, stream=True)
            response.raise_for_status()
            return response.content, 200, {
                'Content-Type': 'audio/mpeg',
                'Content-Disposition': f'attachment; filename={os.path.basename(filename)}'
            }
    except Exception as e:
        logging.error(f"Error in download_audio: {str(e)}")
        abort(404, description="File not found or unable to download.")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    test_api_connections()
    app.run(host='0.0.0.0', port=5000, debug=True)
