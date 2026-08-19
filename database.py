import sqlite3

class Database:
    def __init__(self, db_file="database.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Создает таблицу пользователей, если её нет"""
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
        self.add_user(user_id)  # Убедимся, что пользователь есть
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
        
        # Превращаем кортеж в словарь с ключами как в вашем старом коде
        keys = ['user_id', 'USDT', 'GRAM', 'SOL', 'TRX', 'BTC', 'ETH', 'DOGE', 'LTC', 'BNB', 'USDC', 'XAUT']
        return dict(zip(keys, row))

    def update_balance(self, user_id: int, currency: str, amount: float):
        """Обновляет баланс (добавляет или вычитает)"""
        self.add_user(user_id)
        current = self.get_balance(user_id, currency)
        new_balance = current + amount
        
        # Защита от отрицательного баланса
        if new_balance < 0:
            new_balance = 0.0
            
        self.cursor.execute(f"UPDATE users SET {currency.lower()} = ? WHERE user_id = ?", (new_balance, user_id))
        self.conn.commit()

    def close(self):
        """Закрывает соединение с БД"""
        self.conn.close()