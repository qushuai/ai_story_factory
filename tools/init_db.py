import sqlite3
import os

# -----------------------------
# 数据库路径
# -----------------------------
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(project_dir, "db")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "audio_library.db")

# -----------------------------
# 连接数据库
# -----------------------------
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# -----------------------------
# 创建音频库表
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    alias TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT,
    emotion TEXT,
    duration_ms INTEGER,
    loopable BOOLEAN DEFAULT 0,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,
    status TEXT DEFAULT 'active'
)
""")

# -----------------------------
# 创建使用日志表
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audio_id INTEGER NOT NULL,
    alias TEXT,
    task_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    duration_ms INTEGER,
    FOREIGN KEY (audio_id) REFERENCES audio_library(id)
)
""")

# -----------------------------
# 提交并关闭
# -----------------------------
conn.commit()
conn.close()

print(f"数据库已创建: {db_path}")