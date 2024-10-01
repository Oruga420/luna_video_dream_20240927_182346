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
                {"role": "system", "content": "Generate a simple, concise video prompt (max 100 words) that's easy for video generation APIs to process. Include 'prompt', 'aspect_ratio', and 'duration' in your JSON response."},
                {"role": "user", "content": f"Create a video prompt based on: {prompt}"}
            ]
        )
        content = response.choices[0].message.content
        logging.info(f"Raw OpenAI response: {content}")

        # Remove markdown formatting if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        logging.info(f"Content after removing markdown: {content}")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            logging.error(f"Content after removing markdown: {content}")
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")

        enhanced_prompt = data.get('prompt', prompt)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        duration = data.get('duration', 10)

        if isinstance(duration, str):
            try:
                duration = int(duration.split()[0])
            except (ValueError, IndexError):
                logging.warning(f"Failed to parse duration: {duration}. Using default value.")
                duration = 10

        # Limit prompt to 100 words
        enhanced_prompt = ' '.join(enhanced_prompt.split()[:100])

        return EnhancedPrompt(prompt=enhanced_prompt, aspect_ratio=aspect_ratio, duration=duration)

    except Exception as e:
        logging.error(f"Unexpected error in generate_enhanced_prompt: {e}")
        return EnhancedPrompt(prompt=prompt, aspect_ratio="16:9", duration=10)

def generate_sound_effect_description(prompt: str) -> SoundEffectRequest:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a brief sound effect description for a short video scene (5 seconds or less). Keep it concise and specific."},
            {"role": "user", "content": f"Create a sound effect description for: {prompt}"}
        ]
    )
    description = response.choices[0].message.content
    if description is None:
        description = "Default sound effect"
    return SoundEffectRequest(description=description)
