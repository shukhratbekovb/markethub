from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.v1 import v1_router
from backend.core.configs import settings

Path(settings.upload_root).mkdir(exist_ok=True)

app = FastAPI(
    title="MarketHub",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory=settings.upload_root), name="static")

app.include_router(
    v1_router
)