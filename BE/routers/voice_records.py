from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import sqlite3
import logging
from pydantic import BaseModel
from src.connectionDB import create_connection  

logger = logging.getLogger(__name__)

router = APIRouter()

# 定義 Pydantic 模型
class VoiceRecord(BaseModel):
    id: int
    filename: str
    filetype: str
    duration: float
    size: int
    createtime: str
    filepath: str
    transcript: str = None
    language: str = None
    status: str = "pending"
    error_message: str = None
    parent_id: int = None

@router.get("/voice-records", response_model=List[VoiceRecord])
async def get_all_voice_records():
    logger.info("Fetching all voice records.")
    conn = create_connection()
    if conn is None:
        logger.error("Failed to create database connection.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voice_record")
        rows = cursor.fetchall()
        
        # 獲取欄位名稱
        column_names = [description[0] for description in cursor.description]
        
        # 將資料轉換為字典列表
        records = [dict(zip(column_names, row)) for row in rows]
        
        # 關閉連接
        conn.close()
        
        return records
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail="Database query failed")

@router.get("/voice-records/{record_id}", response_model=VoiceRecord)
async def get_voice_record(record_id: int):
    logger.info(f"Fetching voice record with ID: {record_id}")
    conn = create_connection()
    if conn is None:
        logger.error("Failed to create database connection.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voice_record WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            logger.warning(f"Voice record with ID {record_id} not found.")
            raise HTTPException(status_code=404, detail="Voice record not found")
        
        # 獲取欄位名稱
        column_names = [description[0] for description in cursor.description]
        
        # 將資料轉換為字典
        record = dict(zip(column_names, row))
        
        conn.close()
        
        return record
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail="Database query failed")
