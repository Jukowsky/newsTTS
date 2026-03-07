# NewsTTS - Daily Audio News

A full-stack application that scrapes daily column articles from **Sol Haber** (Turkish) and **RiktpunKt** (Swedish), converts them to audio using TTS, and serves them through a mobile-friendly Progressive Web App.

## Architecture

- **Backend**: Python / FastAPI with SQLite, APScheduler, gTTS
- **Frontend**: React + TypeScript PWA (Vite, TailwindCSS)

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Key endpoints:

| Endpoint | Description |
|---|---|
| `GET  /api/portals` | List available news portals |
| `GET  /api/portals/{id}/articles` | Today's articles for a portal |
| `GET  /api/audio/{id}` | Stream an audio file |
| `POST /api/scrape/{id}` | Manually trigger scrape + TTS |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend.

### Production

```bash
cd frontend && npm run build
```

Serve the `frontend/dist/` folder with any static file server, or configure the FastAPI app to serve it.

## Features

- Scrapes column articles from Sol Haber and RiktpunKt daily
- Generates MP3 audio using gTTS (free, no API key needed)
- Stores audio for 24 hours, then auto-cleans
- Mobile-first PWA with portal selection and audio player
- Play All mode for sequential playback
- Scheduled daily scraping (06:00) and cleanup (02:00)

## Configuration

Create a `.env` file in the `backend/` directory:

```
SCRAPE_HOUR=6
CLEANUP_HOUR=2
AUDIO_RETENTION_HOURS=24
MAX_ARTICLES_PER_PORTAL=10
```

## Project Structure

```
newsTTS/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # DB models
│   ├── routes.py            # API endpoints
│   ├── scheduler.py         # Daily jobs
│   ├── scrapers/
│   │   ├── base.py          # BaseScraper ABC
│   │   ├── sol.py           # Sol Haber scraper
│   │   └── riktpunkt.py     # RiktpunKt scraper
│   ├── tts/
│   │   ├── base.py          # BaseTTS ABC
│   │   ├── gtts_engine.py   # gTTS (default)
│   │   └── elevenlabs_engine.py  # ElevenLabs (future)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── PortalSelect.tsx
│   │   │   └── ArticleList.tsx
│   │   └── components/
│   │       ├── AudioPlayer.tsx
│   │       └── ArticleCard.tsx
│   └── package.json
└── README.md
```

## Next Steps

- Enable ElevenLabs TTS from admin settings
- Add more news portals
- Offline playback via PWA cache
