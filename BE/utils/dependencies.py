from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import sqlite3
import logging
import os

from src.connectionDB import create_connection

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message

def get_db():
    conn = create_connection()
    if conn is None:
        raise DatabaseError("Database connection failed")
    try:
        yield conn
    finally:
        conn.close()

async def database_exception_handler(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message},
    )
