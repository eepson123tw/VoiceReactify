# src/connectionDB.py
import os
import sqlite3
from rich.console import Console
from dotenv import load_dotenv

# 初始化 Rich Console 用於美化日誌輸出
console = Console()

# 加載環境變數
load_dotenv()

def create_connection():
    conn = None
    try:
        db_path = os.getenv('DB_PATH', './db/voiceRecord.sqlite')
        db_dir = os.path.dirname(db_path)
        
        # 如果資料夾不存在，則創建
        if not os.path.exists(db_dir):
            console.print(f"[yellow]Database directory '{db_dir}' does not exist. Creating it...[/yellow]")
            os.makedirs(db_dir, exist_ok=True)
            console.print(f"[green]Database directory '{db_dir}' created successfully.[/green]")
        
        # 嘗試連接資料庫
        console.print(f"[blue]Database path:[/blue] {db_path}")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")  # 啟用外鍵支援
        console.print("[green]Connection successful with foreign keys enabled.[/green]")
        return conn
    except sqlite3.Error as e:
        console.print(f"[bold red]Error connecting to database:[/bold red] {e}")
        return None

# Table creation function
def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # 創建 voice_record 表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                filetype TEXT NOT NULL,
                duration REAL,
                size INTEGER,
                createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
                filepath TEXT NOT NULL,
                transcript TEXT,
                language TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                parent_id INTEGER REFERENCES voice_record(id) ON DELETE CASCADE
            );
        ''')

        # 創建 tags 表格
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS voice_record_tags (
                voice_record_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (voice_record_id) REFERENCES voice_record(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (voice_record_id, tag_id)
            );

            CREATE INDEX IF NOT EXISTS idx_voice_record_tags_voice_record_id ON voice_record_tags(voice_record_id);
            CREATE INDEX IF NOT EXISTS idx_voice_record_tags_tag_id ON voice_record_tags(tag_id);
        ''')
        
        # 創建索引
        cursor.executescript('''
            CREATE INDEX IF NOT EXISTS idx_voice_record_filename ON voice_record(filename);
            CREATE INDEX IF NOT EXISTS idx_voice_record_createtime ON voice_record(createtime);
            CREATE INDEX IF NOT EXISTS idx_voice_record_status ON voice_record(status);
        ''')

        conn.commit()
        console.print("[green]All tables and indexes created successfully.[/green]")
    except sqlite3.Error as e:
        console.print(f"[bold red]Error creating tables or indexes:[/bold red] {e}")

# 新增 voice_record 資料的函數
def create_voice_record(conn, record):
    """
    將一條語音記錄插入到 voice_record 表格中。
    :param conn: SQLite 資料庫連接物件
    :param record: 字典，包含以下鍵值：
        - filename (str): 檔案名稱
        - filetype (str): 檔案類型
        - duration (float): 語音持續時間（秒）
        - size (int): 檔案大小（位元組）
        - filepath (str): 檔案路徑
        - transcript (str): 轉譯文字
        - language (str): 語言
        - status (str): 狀態
        - error_message (str): 錯誤訊息
        - parent_id (int): 原始語音檔案的 ID（可選）
    :return: 新插入的語音記錄的 ID 或 None
    """
    sql = '''
        INSERT INTO voice_record (filename, filetype, duration, size, filepath, transcript, language, status, error_message, parent_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            record.get('filename'),
            record.get('filetype'),
            record.get('duration'),
            record.get('size'),
            record.get('filepath'),
            record.get('transcript'),
            record.get('language'),
            record.get('status'),
            record.get('error_message'),
            record.get('parent_id')  # 可選
        ))
        conn.commit()
        voice_record_id = cursor.lastrowid
        console.print(f"[green]Voice record inserted with ID: {voice_record_id}[/green]")
        return voice_record_id
    except sqlite3.IntegrityError as e:
        console.print(f"[bold red]IntegrityError inserting voice record:[/bold red] {e}")
        return None
    except sqlite3.Error as e:
        console.print(f"[bold red]Error inserting voice record:[/bold red] {e}")
        return None

# 新增 tag 的函數
def create_tag(conn, tag):
    """
    將一個標籤插入到 tags 表格中。如果標籤已存在，返回其 ID。
    :param conn: SQLite 資料庫連接物件
    :param tag: 標籤名稱 (str)
    :return: 標籤的 ID 或 None
    """
    sql = '''
        INSERT OR IGNORE INTO tags (tag)
        VALUES (?)
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (tag,))
        conn.commit()
        if cursor.lastrowid:
            tag_id = cursor.lastrowid
            console.print(f"[green]Tag '{tag}' inserted with ID: {tag_id}[/green]")
            return tag_id
        else:
            # 查詢已存在的 tag 的 ID
            cursor.execute("SELECT id FROM tags WHERE tag = ?", (tag,))
            result = cursor.fetchone()
            if result:
                tag_id = result[0]
                console.print(f"[blue]Tag '{tag}' already exists with ID: {tag_id}[/blue]")
                return tag_id
            else:
                console.print(f"[bold red]Failed to retrieve tag ID for '{tag}'[/bold red]")
                return None
    except sqlite3.Error as e:
        console.print(f"[bold red]Error inserting tag '{tag}':[/bold red] {e}")
        return None

# 關聯 voice_record 與 tags 的函數
def associate_tag_with_voice_record(conn, voice_record_id, tag_id):
    """
    將標籤與語音記錄進行關聯。
    :param conn: SQLite 資料庫連接物件
    :param voice_record_id: 語音記錄的 ID (int)
    :param tag_id: 標籤的 ID (int)
    :return: True 成功, False 失敗
    """
    sql = '''
        INSERT OR IGNORE INTO voice_record_tags (voice_record_id, tag_id)
        VALUES (?, ?)
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (voice_record_id, tag_id))
        conn.commit()
        console.print(f"[green]Associated voice_record ID {voice_record_id} with tag ID {tag_id}[/green]")
        return True
    except sqlite3.Error as e:
        console.print(f"[bold red]Error associating tag ID {tag_id} with voice_record ID {voice_record_id}:[/bold red] {e}")
        return False

# 初始化資料庫
def initialize_database():
    connection = create_connection()
    if connection:
        create_tables(connection)
        connection.close()

# 只在此模組被執行時初始化資料庫
if __name__ == "__main__":
    initialize_database()
