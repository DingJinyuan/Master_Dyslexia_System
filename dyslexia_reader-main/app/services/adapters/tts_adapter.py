from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import json

import httpx

from app.core.config import settings


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, speed: float, voice: str, return_word_marks: bool = True) -> dict:
        raise NotImplementedError


class MockTTSProvider(TTSProvider):
    def synthesize(self, text: str, speed: float, voice: str, return_word_marks: bool = True) -> dict:
        words = text.split()
        marks = []
        current_ms = 0
        duration_per_word = max(120, int(280 / speed))
        for idx, word in enumerate(words):
            marks.append({
                "index": idx,
                "word": word,
                "start_ms": current_ms,
                "end_ms": current_ms + duration_per_word,
            })
            current_ms += duration_per_word
        audio_path = f"mock_audio/{voice}_{str(speed).replace('.', '_')}.mp3"
        return {"audio_url": audio_path, "marks": marks}


class HTTPTTSProvider(TTSProvider):
    def synthesize(self, text: str, speed: float, voice: str, return_word_marks: bool = True) -> dict:
        payload = {
            "text": text,
            "speed": speed,
            "voice": voice,
            "return_word_marks": return_word_marks,
        }
        with httpx.Client(timeout=120) as client:
            response = client.post(
                settings.tts_api_url,
                headers={"Authorization": f"Bearer {settings.tts_api_key}", "Content-Type": "application/json"},
                content=json.dumps(payload),
            )
            response.raise_for_status()
            return response.json()



def get_tts_provider() -> TTSProvider:
    if settings.tts_provider == "http":
        return HTTPTTSProvider()
    return MockTTSProvider()
