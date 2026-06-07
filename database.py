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


def savat_saqlash(user_id: int, savat_items: list):
    """Foydalanuvchi savatini bazaga saqlash."""
    import json
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS savat (
                user_id INTEGER PRIMARY KEY,
                items TEXT,
                yangilangan TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            INSERT OR REPLACE INTO savat (user_id, items, yangilangan)
            VALUES (?, ?, datetime('now'))
        """, (user_id, json.dumps(savat_items, ensure_ascii=False)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Savat saqlashda xato: {e}")


def savat_yuklash(user_id: int) -> list:
    """Foydalanuvchi savatini bazadan yuklash."""
    import json
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS savat (user_id INTEGER PRIMARY KEY, items TEXT, yangilangan TEXT)")
        c.execute("SELECT items FROM savat WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return []
    except Exception as e:
        logger.error(f"Savat yuklashda xato: {e}")
        return []


def savat_tozalash(user_id: int):
    """Foydalanuvchi savatini bazadan o'chirish."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM savat WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Savat o'chirishda xato: {e}")
