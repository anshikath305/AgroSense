import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .advisory.router import router as advisory_router
from .crop.router import router as crop_router
from .disease.router import analyze as analyze_disease
from .disease.router import router as disease_router
from .fertilizer.router import router as fertilizer_router

app = FastAPI(
    title="AgroSense AI Backend",
    version="1.0.0",
    description="Model-serving API for crop recommendation, disease detection, fertilizer prediction, and AI advisory.",
)

# Build allowed origins: always include localhost, plus any Render/custom origins
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
_extra = os.environ.get("ALLOWED_ORIGINS", "")
_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crop_router, prefix="/crop", tags=["Crop Recommendation"])
app.include_router(disease_router, prefix="/disease", tags=["Disease Detection"])
app.include_router(fertilizer_router, prefix="/fertilizer", tags=["Fertilizer Prediction"])
app.include_router(advisory_router, prefix="/advisory", tags=["AI Advisory"])


@app.post("/analyze", tags=["Disease Detection"])
async def analyze(request: Request) -> dict:
    return await analyze_disease(request)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "AgroSense backend running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "AgroSense AI Backend"}
