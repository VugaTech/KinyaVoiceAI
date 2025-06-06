import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ASRModel:
    """Kinyarwanda ASR model using Wav2Vec2"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sample_rate = 16000  # Wav2Vec2 expects 16kHz audio
    
    async def load_model(self):
        """Load the ASR model and processor"""
        try:
            # Load model and processor
            model_name = "facebook/wav2vec2-large-xlsr-53"  # Base model, to be fine-tuned
            self.processor = Wav2Vec2Processor.from_pretrained(model_name)
            self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
            
            # Move model to appropriate device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"ASR model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading ASR model: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.processor is not None
    
    async def unload_model(self):
        """Unload the model to free memory"""
        self.model = None
        self.processor = None
        torch.cuda.empty_cache()
    
    async def transcribe(self, audio_file) -> Tuple[str, float]:
        """Transcribe audio file to text"""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")
        
        try:
            # Load and preprocess audio
            waveform, sample_rate = torchaudio.load(audio_file)
            
            # Resample if necessary
            if sample_rate != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, self.sample_rate)
                waveform = resampler(waveform)
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Prepare input
            input_values = self.processor(
                waveform.squeeze().numpy(),
                sampling_rate=self.sample_rate,
                return_tensors="pt"
            ).input_values.to(self.device)
            
            # Perform inference
            with torch.no_grad():
                logits = self.model(input_values).logits
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.processor.batch_decode(predicted_ids)
                
                # Calculate confidence score
                probs = torch.nn.functional.softmax(logits, dim=-1)
                confidence = torch.mean(probs.max(dim=-1)[0]).item()
            
            return transcription[0], confidence
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    async def batch_transcribe(self, audio_files) -> list:
        """Transcribe multiple audio files"""
        results = []
        for audio_file in audio_files:
            try:
                text, confidence = await self.transcribe(audio_file)
                results.append({
                    "text": text,
                    "confidence": confidence
                })
            except Exception as e:
                logger.error(f"Error processing file {audio_file}: {e}")
                results.append({
                    "error": str(e)
                })
        return results 