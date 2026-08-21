import sqlite3

class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS balances (user_id INTEGER, currency TEXT, amount REAL DEFAULT 0, PRIMARY KEY (user_id, currency))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS invoices (invoice_id TEXT PRIMARY KEY, creator_id INTEGER, amount_usd REAL, currencies TEXT, invoice_type TEXT, allow_comments INTEGER DEFAULT 1, allow_anonymous INTEGER DEFAULT 1, is_paid INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS payments (payment_id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id TEXT, payer_id INTEGER, currency TEXT, amount_sent REAL, amount_usd REAL, comment TEXT, is_anonymous INTEGER DEFAULT 0, paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.conn.commit()
    
    def add_user(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        self.conn.commit()
    
    def get_balance(self, user_id, currency):
        self.cursor.execute('SELECT amount FROM balances WHERE user_id=? AND currency=?', (user_id, currency))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0
    
    def update_balance(self, user_id, currency, amount):
        self.cursor.execute('INSERT OR REPLACE INTO balances (user_id, currency, amount) VALUES (?, ?, ?)', 
                          (user_id, currency, amount))
        self.conn.commit()
    
    def add_to_balance(self, user_id, currency, amount):
        current = self.get_balance(user_id, currency)
        new_amount = current + amount
        if new_amount < 0:
            new_amount = 0
        self.update_balance(user_id, currency, new_amount)
    
    def get_all_balances(self, user_id):
        self.cursor.execute('SELECT currency, amount FROM balances WHERE user_id=?', (user_id,))
        results = self.cursor.fetchall()
        return {row[0]: row[1] for row in results}
    
    def create_invoice(self, invoice_id, creator_id, amount_usd, currencies, invoice_type, 
                      allow_comments=1, allow_anonymous=1):
        self.cursor.execute("INSERT INTO invoices (invoice_id, creator_id, amount_usd, currencies, invoice_type, allow_comments, allow_anonymous) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (invoice_id, creator_id, amount_usd, ','.join(currencies), invoice_type, 
             allow_comments, allow_anonymous))
        self.conn.commit()
    
    def get_invoice(self, invoice_id):
        self.cursor.execute('SELECT * FROM invoices WHERE invoice_id=?', (invoice_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'invoice_id': result[0],
                'creator_id': result[1],
                'amount_usd': result[2],
                'currencies': result[3].split(','),
                'invoice_type': result[4],
                'allow_comments': result[5],
                'allow_anonymous': result[6],
                'is_paid': result[7],
                'is_active': result[8],
                'created_at': result[9]
            }
        return None
    
    def update_invoice_settings(self, invoice_id, allow_comments=None, allow_anonymous=None):
        if allow_comments is not None:
            self.cursor.execute('UPDATE invoices SET allow_comments=? WHERE invoice_id=?', 
                              (allow_comments, invoice_id))
        if allow_anonymous is not None:
            self.cursor.execute('UPDATE invoices SET allow_anonymous=? WHERE invoice_id=?', 
                              (allow_anonymous, invoice_id))
        self.conn.commit()
    
    def mark_invoice_paid(self, invoice_id):
        self.cursor.execute('UPDATE invoices SET is_paid=1 WHERE invoice_id=?', (invoice_id,))
        self.conn.commit()
    
    def delete_invoice(self, invoice_id):
        self.cursor.execute('UPDATE invoices SET is_active=0 WHERE invoice_id=?', (invoice_id,))
        self.conn.commit()
    
    def get_user_invoices(self, user_id):
        self.cursor.execute('SELECT invoice_id FROM invoices WHERE creator_id=? AND is_active=1', (user_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_active_invoices_for_list(self, user_id):
        self.cursor.execute("SELECT invoice_id FROM invoices WHERE creator_id=? AND is_active=1 AND NOT (invoice_type='single' AND is_paid=1)", (user_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_payment(self, invoice_id, payer_id, currency, amount_sent, amount_usd, comment='', is_anonymous=0):
        self.cursor.execute("INSERT INTO payments (invoice_id, payer_id, currency, amount_sent, amount_usd, comment, is_anonymous) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (invoice_id, payer_id, currency, amount_sent, amount_usd, comment, is_anonymous))
        self.conn.commit()
    
    def close(self):
        self.conn.close()
