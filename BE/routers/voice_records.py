from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging
from pydantic import BaseModel
from utils.dependencies import get_db, DatabaseError
import sqlite3

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

def fetch_all_records(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[dict]:
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        records = [dict(zip(column_names, row)) for row in rows]
        return records
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        raise DatabaseError("Database query failed")

@router.get("/all", response_model=List[VoiceRecord])
def get_all_voice_records(conn: sqlite3.Connection = Depends(get_db)):
    logger.info("Fetching all voice records.")
    records = fetch_all_records(conn, "SELECT * FROM voice_record")
    return records

@router.get("/{record_id}", response_model=VoiceRecord)
def get_voice_record(record_id: int, conn: sqlite3.Connection = Depends(get_db)):
    logger.info(f"Fetching voice record with ID: {record_id}")
    records = fetch_all_records(conn, "SELECT * FROM voice_record WHERE id = ?", (record_id,))
    if not records:
        logger.warning(f"Voice record with ID {record_id} not found.")
        raise HTTPException(status_code=404, detail="Voice record not found")
    return records[0]
