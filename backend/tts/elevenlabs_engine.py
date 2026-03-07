import logging
import os
from io import BytesIO
from pathlib import Path

import requests

from tts.base import BaseTTS

logger = logging.getLogger(__name__)

MAX_CHUNK = 4500


class ElevenLabsEngine(BaseTTS):
    """ElevenLabs TTS engine (requires API key)."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str, voice_id: str | None = None):
        self.api_key = api_key
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

    def _synthesize_chunk(self, text: str) -> bytes:
        url = f"{self.BASE_URL}/text-to-speech/{self.voice_id}"
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        resp = requests.post(url, json=data, headers=self.headers, timeout=120)
        resp.raise_for_status()
        return resp.content

    def generate(self, text: str, output_path: str, lang: str = "en") -> bool:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if len(text) <= MAX_CHUNK:
                audio = self._synthesize_chunk(text)
            else:
                chunks = self._split(text, MAX_CHUNK)
                combined = BytesIO()
                for chunk in chunks:
                    combined.write(self._synthesize_chunk(chunk))
                audio = combined.getvalue()

            Path(output_path).write_bytes(audio)
            logger.info("ElevenLabs audio saved: %s", output_path)
            return True
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 402:
                raise  # propagate so the caller can stop processing
            logger.exception("ElevenLabs generation failed for %s", output_path)
            return False
        except Exception:
            logger.exception("ElevenLabs generation failed for %s", output_path)
            return False

    @staticmethod
    def _split(text: str, max_len: int) -> list[str]:
        sentences = []
        for part in text.replace("\n", " ").split(". "):
            part = part.strip()
            if part:
                sentences.append(part + ".")

        chunks: list[str] = []
        current = ""
        for s in sentences:
            if len(current) + len(s) + 1 > max_len and current:
                chunks.append(current.strip())
                current = s
            else:
                current = f"{current} {s}" if current else s
        if current.strip():
            chunks.append(current.strip())
        return chunks
