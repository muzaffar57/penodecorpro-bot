import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_FILE = "penodecor.db"


def init_db():
    """Bazani yaratish."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            ism TEXT,
            username TEXT,
            birinchi_sana TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Baza tayyor!")


def foydalanuvchi_qoshish(user_id: int, ism: str, username: str = ""):
    """Yangi foydalanuvchini bazaga qo'shish."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO users (user_id, ism, username)
            VALUES (?, ?, ?)
        """, (user_id, ism, username or ""))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Foydalanuvchi qo'shishda xato: {e}")


def barcha_userlar() -> list:
    """Barcha user_id larni olish."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        natija = [row[0] for row in c.fetchall()]
        conn.close()
        return natija
    except Exception as e:
        logger.error(f"Userlarni olishda xato: {e}")
        return []


def foydalanuvchilar_soni() -> int:
    """Jami foydalanuvchilar soni."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        soni = c.fetchone()[0]
        conn.close()
        return soni
    except:
        return 0
