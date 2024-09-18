import os
import sqlite3
import logging
from src.connectionDB import create_connection, create_voice_record_table

logger = logging.getLogger(__name__)

def initialize_database():
    logger.info("Initializing database connection.")
    conn = create_connection()
    if conn:
        logger.info("Creating voice record table if not exists.")
        create_voice_record_table(conn)
        conn.close()
        logger.info("Database initialized successfully.")
    else:
        logger.error("Failed to initialize database connection.")
