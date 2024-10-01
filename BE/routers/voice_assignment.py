from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.voice_assignment import perform_pronunciation_assessment
from pydub import AudioSegment
import os
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIRECTORY = os.path.abspath('./originVoice/')

class PronunciationAssessmentRequest(BaseModel):
    reference_path: str
    reference_text: str

@router.post("/analysis", response_class=JSONResponse)
async def assess_pronunciation(request: PronunciationAssessmentRequest):
    reference_path = request.reference_path
    reference_text = request.reference_text
    logger.debug(f"Received reference_path: {reference_path}")
    logger.debug(f"Received reference_text: {reference_text}")


    normalized_path = os.path.normpath(os.path.join(BASE_DIRECTORY, reference_path))
    logger.debug(f"Normalized path: {normalized_path}")


    if not normalized_path.startswith(BASE_DIRECTORY):
        logger.warning("Invalid reference path attempted.")
        raise HTTPException(status_code=400, detail="Invalid reference path.")

    realpath = normalized_path


    if not os.path.isfile(realpath) or not realpath.lower().endswith('.wav'):
        logger.warning(f"File does not exist or is not a WAV file: {realpath}")
        raise HTTPException(status_code=400, detail="Specified file does not exist or is not a WAV file.")


    temp_audio_path = "temp_audio.wav"
    try:
    
        audio = AudioSegment.from_file(realpath)
    
        audio.export(temp_audio_path, format="wav")
        logger.debug(f"Exported temporary audio file to {temp_audio_path}")
    except Exception as e:
        logger.error(f"Failed to convert audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio file: {e}")


    try:
        assessment_result = perform_pronunciation_assessment(temp_audio_path, reference_text)
        logger.debug("Pronunciation assessment completed successfully.")
    except Exception as e:
        logger.error(f"Pronunciation assessment failed: {e}")
        raise HTTPException(status_code=500, detail="Pronunciation assessment failed.")
    finally:
    
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                logger.debug(f"Removed temporary audio file: {temp_audio_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary audio file: {e}")

    return JSONResponse(content=assessment_result)
