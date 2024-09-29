from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse,HTMLResponse
from services.voice_assignment import perform_pronunciation_assessment
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_class=HTMLResponse)
async def assess_pronunciation(file: UploadFile = File(...), reference_text: str = "your reference text"):
    # 驗證文件類型
    if not file.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Only WAV files are supported.")

    # 保存上傳的文件到臨時位置
    try:
        with open("temp_audio.wav", "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    # 執行發音評估
    try:
        assessment_result = perform_pronunciation_assessment("temp_audio.wav", reference_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation assessment failed: {e}")

    return JSONResponse(content=assessment_result)
