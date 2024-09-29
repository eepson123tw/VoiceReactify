from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.voice_assignment import perform_pronunciation_assessment
from pydub import AudioSegment
import os
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

# 定义基础目录，这里假设为 './originVoice/'
BASE_DIRECTORY = os.path.abspath('./originVoice/')

# 定义 Pydantic 模型
class PronunciationAssessmentRequest(BaseModel):
    reference_path: str
    reference_text: str

@router.post("/analysis", response_class=JSONResponse)
async def assess_pronunciation(request: PronunciationAssessmentRequest):
    reference_path = request.reference_path
    reference_text = request.reference_text
    logger.debug(f"Received reference_path: {reference_path}")
    logger.debug(f"Received reference_text: {reference_text}")

    # 构建实际文件路径
    normalized_path = os.path.normpath(os.path.join(BASE_DIRECTORY, reference_path))
    logger.debug(f"Normalized path: {normalized_path}")

    # 安全检查，确保路径在基础目录内
    if not normalized_path.startswith(BASE_DIRECTORY):
        logger.warning("Invalid reference path attempted.")
        raise HTTPException(status_code=400, detail="Invalid reference path.")

    realpath = normalized_path

    # 检查文件是否存在且为 WAV 文件
    if not os.path.isfile(realpath) or not realpath.lower().endswith('.wav'):
        logger.warning(f"File does not exist or is not a WAV file: {realpath}")
        raise HTTPException(status_code=400, detail="Specified file does not exist or is not a WAV file.")

    # 转换音频文件为临时文件 temp_audio.wav
    temp_audio_path = "temp_audio.wav"
    try:
        # 使用 pydub 读取音频文件
        audio = AudioSegment.from_file(realpath)
        # 导出为 WAV 格式的临时文件
        audio.export(temp_audio_path, format="wav")
        logger.debug(f"Exported temporary audio file to {temp_audio_path}")
    except Exception as e:
        logger.error(f"Failed to convert audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio file: {e}")

    # 执行发音评估
    try:
        assessment_result = perform_pronunciation_assessment(temp_audio_path, reference_text)
        logger.debug("Pronunciation assessment completed successfully.")
    except Exception as e:
        logger.error(f"Pronunciation assessment failed: {e}")
        raise HTTPException(status_code=500, detail="Pronunciation assessment failed.")
    finally:
        # 确保临时文件被删除
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                logger.debug(f"Removed temporary audio file: {temp_audio_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary audio file: {e}")

    return JSONResponse(content=assessment_result)
