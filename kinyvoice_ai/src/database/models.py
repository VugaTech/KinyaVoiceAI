from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TranscriptionRecord(BaseModel):
    """Model for storing transcription records"""
    id: str
    text: str
    confidence: float
    processing_time: float
    wer: Optional[float] = None
    cer: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True

def create_tables():
    """Create necessary database tables if they don't exist"""
    from kinyvoice_ai.configs.connect_timescale_db import get_db_connection, release_db_connection
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Create transcriptions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id UUID PRIMARY KEY,
                    text TEXT NOT NULL,
                    confidence FLOAT NOT NULL,
                    processing_time FLOAT NOT NULL,
                    wer FLOAT,
                    cer FLOAT,
                    created_at TIMESTAMPTZ NOT NULL
                );
                
                -- Create TimescaleDB hypertable
                SELECT create_hypertable('transcriptions', 'created_at', if_not_exists => TRUE);
                
                -- Create indexes
                CREATE INDEX IF NOT EXISTS idx_transcriptions_created_at 
                ON transcriptions (created_at DESC);
                
                CREATE INDEX IF NOT EXISTS idx_transcriptions_confidence 
                ON transcriptions (confidence DESC);
            """)
    finally:
        release_db_connection(conn) 