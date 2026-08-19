import sqlite3

class Database:
    def __init__(self, db_file="database.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Создает таблицы пользователей и чеков, если их нет"""
        # Таблица пользователей
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
        
        # Таблица чеков
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id TEXT PRIMARY KEY,
                creator_id INTEGER,
                currency TEXT,
                amount REAL,
                is_active INTEGER DEFAULT 1,
                activated_by INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()

    def add_user(self, user_id: int):
        """Добавляет нового пользователя в БД"""
        try:
            self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Пользователь уже существует

    def get_balance(self, user_id: int, currency: str):
        """Получает баланс конкретной валюты у пользователя"""
        self.add_user(user_id)
        self.cursor.execute(f"SELECT {currency.lower()} FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def get_all_balances(self, user_id: int):
        """Получает все балансы пользователя в виде словаря"""
        self.add_user(user_id)
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return {}
        keys = ['user_id', 'USDT', 'GRAM', 'SOL', 'TRX', 'BTC', 'ETH', 'DOGE', 'LTC', 'BNB', 'USDC', 'XAUT']
        return dict(zip(keys, row))

    def update_balance(self, user_id: int, currency: str, amount: float):
        """Обновляет баланс (добавляет или вычитает)"""
        self.add_user(user_id)
        current = self.get_balance(user_id, currency)
        new_balance = current + amount
        if new_balance < 0:
            new_balance = 0.0
        self.cursor.execute(f"UPDATE users SET {currency.lower()} = ? WHERE user_id = ?", (new_balance, user_id))
        self.conn.commit()

    # --- МЕТОДЫ ДЛЯ ЧЕКОВ ---

    def create_check(self, check_id: str, creator_id: int, currency: str, amount: float):
        """Создает запись о новом чеке"""
        self.cursor.execute(
            "INSERT INTO checks (id, creator_id, currency, amount, is_active) VALUES (?, ?, ?, ?, 1)",
            (check_id, creator_id, currency, amount)
        )
        self.conn.commit()

    def get_check(self, check_id: str):
        """Получает информацию о чеке по ID"""
        self.cursor.execute("SELECT * FROM checks WHERE id = ?", (check_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        keys = ['id', 'creator_id', 'currency', 'amount', 'is_active', 'activated_by', 'created_at']
        return dict(zip(keys, row))

    def get_user_checks(self, user_id: int):
        """Получает список активных чеков пользователя"""
        self.cursor.execute("SELECT * FROM checks WHERE creator_id = ? AND is_active = 1", (user_id,))
        rows = self.cursor.fetchall()
        checks = []
        keys = ['id', 'creator_id', 'currency', 'amount', 'is_active', 'activated_by', 'created_at']
        for row in rows:
            checks.append(dict(zip(keys, row)))
        return checks

    def activate_check(self, check_id: str, activator_id: int):
        """Помечает чек как активированный"""
        self.cursor.execute(
            "UPDATE checks SET is_active = 0, activated_by = ? WHERE id = ?",
            (activator_id, check_id)
        )
        self.conn.commit()

    def delete_check(self, check_id: str, user_id: int):
        """Удаляет чек из базы данных"""
        self.cursor.execute("DELETE FROM checks WHERE id = ? AND creator_id = ?", (check_id, user_id))
        self.conn.commit()

    def close(self):
        """Закрывает соединение с БД"""
        self.conn.close()
