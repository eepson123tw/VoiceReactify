from fastapi import APIRouter, Form, HTTPException
from pydub import AudioSegment
from fastapi.responses import StreamingResponse
import os
import uuid
from datetime import datetime
import logging
from src.connectionDB import create_connection, create_voice_record, create_tag, associate_tag_with_voice_record
from services.tts_service import generate_voice
import aiofiles # type: ignore
import sqlite3

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate-voice", response_model=None)
async def generate_voice_endpoint(
    prompt: str = Form(...),
    description: str = Form(...),
    tags: str = Form(None),  # 可選的標籤參數
    original_record_id: int = Form(...),  # 新增參數，關聯轉譯記錄
):
    """
    生成語音檔案並將相關資訊寫入資料庫。
    :param prompt: 用戶輸入的文字提示
    :param description: 描述或轉譯文字
    :param tags: 逗號分隔的標籤字串（可選）
    :param original_record_id: 轉譯記錄的 ID，用於關聯
    :return: 語音檔案的串流響應
    """
    conn = None
    output_path = ""
    output_filename = ""

    try:
        logger.info(f"Received prompt: {prompt}")
        logger.info(f"Received description: {description}")
        logger.info(f"Received tags: {tags}")
        logger.info(f"Original Record ID: {original_record_id}")

        # 生成唯一檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"parler_tts_{timestamp}_{unique_id}.wav"
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join("outVoiceFile", date_str)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        pakora_path = os.path.join('pekora', "pekora.wav")

        logger.info(f"Generating voice file at: {output_path}")

        # 生成語音
        await generate_voice(prompt, pakora_path, output_path)

        # 獲取檔案資訊
        file_size = os.path.getsize(output_path)
        try:
            audio = AudioSegment.from_file(output_path)
            duration = audio.duration_seconds
            logger.info(f"Audio duration: {duration} seconds, Size: {file_size} bytes")
        except Exception as audio_e:
            logger.error(f"Error processing audio file with pydub: {audio_e}")
            raise HTTPException(status_code=500, detail="Error processing audio file")

        # 將檔案資訊寫入資料庫
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # 準備記錄資料
        record = {
            "filename": output_filename,
            "filetype": "audio/wav",
            "duration": duration,
            "size": file_size,
            "filepath": output_path,
            "transcript": description,  # 假設 description 為轉譯文字
            "language": "zh-TW",  # 根據需求設置語言
            "status": "completed",
            "error_message": None,
            "parent_id": original_record_id  # 關聯轉譯記錄
        }

        # 插入 voice_record 表格
        voice_record_id = create_voice_record(conn, record)
        if not voice_record_id:
            raise HTTPException(status_code=500, detail="Failed to insert voice record into database")

        # 處理標籤（如果有）
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            for tag in tag_list:
                tag_id = create_tag(conn, tag)
                if tag_id:
                    associate_tag_with_voice_record(conn, voice_record_id, tag_id)

        # 關閉資料庫連接
        conn.close()

        # 串流檔案
        async def iterfile():
            async with aiofiles.open(output_path, mode="rb") as f:
                while True:
                    chunk = await f.read(1024 * 1024)  # 每次讀取1MB
                    if not chunk:
                        break
                    yield chunk

        logger.info(f"Streaming voice file: {output_filename}")
        return StreamingResponse(
            iterfile(),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e:
        logger.error(f"Error in generate_voice_endpoint: {e}")

        # 嘗試將狀態更新為錯誤
        if conn and output_filename:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE voice_record SET status = ?, error_message = ? WHERE filename = ?",
                    ("error", str(e), output_filename)
                )
                conn.commit()
                logger.info(f"Updated voice record '{output_filename}' status to 'error'")
            except sqlite3.Error as db_e:
                logger.error(f"Error updating voice record status: {db_e}")
            finally:
                conn.close()

        # 嘗試刪除已生成的檔案（如果存在）
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Removed corrupted audio file: {output_path}")
            except Exception as file_e:
                logger.error(f"Error removing corrupted audio file: {file_e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")
