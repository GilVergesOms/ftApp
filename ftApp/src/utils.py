# ftApp/utils.py
import sqlite3
import os

def get_db_connection():
    """Devuelve conexión a la base de datos"""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_path = os.path.join(BASE_DIR, "data", "database.sqlite")
    conn = sqlite3.connect(db_path)
    return conn