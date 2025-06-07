from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kinyvoice_ai.configs.settings import Settings
from kinyvoice_ai.configs.connect_timescale_db import init_db_pool, close_db_pool
from kinyvoice_ai.api.routers import asr, health, metrics
from kinyvoice_ai.src.model.asr_model import ASRModel
from kinyvoice_ai.src.database.models import create_tables

app = FastAPI(
    title="KinyaVoice AI API",
    description="Kinyarwanda Automatic Speech Recognition API. Provides endpoints for real-time and batch transcription, metrics, and health checks.",
    version="1.0.0"
)

settings = Settings()

# Initialize ASR model (singleton)
asr_model = ASRModel()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(asr.router, prefix="/api/v1/asr", tags=["ASR"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])

@app.on_event("startup")
async def startup_event():
    """Initialize DB pool, create tables, and load ASR model on startup."""
    init_db_pool()
    create_tables()
    await asr_model.load_model()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup DB pool and unload ASR model on shutdown."""
    close_db_pool()
    await asr_model.unload_model()

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint for API status."""
    return {
        "message": "KinyaVoice AI API is running",
        "version": settings.version,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)