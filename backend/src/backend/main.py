from fastapi import FastAPI

from backend.api.v1 import v1_router

app = FastAPI(
    title="MarketHub",
    version="0.1.0"
)

app.include_router(
    v1_router
)