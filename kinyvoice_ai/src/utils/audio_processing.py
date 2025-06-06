import soundfile as sf
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def validate_audio_file(file) -> bool:
    """Validate audio file format and properties"""
    try:
        # Read audio file
        data, sample_rate = sf.read(file)
        
        # Check if audio is not empty
        if len(data) == 0:
            logger.error("Empty audio file")
            return False
        
        # Check if audio is not too long (e.g., max 10 minutes)
        max_duration = 10 * 60  # 10 minutes in seconds
        if len(data) / sample_rate > max_duration:
            logger.error("Audio file too long")
            return False
        
        # Check if audio is not too short (e.g., min 0.1 seconds)
        min_duration = 0.1  # 0.1 seconds
        if len(data) / sample_rate < min_duration:
            logger.error("Audio file too short")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating audio file: {e}")
        return False

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to have zero mean and unit variance"""
    return (audio - np.mean(audio)) / (np.std(audio) + 1e-8)

def trim_silence(audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    """Trim silence from the beginning and end of audio"""
    # Find non-silent regions
    mask = np.abs(audio) > threshold
    start = np.argmax(mask)
    end = len(audio) - np.argmax(mask[::-1])
    return audio[start:end]

def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to target sample rate"""
    if orig_sr == target_sr:
        return audio
    
    # Calculate number of samples in resampled audio
    n_samples = int(len(audio) * target_sr / orig_sr)
    
    # Resample using linear interpolation
    resampled = np.interp(
        np.linspace(0, len(audio), n_samples),
        np.arange(len(audio)),
        audio
    )
    
    return resampled 