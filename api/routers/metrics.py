from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
from kinyvoice_ai.configs.connect_timescale_db import get_db_connection, release_db_connection

router = APIRouter()

@router.get("/summary")
async def get_metrics_summary(
    start_time: Optional[datetime] = Query(None, description="Start time for metrics"),
    end_time: Optional[datetime] = Query(None, description="End time for metrics")
):
    """Get summary metrics for the specified time period"""
    if not start_time:
        start_time = datetime.now() - timedelta(days=7)
    if not end_time:
        end_time = datetime.now()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get average WER and CER
            cur.execute("""
                SELECT 
                    AVG(wer) as avg_wer,
                    AVG(cer) as avg_cer,
                    AVG(processing_time) as avg_processing_time,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) as total_transcriptions
                FROM transcriptions
                WHERE created_at BETWEEN %s AND %s
            """, (start_time, end_time))
            metrics = cur.fetchone()
            
            # Get hourly distribution
            cur.execute("""
                SELECT 
                    date_trunc('hour', created_at) as hour,
                    COUNT(*) as count
                FROM transcriptions
                WHERE created_at BETWEEN %s AND %s
                GROUP BY hour
                ORDER BY hour
            """, (start_time, end_time))
            hourly_distribution = cur.fetchall()
            
            return {
                "summary": metrics,
                "hourly_distribution": hourly_distribution
            }
    finally:
        release_db_connection(conn)

@router.get("/transcription/{transcription_id}/metrics")
async def get_transcription_metrics(transcription_id: str):
    """Get detailed metrics for a specific transcription"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    wer,
                    cer,
                    processing_time,
                    confidence,
                    created_at
                FROM transcriptions
                WHERE id = %s
            """, (transcription_id,))
            metrics = cur.fetchone()
            
            if not metrics:
                return {"error": "Transcription not found"}
            
            return metrics
    finally:
        release_db_connection(conn)

@router.get("/performance")
async def get_performance_metrics(
    start_time: Optional[datetime] = Query(None, description="Start time for metrics"),
    end_time: Optional[datetime] = Query(None, description="End time for metrics")
):
    """Get detailed performance metrics"""
    if not start_time:
        start_time = datetime.now() - timedelta(days=7)
    if not end_time:
        end_time = datetime.now()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get performance metrics
            cur.execute("""
                SELECT 
                    date_trunc('hour', created_at) as hour,
                    AVG(processing_time) as avg_processing_time,
                    MIN(processing_time) as min_processing_time,
                    MAX(processing_time) as max_processing_time,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) as request_count
                FROM transcriptions
                WHERE created_at BETWEEN %s AND %s
                GROUP BY hour
                ORDER BY hour
            """, (start_time, end_time))
            performance_metrics = cur.fetchall()
            
            return {
                "performance_metrics": performance_metrics
            }
    finally:
        release_db_connection(conn) 