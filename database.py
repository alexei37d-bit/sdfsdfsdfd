import sqlite3
import time
import random
import string

class Database:
    def __init__(self, db_file="database.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица пользователей (остается как была)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                usdt REAL DEFAULT 0.0,
                gram REAL DEFAULT 0.0,
                sol REAL DEFAULT 0.0,
                trx REAL DEFAULT 0.0,
                btc REAL DEFAULT 0.0,
                eth REAL DEFAULT 0.0,
                doge REAL DEFAULT 0.0,
                ltc REAL DEFAULT 0.0,
                bnb REAL DEFAULT 0.0,
                usdc REAL DEFAULT 0.0,
                xaut REAL DEFAULT 0.0
            )
        """)
        
        # Новая таблица для чеков
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id TEXT PRIMARY KEY,
                creator_id INTEGER,
                currency TEXT,
                amount REAL,
                created_at INTEGER,
                is_active INTEGER DEFAULT 1,
                activated_by INTEGER DEFAULT NULL
            )
        """)
        self.conn.commit()

    # --- Методы пользователей (без изменений) ---
    def add_user(self, user_id: int):
        try:
            self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_balance(self, user_id: int, currency: str):
        self.add_user(user_id)
        self.cursor.execute(f"SELECT {currency.lower()} FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def get_all_balances(self, user_id: int):
        self.add_user(user_id)
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row: return {}
        keys = ['user_id', 'USDT', 'GRAM', 'SOL', 'TRX', 'BTC', 'ETH', 'DOGE', 'LTC', 'BNB', 'USDC', 'XAUT']
        return dict(zip(keys, row))

    def update_balance(self, user_id: int, currency: str, amount: float):
        self.add_user(user_id)
        current = self.get_balance(user_id, currency)
        new_balance = current + amount
        if new_balance < 0: new_balance = 0.0
        self.cursor.execute(f"UPDATE users SET {currency.lower()} = ? WHERE user_id = ?", (new_balance, user_id))
        self.conn.commit()

    # --- Новые методы для чеков ---
    def create_check(self, check_id: str, creator_id: int, currency: str, amount: float):
        """Создает чек в БД"""
        self.cursor.execute(
            "INSERT INTO checks (id, creator_id, currency, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (check_id, creator_id, currency, amount, int(time.time()))
        )
        self.conn.commit()

    def get_check(self, check_id: str):
        """Получает информацию о чеке"""
        self.cursor.execute("SELECT * FROM checks WHERE id = ?", (check_id,))
        row = self.cursor.fetchone()
        if not row: return None
        return {
            "id": row[0], "creator_id": row[1], "currency": row[2], 
            "amount": row[3], "created_at": row[4], "is_active": row[5], "activated_by": row[6]
        }

    def activate_check(self, check_id: str, activator_id: int):
        """Активирует чек (помечает как использованный)"""
        self.cursor.execute(
            "UPDATE checks SET is_active = 0, activated_by = ? WHERE id = ? AND is_active = 1",
            (activator_id, check_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_user_checks(self, user_id: int):
        """Получает список активных чеков пользователя"""
        self.cursor.execute(
            "SELECT * FROM checks WHERE creator_id = ? AND is_active = 1 ORDER BY created_at DESC",
            (user_id,)
        )
        rows = self.cursor.fetchall()
        checks = []
        for row in rows:
            checks.append({
                "id": row[0], "currency": row[2], "amount": row[3], "created_at": row[4]
            })
        return checks

    def delete_check(self, check_id: str, user_id: int):
        """Удаляет чек (только если он принадлежит пользователю)"""
        self.cursor.execute(
            "DELETE FROM checks WHERE id = ? AND creator_id = ?",
            (check_id, user_id)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
