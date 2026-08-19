import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Токен бота
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Имитация базы данных балансов (можно менять значения для теста)
user_balances = {
    "USDT": 0.00000000,
    "GRAM": 0.00000000,
    "SOL": 0.00000000,
    "TRX": 0.00000000,
    "BTC": 0.00000000,
    "ETH": 0.00000000,
    "DOGE": 0.00000000,
    "LTC": 0.00000000,
    "BNB": 0.00000000,
    "USDC": 0.00000000,
    "XAUT": 0.00000000
}

# Функция для получения текста баланса
def get_wallet_text(user_id: int):
    # Для примера берем баланс из словаря (в реальном боте тут будет запрос к БД)
    b = user_balances 
    
    # Расчет общего баланса в BTC (условный курс для примера)
    total_btc = (
        b["USDT"] * 0.00001 + 
        b["GRAM"] * 0.0000001 + 
        b["SOL"] * 0.002 + 
        b["TRX"] * 0.000002 + 
        b["BTC"] + 
        b["ETH"] * 0.03 + 
        b["DOGE"] * 0.000001 + 
        b["LTC"] * 0.001 + 
        b["BNB"] * 0.005 + 
        b["USDC"] * 0.00001 + 
        b["XAUT"] * 0.03
    )
    
    text = (
        f"<b><tg-emoji emoji-id=\"5310191758255099001\">👛</tg-emoji> Кошелек</b>\n\n"
        f"<tg-emoji emoji-id=\"5406841020769936275\">️</tg-emoji> Tether: {b['USDT']:.8f} USDT\n"
        f"<tg-emoji emoji-id=\"5318901904686754959\">🙂</tg-emoji> Gram: {b['GRAM']:.8f} GRAM\n"
        f"<tg-emoji emoji-id=\"5407016676342401484\">️</tg-emoji> Solana: {b['SOL']:.8f} SOL\n"
        f"<tg-emoji emoji-id=\"5406978786140918829\">☺️</tg-emoji> TRON: {b['TRX']:.8f} TRX\n"
        f"<tg-emoji emoji-id=\"5409133571233319295\">☺️</tg-emoji> Bitcoin: {b['BTC']:.8f} BTC\n"
        f"<tg-emoji emoji-id=\"5406930321729948822\">☺️</tg-emoji> Ethereum: {b['ETH']:.8f} ETH\n"
        f"<tg-emoji emoji-id=\"5406581441536495663\">🐶</tg-emoji> Dogecoin: {b['DOGE']:.8f} DOGE\n"
        f"<tg-emoji emoji-id=\"5407128573125366746\">☺️</tg-emoji> Litecoin: {b['LTC']:.8f} LTC\n"
        f"<tg-emoji emoji-id=\"5406671889252781489\">☺️</tg-emoji> Binance Coin: {b['BNB']:.8f} BNB\n"
        f"<tg-emoji emoji-id=\"5406575600380974539\">☺️</tg-emoji> USD Coin: {b['USDC']:.8f} USDC\n"
        f"<tg-emoji emoji-id=\"5407080001340215945\">😊</tg-emoji> Tether Gold: {b['XAUT']:.8f} XAUT\n\n"
        f"≈ {total_btc:.8f} BTC"
    )
    return text

# Клавиатура главного меню
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Кошелёк", callback_data="wallet", icon_custom_emoji_id="5310191758255099001"),
        InlineKeyboardButton(text="Обмен", callback_data="exchange", icon_custom_emoji_id="5361993818373655559")
    ],
    [
        InlineKeyboardButton(text="P2P", callback_data="p2p", icon_custom_emoji_id="5312419154064607942"),
        InlineKeyboardButton(text="Биржа", callback_data="market", icon_custom_emoji_id="5312212278374861302")
    ],
    [
        InlineKeyboardButton(text="Чеки", callback_data="checks", icon_custom_emoji_id="5311998535032409760"),
        InlineKeyboardButton(text="Счета", callback_data="invoices", icon_custom_emoji_id="5312043357311111246")
    ],
    [
        InlineKeyboardButton(text="Crypto Pay", callback_data="cryptopay", icon_custom_emoji_id="5361543877599724417"),
        InlineKeyboardButton(text="Розыгрыши", callback_data="giveaways", icon_custom_emoji_id="5361986358015463601")
    ],
    [
        InlineKeyboardButton(text="Подписки", callback_data="subscriptions", icon_custom_emoji_id="5312161417372142817"),
        InlineKeyboardButton(text="Настройки", callback_data="settings", icon_custom_emoji_id="5309974037772928528")
    ]
])

# Клавиатура кошелька
wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Пополнить", callback_data="deposit"),
        InlineKeyboardButton(text="Вывести", callback_data="withdraw")
    ],
    [
        InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")
    ]
])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    text = (
        "<tg-emoji emoji-id=\"5361914370068613491\">👛</tg-emoji> "
        "<a href=\"https://t.me/Crypto_Bot_RUSSIA/6\">Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href=\"https://t.me/Crypto_Bot_RUSSIA\">наш канал</a> и вступайте в\n"
        "<a href=\"https://t.me/Crypto_Bot_Russian_Chat\">наш чат</a>."
    )
    
    await message.answer(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )

@dp.callback_query(lambda c: lambda c: c.data == "wallet")
async def open_wallet(callback: types.CallbackQuery):
    await callback.message.edit_text(
        get_wallet_text(callback.from_user.id),
        parse_mode='HTML',
        reply_markup=wallet_keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
     text = (
        "<tg-emoji emoji-id=\"5361914370068613491\">👛</tg-emoji> "
        "<a href=\"https://t.me/Crypto_Bot_RUSSIA/6\">Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href=\"https://t.me/Crypto_Bot_RUSSIA\">наш канал</a> и вступайте в\n"
        "<a href=\"https://t.me/Crypto_Bot_Russian_Chat\">наш чат</a>."
    )
    
    await callback.message.edit_text(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )
    await callback.answer()

# Заглушки для остальных кнопок
@dp.callback_query(lambda c: c.data in ["exchange", "p2p", "market", "checks", "invoices", "cryptopay", "giveaways", "subscriptions", "settings", "deposit", "withdraw"])
async def placeholder_callback(callback: types.CallbackQuery):
    await callback.answer(f"Раздел '{callback.data}' пока в разработке", show_alert=True)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
