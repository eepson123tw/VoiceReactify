from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse
import uuid
import os
from datetime import datetime
from services.tts_service import generate_voice
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-voice", response_model=None)
async def generate_voice_endpoint(prompt: str = Form(...), description: str = Form(...)):
    try:
        logger.info(f"Received prompt: {prompt}")
        logger.info(f"Received description: {description}")
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"parler_tts_{timestamp}_{unique_id}.wav"
        output_dir = "outVoiceFile"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        pakora_path = os.path.join('pekora', "pekora.wav")
        
        # Generate voice
        await generate_voice(prompt, pakora_path, output_path)
        
        # Stream the file
        def iterfile():
            with open(output_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(
            iterfile(),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e:
        logger.error(f"Error in generate_voice_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
