from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import PORTALS, settings
from database import get_db
from models import Article, AudioFile, AppSettings

router = APIRouter()


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def require_admin(x_admin_password: str = Header(...)):
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@router.get("/portals")
def list_portals():
    return PORTALS


@router.get("/portals/{portal_id}/articles")
def get_articles(portal_id: str, db: Session = Depends(get_db)):
    valid_ids = {p["id"] for p in PORTALS}
    if portal_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Portal not found")

    since = datetime.utcnow() - timedelta(hours=settings.audio_retention_hours)
    articles = (
        db.query(Article)
        .filter(Article.portal == portal_id, Article.scraped_at >= since)
        .order_by(Article.scraped_at.desc(), Article.id.desc())
        .all()
    )

    results = []
    for a in articles:
        audio = db.query(AudioFile).filter(AudioFile.article_id == a.id).first()
        results.append({
            "id": a.id,
            "title": a.title,
            "author": a.author,
            "date": a.date,
            "url": a.url,
            "word_count": a.word_count,
            "scraped_at": a.scraped_at.isoformat(),
            "audio_url": f"/api/audio/{audio.id}" if audio else None,
        })

    return results


@router.get("/audio/{audio_id}")
def stream_audio(audio_id: int, db: Session = Depends(get_db)):
    audio = db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")

    from pathlib import Path

    path = Path(audio.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file missing from disk")

    mime = "audio/wav" if path.suffix == ".wav" else "audio/mpeg"
    return FileResponse(path, media_type=mime, filename=path.name)


# ---------------------------------------------------------------------------
# Admin endpoints (password-protected)
# ---------------------------------------------------------------------------

def _get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(AppSettings).filter(AppSettings.key == key).first()
    return row.value if row else default


def _set_setting(db: Session, key: str, value: str):
    row = db.query(AppSettings).filter(AppSettings.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSettings(key=key, value=value))


def _portal_settings(db: Session, portal_id: str) -> dict:
    return {
        "tts_engine": _get_setting(db, f"tts_engine.{portal_id}", "gtts"),
        "elevenlabs_api_key": _get_setting(db, f"elevenlabs_api_key.{portal_id}"),
        "elevenlabs_voice_id": _get_setting(db, f"elevenlabs_voice_id.{portal_id}"),
        "gemini_api_key": _get_setting(db, f"gemini_api_key.{portal_id}"),
        "gemini_voice_name": _get_setting(db, f"gemini_voice_name.{portal_id}"),
    }


@router.post("/admin/login")
def admin_login(_: None = Depends(require_admin)):
    return {"ok": True}


@router.get("/admin/settings")
def get_admin_settings(
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = {}
    for p in PORTALS:
        result[p["id"]] = _portal_settings(db, p["id"])
    return result


class PortalSettingsUpdate(BaseModel):
    tts_engine: str | None = None
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str | None = None
    gemini_api_key: str | None = None
    gemini_voice_name: str | None = None


@router.put("/admin/settings/{portal_id}")
def update_portal_settings(
    portal_id: str,
    body: PortalSettingsUpdate,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    valid_ids = {p["id"] for p in PORTALS}
    if portal_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Portal not found")

    for field, value in body.model_dump(exclude_none=True).items():
        if field == "tts_engine" and value not in ("gtts", "elevenlabs", "gemini"):
            raise HTTPException(status_code=400, detail="tts_engine must be 'gtts', 'elevenlabs', or 'gemini'")
        _set_setting(db, f"{field}.{portal_id}", value)
    db.commit()

    result = {}
    for p in PORTALS:
        result[p["id"]] = _portal_settings(db, p["id"])
    return result


@router.post("/admin/scrape/{portal_id}")
def trigger_scrape(
    portal_id: str,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
):
    valid_ids = {p["id"] for p in PORTALS}
    if portal_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Portal not found")

    from pathlib import Path as _P
    existing = db.query(Article).filter(Article.portal == portal_id).all()
    for a in existing:
        for af in a.audio_files:
            p = _P(af.file_path)
            if p.exists():
                p.unlink()
        db.delete(a)
    db.commit()

    from scheduler import run_scrape_and_tts
    count, error = run_scrape_and_tts(portal_id)
    return {"portal": portal_id, "articles_processed": count, "error": error}
