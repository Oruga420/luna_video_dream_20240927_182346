import json
import logging
from openai import OpenAI
from config import Config
from models.pydantic_models import EnhancedPrompt, SoundEffectRequest

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_enhanced_prompt(prompt: str) -> EnhancedPrompt:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps generate enhanced prompts for video creation. Provide a JSON response with 'prompt', 'aspect_ratio', and 'duration' keys."},
                {"role": "user", "content": f"Generate an enhanced prompt for video creation based on: {prompt}"}
            ]
        )
        content = response.choices[0].message.content
        logging.info(f"Raw OpenAI response: {content}")

        # Remove markdown formatting if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove the ```json prefix
        if content.endswith("```"):
            content = content[:-3]  # Remove the ``` suffix
        content = content.strip()  # Remove any remaining whitespace

        logging.info(f"Content after removing markdown: {content}")

        # Attempt to parse the JSON response
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            logging.error(f"Content after removing markdown: {content}")
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")

        # Extract and validate the required fields
        enhanced_prompt = data.get('prompt', prompt)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        duration = data.get('duration', 10)

        # Convert duration to int if it's a string
        if isinstance(duration, str):
            try:
                duration = int(duration.split()[0])
            except (ValueError, IndexError):
                logging.warning(f"Failed to parse duration: {duration}. Using default value.")
                duration = 10

        return EnhancedPrompt(prompt=enhanced_prompt, aspect_ratio=aspect_ratio, duration=duration)

    except Exception as e:
        logging.error(f"Unexpected error in generate_enhanced_prompt: {e}")
        return EnhancedPrompt(prompt=prompt, aspect_ratio="16:9", duration=10)

def generate_sound_effect_description(prompt: str) -> SoundEffectRequest:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates sound effect descriptions for short video scenes (5 seconds or less). Provide detailed and concise descriptions."},
            {"role": "user", "content": f"Generate a sound effect description for a short video scene (5 seconds or less) with the prompt: {prompt}. For example, for a scene of a strawberry falling from a plant, the sound effect should be 'Soft rustling of leaves, followed by a gentle thud as the strawberry hits the ground'."}
        ]
    )
    description = response.choices[0].message.content
    if description is None:
        description = "Default sound effect"
    return SoundEffectRequest(description=description)
