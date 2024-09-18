from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from services.transcription_service import transcribe_audio_streaming, transcribe_audio_single
from pydub import AudioSegment
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe-stream")
async def transcribe_stream(file: UploadFile = File(...), return_timestamps: bool = Form(False)):
    try:
        logger.info("===== FILE INFO =====")
        logger.info(f"Received file: {file.filename}, Content Type: {file.content_type}")

        audio = AudioSegment.from_file(file.file)
        logger.info("===== AUDIO INFO =====")
        logger.info(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")
        audio = audio.set_frame_rate(16000)
        
        logger.info("===== STARTING STREAMING TRANSCRIPTION =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        transcription_generator = transcribe_audio_streaming(audio_data, sampling_rate=16000, return_timestamps=return_timestamps)
        
        logger.info("===== STREAMING TRANSCRIPTION COMPLETED =====")
        return StreamingResponse(transcription_generator, media_type="text/event-stream")
    except MemoryError as me:
        logger.error(f"MemoryError during transcription: {me}")
        raise HTTPException(status_code=500, detail="Memory error: " + str(me))
    except TimeoutError as te:
        logger.error(f"TimeoutError during transcription: {te}")
        raise HTTPException(status_code=500, detail="Timeout error: " + str(te))
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), return_timestamps: bool = Form(False)):
    try:
        logger.info("===== FILE INFO =====")
        logger.info(f"Received file: {file.filename}, Content Type: {file.content_type}")

        audio = AudioSegment.from_file(file.file)
        logger.info("===== AUDIO INFO =====")
        logger.info(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")

        audio = audio.set_frame_rate(16000)
        logger.info("===== CONVERTING AUDIO TO NUMPY ARRAY =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        logger.info(f"return_timestamps: {return_timestamps}")
        
        transcription = transcribe_audio_single(audio_data, sampling_rate=16000, return_timestamps=return_timestamps)
        logger.info(f"transcription: {transcription}")
        
        if transcription:
            logger.info("===== TRANSCRIPTION SUCCESSFUL =====")
            return {"transcription": transcription}
        else:
            logger.warning("===== TRANSCRIPTION FAILED =====")
            raise ValueError("Transcription failed or returned unexpected format.")
    except MemoryError as me:
        logger.error(f"MemoryError during transcription: {me}")
        raise HTTPException(status_code=500, detail="Memory error: " + str(me))
    except TimeoutError as te:
        logger.error(f"TimeoutError during transcription: {te}")
        raise HTTPException(status_code=500, detail="Timeout error: " + str(te))
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
