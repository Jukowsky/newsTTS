import logging
import os
import wave
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types

from tts.base import BaseTTS

logger = logging.getLogger(__name__)

MAX_CHUNK = 4500
DEFAULT_VOICE = "Kore"


class GeminiEngine(BaseTTS):
    """Google Gemini TTS engine. Audio is saved as WAV (no ffmpeg required)."""

    MODEL = "gemini-2.5-flash-preview-tts"
    audio_ext = ".wav"

    def __init__(self, api_key: str, voice_name: str | None = None):
        self.client = genai.Client(api_key=api_key)
        self.voice_name = voice_name or DEFAULT_VOICE

    def _synthesize_chunk(self, text: str) -> bytes:
        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice_name
                        )
                    )
                ),
            ),
        )
        return response.candidates[0].content.parts[0].inline_data.data

    def generate(self, text: str, output_path: str, lang: str = "en") -> bool:
        wav_path = str(Path(output_path).with_suffix(".wav"))
        try:
            os.makedirs(os.path.dirname(wav_path), exist_ok=True)

            if len(text) <= MAX_CHUNK:
                pcm = self._synthesize_chunk(text)
            else:
                chunks = self._split(text, MAX_CHUNK)
                buf = BytesIO()
                for chunk in chunks:
                    buf.write(self._synthesize_chunk(chunk))
                pcm = buf.getvalue()

            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)   # 16-bit PCM
                wf.setframerate(24000)
                wf.writeframes(pcm)

            logger.info("Gemini audio saved: %s", wav_path)
            return True
        except Exception:
            logger.exception("Gemini TTS failed for %s", wav_path)
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
