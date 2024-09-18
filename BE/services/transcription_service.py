import asyncio
import json
from typing import AsyncGenerator
import logging
from src.voice_model import transcribe_audio

logger = logging.getLogger(__name__)

async def transcribe_audio_streaming(audio_data, sampling_rate, return_timestamps) -> AsyncGenerator[str, None]:
    try:
        transcription = transcribe_audio(audio_data, sampling_rate, return_timestamps)
        for transcription_part in transcription:
            logger.info(f"Transcription part: {transcription_part}")
            yield f"data: {json.dumps({'transcription': transcription_part})}\n\n"
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Error during streaming transcription: {e}")
        raise e

def transcribe_audio_single(audio_data, sampling_rate, return_timestamps):
    try:
        transcription = transcribe_audio(audio_data, sampling_rate, return_timestamps)
        return transcription
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise e
