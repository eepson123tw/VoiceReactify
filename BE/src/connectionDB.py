import os
import sqlite3
from rich.console import Console
from dotenv import load_dotenv

# SQLite connection function
# Load environment variables from .env file
console = Console()
load_dotenv()

def create_connection():
    conn = None
    try:
        db_path = os.getenv('DB_PATH', './db/voiceRecord.sqlite')
        print(f"Database path: {db_path}")
        conn = sqlite3.connect(db_path)
        print("Connection successful")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Table creation function
def create_voice_record_table(conn):
    try:
        cursor = conn.cursor()
        # SQL statement to create the voice_record table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filetype TEXT NOT NULL,
                duration INTEGER,
                size INTEGER,
                createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
                filepath TEXT NOT NULL,
                transcript TEXT,
                tags TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()
        console.print("[green]Table created successfully[/green]")
    except sqlite3.Error as e:
        console.print(f"[bold red]Error creating table:[/bold red] {e}")
