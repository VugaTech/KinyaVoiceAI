from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from kinyvoice_ai.src.model.asr_model import ASRModel
from kinyvoice_ai.src.utils.audio_processing import validate_audio_file
from kinyvoice_ai.src.utils.metrics import calculate_wer, calculate_cer
from kinyvoice_ai.src.database.models import TranscriptionRecord
from kinyvoice_ai.configs.connect_timescale_db import get_db_connection, release_db_connection

router = APIRouter()
asr_model = ASRModel()

class TranscriptionResponse(BaseModel):
    """Response model for a single transcription."""
    transcription_id: str
    text: str
    confidence: float
    processing_time: float
    wer: Optional[float] = None
    cer: Optional[float] = None
    created_at: datetime

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    reference_text: Optional[str] = None
):
    """Transcribe a single audio file and return text, confidence, and metrics."""
    # Validate audio file
    if not validate_audio_file(file):
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    # Process audio
    start_time = datetime.now()
    text, confidence = await asr_model.transcribe(file)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Calculate metrics if reference text is provided
    wer = calculate_wer(reference_text, text) if reference_text else None
    cer = calculate_cer(reference_text, text) if reference_text else None
    
    # Store in database
    transcription_id = str(uuid.uuid4())
    record = TranscriptionRecord(
        id=transcription_id,
        text=text,
        confidence=confidence,
        processing_time=processing_time,
        wer=wer,
        cer=cer,
        created_at=datetime.now()
    )
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transcriptions (id, text, confidence, processing_time, wer, cer, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                record.id, record.text, record.confidence, record.processing_time,
                record.wer, record.cer, record.created_at
            ))
    finally:
        release_db_connection(conn)
    
    return TranscriptionResponse(
        transcription_id=record.id,
        text=record.text,
        confidence=record.confidence,
        processing_time=record.processing_time,
        wer=record.wer,
        cer=record.cer,
        created_at=record.created_at
    )

@router.post("/batch-transcribe")
async def batch_transcribe(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Transcribe multiple audio files in batch asynchronously."""
    job_id = str(uuid.uuid4())
    
    # Start background task for processing
    background_tasks.add_task(
        process_batch_transcription,
        job_id=job_id,
        files=files
    )
    
    return {"job_id": job_id, "status": "processing"}

@router.get("/transcription/{transcription_id}")
async def get_transcription(transcription_id: str):
    """Get transcription result by ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM transcriptions WHERE id = %s
            """, (transcription_id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Transcription not found")
            
            return result
    finally:
        release_db_connection(conn)

async def process_batch_transcription(job_id: str, files: List[UploadFile]):
    """Process batch transcription in background and store results in DB."""
    conn = get_db_connection()
    try:
        for file in files:
            if validate_audio_file(file):
                start_time = datetime.now()
                text, confidence = await asr_model.transcribe(file)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO transcriptions (id, text, confidence, processing_time, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        text,
                        confidence,
                        processing_time,
                        datetime.now()
                    ))
    finally:
        release_db_connection(conn) 