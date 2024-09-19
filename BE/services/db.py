import os
import sqlite3
import logging
from src.connectionDB import create_connection, create_tables

logger = logging.getLogger(__name__)

def initialize_database():
    logger.info("Initializing database connection.")
    conn = create_connection()
    if conn:
        logger.info("Creating voice record table if not exists.")
        create_tables(conn)
        conn.close()
        logger.info("Database initialized successfully.")
    else:
        logger.error("Failed to initialize database connection.")
