from fastapi import APIRouter, HTTPException
from kinyvoice_ai.configs.connect_timescale_db import get_db_connection, release_db_connection
from kinyvoice_ai.src.model.asr_model import ASRModel

router = APIRouter()
asr_model = ASRModel()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy"}

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including database and model status"""
    health_status = {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "model": "healthy"
        }
    }
    
    # Check database connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    finally:
        release_db_connection(conn)
    
    # Check model status
    if not asr_model.is_loaded():
        health_status["components"]["model"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status 