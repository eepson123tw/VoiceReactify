from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from services.transcription_service import transcribe_audio_streaming,transcribe_audio_single
from pydub import AudioSegment
import numpy as np
import logging
from src.connectionDB import create_connection, create_voice_record, create_tag, associate_tag_with_voice_record
import aiofiles # type: ignore
from datetime import datetime
import uuid
import os
import sqlite3  # 確保引入 sqlite3

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe-stream")
async def transcribe_stream(
    file: UploadFile = File(...), 
    return_timestamps: bool = Form(False), 
    tags: str = Form(None)  # 可選的標籤參數
):
    """
    接收音頻文件，進行非同步轉譯，並以事件流方式返回轉譯結果。
    同時，將轉譯結果存入資料庫。
    """
    conn = None
    output_path = ""
    output_filename = ""
    voice_record_id = None

    try:
        logger.info("===== FILE INFO =====")
        logger.info(f"Received file: {file.filename}, Content Type: {file.content_type}")

        # 生成唯一檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"transcription_{timestamp}_{unique_id}.txt"
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join("transcriptions", date_str)  # 確保與 TTS 的 outVoiceFile 不同
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # 讀取音頻文件
        audio = AudioSegment.from_file(file.file)
        logger.info("===== AUDIO INFO =====")
        logger.info(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")
        audio = audio.set_frame_rate(16000)

        logger.info("===== STARTING STREAMING TRANSCRIPTION =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

        # 開始轉譯
        transcription_generator = transcribe_audio_streaming(audio_data, sampling_rate=16000, return_timestamps=return_timestamps)

        # 開啟資料庫連接
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # 準備記錄資料，初始狀態為 'transcribing'
        record = {
            "filename": output_filename,
            "filetype": "text/plain",
            "duration": audio.duration_seconds,
            "size": 0,  # 後續更新
            "filepath": output_path,
            "transcript": "",  # 後續更新
            "language": "zh-TW",  # 根據需求設置語言
            "status": "transcribing",
            "error_message": None,
            "parent_id": None  # 因為這是轉譯，不是衍生的檔案
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

        # 定義內部生成器，用於同步寫入檔案和傳輸事件
        async def internal_event_generator():
            nonlocal record
            try:
                async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
                    async for chunk in transcription_generator:
                        await f.write(chunk)
                        # 更新資料庫
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE voice_record SET transcript = transcript || ?, size = ? WHERE id = ?",
                            (chunk, os.path.getsize(output_path), voice_record_id)
                        )
                        conn.commit()
                        yield chunk  # 只回傳 chunk，不改變結構
                        
                # 最後更新狀態為 'completed'
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE voice_record SET status = ? WHERE id = ?",
                    ("completed", voice_record_id)
                )
                conn.commit()
                logger.info(f"Updated voice record ID {voice_record_id} status to 'completed'")
            except Exception as e:
                logger.error(f"Error during streaming transcription: {e}")
                # 更新狀態為錯誤
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE voice_record SET status = ?, error_message = ? WHERE id = ?",
                    ("error", str(e), voice_record_id)
                )
                conn.commit()
                raise e
            finally:
                conn.close()

        logger.info("===== STREAMING TRANSCRIPTION COMPLETED =====")
        return StreamingResponse(
            internal_event_generator(),
            media_type="text/event-stream"
        )
    except MemoryError as me:
        logger.error(f"MemoryError during transcription: {me}")
        raise HTTPException(status_code=500, detail="Memory error: " + str(me))
    except TimeoutError as te:
        logger.error(f"TimeoutError during transcription: {te}")
        raise HTTPException(status_code=500, detail="Timeout error: " + str(te))
    except Exception as e:
        logger.error(f"Error during transcription: {e}")

        # 嘗試將狀態更新為錯誤
        if conn and voice_record_id:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE voice_record SET status = ?, error_message = ? WHERE id = ?",
                    ("error", str(e), voice_record_id)
                )
                conn.commit()
                logger.info(f"Updated voice record ID {voice_record_id} status to 'error'")
            except sqlite3.Error as db_e:
                logger.error(f"Error updating voice record status: {db_e}")
            finally:
                conn.close()

        # 嘗試刪除已生成的檔案（如果存在）
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Removed corrupted transcription file: {output_path}")
            except Exception as file_e:
                logger.error(f"Error removing corrupted transcription file: {file_e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...), 
    return_timestamps: bool = Form(False), 
    tags: str = Form(None)
):
    """
    接收音頻文件，進行轉譯，並返回轉譯結果與 voice_record_id。
    同時，將轉譯結果存入資料庫。
    """
    conn = None
    output_path = ""
    output_filename = ""
    voice_record_id = None

    try:
        logger.info("===== FILE INFO =====")
        logger.info(f"Received file: {file.filename}, Content Type: {file.content_type}")

        # 生成唯一檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4()
        output_filename = f"transcription_{timestamp}_{unique_id}.txt"
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join("transcriptions", date_str)  # 確保與 TTS 的 outVoiceFile 不同
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # 讀取音頻文件
        audio = AudioSegment.from_file(file.file)
        logger.info("===== AUDIO INFO =====")
        logger.info(f"Audio duration: {audio.duration_seconds} seconds, Channels: {audio.channels}")
        audio = audio.set_frame_rate(16000)
        logger.info("===== CONVERTING AUDIO TO NUMPY ARRAY =====")
        audio_data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        logger.info(f"return_timestamps: {return_timestamps}")

        # 進行轉譯
        transcription = transcribe_audio_single(audio_data, sampling_rate=16000, return_timestamps=return_timestamps)
        logger.info(f"transcription: {transcription}")

        if transcription:
            logger.info("===== TRANSCRIPTION SUCCESSFUL =====")
            if return_timestamps:
            # return_timestamps 為 True，transcription 是字典列表，提取文本
                transcription_texts = [item['text'] for item in transcription]
                transcription_str = '\n'.join(transcription_texts)
            else:
                # return_timestamps 為 False，transcription 是純文本字串
                transcription_str = transcription

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcription_str)

            # 將轉譯結果存入資料庫
            conn = create_connection()
            if not conn:
                raise HTTPException(status_code=500, detail="Database connection failed")

            # 準備記錄資料
            record = {
                "filename": output_filename,
                "filetype": "text/plain",
                "duration": audio.duration_seconds,
                "size": os.path.getsize(output_path),
                "filepath": output_path,
                "transcript": transcription_str,  # 轉譯文字
                "language": "en",  # 根據需求設置語言
                "status": "completed",
                "error_message": None,
                "parent_id": None  # 因為這是轉譯，不是衍生的檔案
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

            return {"transcription": transcription, "record_id": voice_record_id}
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

        # 嘗試將狀態更新為錯誤
        if conn and voice_record_id:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE voice_record SET status = ?, error_message = ? WHERE id = ?",
                    ("error", str(e), voice_record_id)
                )
                conn.commit()
                logger.info(f"Updated voice record ID {voice_record_id} status to 'error'")
            except sqlite3.Error as db_e:
                logger.error(f"Error updating voice record status: {db_e}")
            finally:
                conn.close()

        # 嘗試刪除已生成的檔案（如果存在）
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Removed corrupted transcription file: {output_path}")
            except Exception as file_e:
                logger.error(f"Error removing corrupted transcription file: {file_e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")
