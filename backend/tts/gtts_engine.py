import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path

from gtts import gTTS

from tts.base import BaseTTS

logger = logging.getLogger(__name__)

MAX_CHUNK = 4500


class GTTSEngine(BaseTTS):
    """Free TTS engine using Google Translate's TTS service."""

    def generate(self, text: str, output_path: str, lang: str = "en") -> bool:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if len(text) <= MAX_CHUNK:
                tts = gTTS(text=text, lang=lang)
                tts.save(output_path)
            else:
                chunks = self._split(text, MAX_CHUNK)
                combined = BytesIO()
                for chunk in chunks:
                    tts = gTTS(text=chunk, lang=lang)
                    buf = BytesIO()
                    tts.write_to_fp(buf)
                    combined.write(buf.getvalue())

                Path(output_path).write_bytes(combined.getvalue())

            logger.info("Audio saved: %s", output_path)
            return True
        except Exception:
            logger.exception("gTTS generation failed for %s", output_path)
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
