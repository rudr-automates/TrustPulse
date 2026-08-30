from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.analysis import router as analysis_router
from backend.app.api.routes.evidence import router as evidence_router
from backend.app.api.routes.profile import router as profile_router
from backend.app.api.routes.triangulation import (
    router as triangulation_router,
)
from backend.app.api.routes.signals import (
    router as signals_router,
)


app = FastAPI(
    title="TrustPulse API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "trustpulse-api",
    }


app.include_router(
    profile_router,
    prefix="/api/v1",
)

app.include_router(
    evidence_router,
    prefix="/api/v1",
)

app.include_router(
    analysis_router,
    prefix="/api/v1",
)

app.include_router(
    triangulation_router,
    prefix="/api/v1",
)
app.include_router(
    signals_router,
    prefix="/api/v1",
)