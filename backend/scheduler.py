import logging
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from config import PORTALS, settings


def _audio_filename(author: str, dt: datetime, ext: str = ".mp3") -> str:
    """Return audio filename in format MMDDYYYY_authorslug{ext}"""
    date_str = dt.strftime("%m%d%Y")
    nfkd = unicodedata.normalize("NFKD", author)
    slug = re.sub(r"[^a-z0-9]", "", nfkd.encode("ascii", "ignore").decode("ascii").lower())
    return f"{date_str}_{slug or 'unknown'}{ext}"

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def _get_tts_engine(portal_id: str):
    """Read per-portal TTS engine preference from DB and return the appropriate instance."""
    from database import SessionLocal
    from models import AppSettings

    db = SessionLocal()
    try:
        def _val(key: str) -> str:
            row = db.query(AppSettings).filter(AppSettings.key == key).first()
            return row.value if row else ""

        engine_name = _val(f"tts_engine.{portal_id}") or "gtts"

        if engine_name == "elevenlabs":
            api_key = _val(f"elevenlabs_api_key.{portal_id}")
            voice_id = _val(f"elevenlabs_voice_id.{portal_id}")

            if api_key:
                from tts.elevenlabs_engine import ElevenLabsEngine
                logger.info("Using ElevenLabs TTS for %s", portal_id)
                return ElevenLabsEngine(api_key=api_key, voice_id=voice_id or None)
            else:
                logger.warning("ElevenLabs selected for %s but no API key, falling back to gTTS", portal_id)

        if engine_name == "gemini":
            api_key = _val(f"gemini_api_key.{portal_id}")
            voice_name = _val(f"gemini_voice_name.{portal_id}")
            if api_key:
                from tts.gemini_engine import GeminiEngine
                logger.info("Using Gemini TTS for %s", portal_id)
                return GeminiEngine(api_key=api_key, voice_name=voice_name or None)
            else:
                logger.warning("Gemini selected for %s but no API key, falling back to gTTS", portal_id)

        from tts.gtts_engine import GTTSEngine
        return GTTSEngine()
    finally:
        db.close()


def run_scrape_and_tts(portal_id: str) -> tuple[int, str | None]:
    """Scrape articles for a portal and generate TTS audio. Returns (count, error)."""
    from database import SessionLocal
    from models import Article, AudioFile

    portal_cfg = next((p for p in PORTALS if p["id"] == portal_id), None)
    if not portal_cfg:
        return 0, None

    if portal_id == "sol":
        from scrapers.sol import SolScraper
        scraper = SolScraper()
    else:
        from scrapers.riktpunkt import RiktpunktScraper
        scraper = RiktpunktScraper()

    logger.info("Scraping started for portal: %s", portal_id)
    articles_data = scraper.scrape()
    if not articles_data:
        logger.info("No articles found for %s", portal_id)
        return 0, None
    logger.info("Fetched %d raw articles for %s", len(articles_data), portal_id)

    tts = _get_tts_engine(portal_id)

    db = SessionLocal()
    count = 0
    tts_error: str | None = None
    try:
        for data in articles_data:
            existing = db.query(Article).filter(Article.url == data["url"]).first()
            if existing:
                logger.info("Skipping already-processed article: %s", data["url"])
                continue

            article = Article(
                portal=portal_id,
                title=data["title"],
                author=data.get("author", ""),
                date=data.get("date", ""),
                url=data["url"],
                content=data["content"],
                word_count=data.get("word_count", len(data["content"].split())),
            )
            db.add(article)
            db.flush()

            now = datetime.utcnow()
            today = now.strftime("%Y-%m-%d")
            audio_dir = settings.audio_dir / portal_id / today
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_path = audio_dir / _audio_filename(data.get("author", ""), now, tts.audio_ext)

            # If the audio file already exists on disk, reuse it and skip TTS
            if audio_path.exists():
                logger.info("Reusing existing audio %s", audio_path.name)
                db.add(AudioFile(article_id=article.id, file_path=str(audio_path)))
                article.audio_generated = True
                count += 1
                continue

            lang = portal_cfg["language"]
            try:
                success = tts.generate(data["content"], str(audio_path), lang=lang)
            except Exception as exc:
                tts_error = str(exc)
                logger.warning("TTS stopped for %s after %d articles: %s", portal_id, count, tts_error)
                db.commit()
                return count, tts_error

            if success:
                logger.info("TTS generated: %s -> %s", data["title"][:60], audio_path.name)
                db.add(AudioFile(article_id=article.id, file_path=str(audio_path)))
                article.audio_generated = True
                count += 1
            else:
                logger.warning("TTS failed (returned False) for article: %s", data["title"][:60])

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error during scrape+TTS for %s", portal_id)
    finally:
        db.close()

    logger.info("Processed %d articles for %s", count, portal_id)
    return count, tts_error


def _daily_scrape():
    for portal in PORTALS:
        try:
            run_scrape_and_tts(portal["id"])
        except Exception:
            logger.exception("Scheduled scrape failed for %s", portal["id"])


def _daily_cleanup():
    from database import SessionLocal
    from models import AudioFile, Article

    cutoff = datetime.utcnow() - timedelta(hours=settings.audio_retention_hours)
    db = SessionLocal()
    try:
        expired = db.query(AudioFile).filter(AudioFile.expires_at < cutoff).all()
        for af in expired:
            path = Path(af.file_path)
            if path.exists():
                path.unlink()
            db.delete(af)

        old_articles = (
            db.query(Article)
            .filter(Article.scraped_at < cutoff)
            .all()
        )
        for a in old_articles:
            db.delete(a)

        db.commit()
        logger.info("Cleanup: removed %d audio files, %d articles", len(expired), len(old_articles))
    except Exception:
        db.rollback()
        logger.exception("Cleanup failed")
    finally:
        db.close()


def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _daily_scrape, "cron",
        hour=settings.scrape_hour, minute=settings.scrape_minute,
        id="daily_scrape",
    )
    _scheduler.add_job(
        _daily_cleanup, "cron",
        hour=settings.cleanup_hour, minute=settings.cleanup_minute,
        id="daily_cleanup",
    )
    _scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        logger.info("Scheduler shut down")
