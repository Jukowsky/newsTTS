import logging
import logging.handlers
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from scheduler import start_scheduler, shutdown_scheduler

_LOG_DIR = Path(__file__).resolve().parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.TimedRotatingFileHandler(
            _LOG_DIR / "app.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        ),
    ],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Redcast API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import router  # noqa: E402
app.include_router(router, prefix="/api")

# Serve built frontend in production (no-op if dist doesn't exist)
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Serve static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    # SPA catch-all: serve index.html for any unmatched route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file = _FRONTEND_DIST / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(_FRONTEND_DIST / "index.html")
