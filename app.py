import logging
from flask import Flask, render_template, request, jsonify
from models.pydantic_models import VideoGenerationRequest, FinalVideoResponse
from utils.openai_helper import generate_enhanced_prompt, generate_sound_effect_description
from utils.lumma_helper import generate_video
from utils.elevenlabs_helper import generate_sound_effect
from utils.video_processor import combine_video_and_audio

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_video', methods=['POST'])
def generate_video_route():
    try:
        data = request.json
        video_request = VideoGenerationRequest(**data)
        
        # Generate enhanced prompt using OpenAI
        enhanced_prompt = generate_enhanced_prompt(video_request.prompt)
        logging.info("Step 1: Generated enhanced prompt using OpenAI")
        
        # Generate video using Lumma API
        logging.info("Step 2: Generating video using Lumma API")
        video_response = generate_video(enhanced_prompt)
        logging.info("Step 3: Video generation completed")
        
        # Generate sound effect description using OpenAI
        logging.info("Step 4: Generating sound effect description using OpenAI")
        sound_effect_description = generate_sound_effect_description(enhanced_prompt.prompt)
        
        # Generate sound effect using ElevenLabs API
        logging.info("Step 5: Generating sound effect using ElevenLabs API")
        sound_effect_response = generate_sound_effect(sound_effect_description)
        
        if sound_effect_response.audio_url is None:
            logging.warning("Sound effect generation failed. Returning video without audio.")
            return jsonify({"video_url": video_response.video_url})
        
        # Combine video and audio
        logging.info("Step 6: Mixing video and sound effect")
        final_video = combine_video_and_audio(video_response, sound_effect_response)
        
        return jsonify({"video_url": final_video.video_url})
    
    except Exception as e:
        logging.error(f"Error in generate_video_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
