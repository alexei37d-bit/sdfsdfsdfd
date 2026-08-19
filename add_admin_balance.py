from database import Database

# ID админов
ADMIN_IDS = [7921743592, 5744099934]

# Сумма для добавления (100 условных единиц каждой валюты)
AMOUNT = 100.0

# Список всех валют из вашей БД
CURRENCIES = ["USDT", "GRAM", "SOL", "TRX", "BTC", "ETH", "DOGE", "LTC", "BNB", "USDC", "XAUT"]

def main():
    db = Database()
    
    print("Начало обновления балансов...")
    
    for user_id in ADMIN_IDS:
        # 1. Гарантируем, что пользователь есть в базе
        db.add_user(user_id)
        
        print(f"Обработка пользователя {user_id}...")
        
        # 2. Добавляем по 100 единиц каждой валюты
        for currency in CURRENCIES:
            db.update_balance(user_id, currency, AMOUNT)
            
        print(f"✅ Пользователю {user_id} добавлено по {AMOUNT} ед. каждой валюты.")

    db.close()
    print("Готово! База данных обновлена.")

if __name__ == "__main__":
    main()
