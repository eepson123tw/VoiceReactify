import torch
from TTS.api import TTS
import logging

logger = logging.getLogger(__name__)

tts = None

def initialize_tts():
    global tts
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device for TTS: {device}")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    logger.info("TTS model initialized successfully.")

async def generate_voice(prompt: str, speaker_wav: str, output_path: str):
    try:
        logger.info(f"Generating voice for prompt: {prompt}")
        tts.tts_to_file(prompt, speaker_wav=speaker_wav, language="en", file_path=output_path)
        logger.info(f"Voice generated and saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error during voice generation: {e}")
        raise e
