import os
import sqlite3
from rich.console import Console

console = Console()

# SQLite connection function
def create_connection():
    conn = None
    try:
        # Get the absolute path
        db_path = os.path.abspath('./db/voiceRecord.sqlite')  
        console.print(f"[bold cyan]Database path:[/bold cyan] {db_path}")
        
        # Establish connection to SQLite database
        conn = sqlite3.connect(db_path)
        console.print("[green]Connection successful[/green]")
        return conn
    except sqlite3.Error as e:
        console.print(f"[bold red]Error connecting to database:[/bold red] {e}")
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
