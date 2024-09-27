from pydantic import BaseModel
from typing import List, Optional

class VideoGenerationRequest(BaseModel):
    prompt: str

class EnhancedPrompt(BaseModel):
    prompt: str
    aspect_ratio: str
    duration: int

class VideoGenerationResponse(BaseModel):
    video_url: str
    audio_url: Optional[str] = None

    def to_dict(self):
        return {"video_url": self.video_url, "audio_url": self.audio_url}

class SoundEffectRequest(BaseModel):
    description: str

class SoundEffectResponse(BaseModel):
    audio_url: str

class FinalVideoResponse(BaseModel):
    video_url: str

    def to_dict(self):
        return {"video_url": self.video_url}
