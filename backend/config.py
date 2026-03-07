from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./newstts.db"
    audio_dir: Path = Path(__file__).resolve().parent / "audio_files"
    scrape_hour: int = 3
    scrape_minute: int = 0
    cleanup_hour: int = 2
    cleanup_minute: int = 0
    audio_retention_hours: int = 24
    max_articles_per_portal: int = 10
    admin_password: str = "H06eL0#?bnvw"
    elevenlabs_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
settings.audio_dir.mkdir(parents=True, exist_ok=True)

PORTALS = [
    {"id": "sol", "name": "Sol Haber", "language": "tr"},
    {"id": "riktpunkt", "name": "RiktpunKt", "language": "sv"},
]
