import sqlite3
import os

from core.config_loader import config


DB_PATH = config["database"]["path"]

SFX_DIR = config["paths"]["sfx_dir"]


def get_sfx_map():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT alias,file_name
        FROM audio_library
        WHERE type='sfx'
    """)

    rows = cursor.fetchall()

    conn.close()

    sfx_map = {}

    for alias, file_name in rows:

        path = os.path.join(SFX_DIR, file_name)

        sfx_map[alias] = path

    return sfx_map