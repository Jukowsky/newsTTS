from abc import ABC, abstractmethod


class BaseTTS(ABC):
    """Abstract base class for TTS engines."""

    audio_ext: str = ".mp3"

    @abstractmethod
    def generate(self, text: str, output_path: str, lang: str = "en") -> bool:
        """Generate an audio file from text. Returns True on success."""
        ...
