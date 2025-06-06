from jiwer import wer as jiwer_wer, cer as jiwer_cer
from typing import Optional

def calculate_wer(reference: Optional[str], hypothesis: str) -> Optional[float]:
    """Calculate Word Error Rate (WER) between reference and hypothesis."""
    if reference is None:
        return None
    return jiwer_wer(reference, hypothesis)

def calculate_cer(reference: Optional[str], hypothesis: str) -> Optional[float]:
    """Calculate Character Error Rate (CER) between reference and hypothesis."""
    if reference is None:
        return None
    return jiwer_cer(reference, hypothesis) 