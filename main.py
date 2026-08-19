import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Токен бота
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Имитация базы данных балансов (исправлены ключи: убраны лишние пробелы)
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

# Ссылки на официальные сайты криптовалют (исправлены ключи и URL)
crypto_websites = {
    "USDT": "https://tether.to",
    "GRAM": "https://ton.org",
    "SOL": "https://solana.com",
    "TRX": "https://tron.network",
    "BTC": "https://bitcoin.org",
    "ETH": "https://ethereum.org",
    "DOGE": "https://dogecoin.com",
    "LTC": "https://litecoin.org",
    "BNB": "https://www.bnbchain.org",
    "USDC": "https://www.centre.io/usdc",
    "XAUT": "https://tether.to/en/tether-gold/"
}

# Функция для форматирования баланса
def format_balance(value):
    """Форматирует баланс: если 0 - показывает '0', иначе показывает с точностью"""
    if value == 0:
        return "0"
    # Убираем лишние нули в конце
    formatted = f"{value:.8f}".rstrip('0').rstrip('.')
    return formatted

# Функция для получения текста баланса
def get_wallet_text(user_id: int):
    # Для примера берем баланс из словаря
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
    
    # Форматируем общий баланс
    total_btc_formatted = format_balance(total_btc)
    
    # Используем одинарные кавычки внутри f-строки для HTML атрибутов
    text = (
        f"<b><tg-emoji emoji-id='5310191758255099001'>👛</tg-emoji> Кошелек</b>\n\n"
        f"<tg-emoji emoji-id='5406841020769936275'>☺️</tg-emoji> <a href='{crypto_websites['USDT']}'>Tether</a>: {format_balance(b['USDT'])} USDT\n\n"
        f"<tg-emoji emoji-id='5318901904686754959'>🙂</tg-emoji> <a href='{crypto_websites['GRAM']}'>Gram</a>: {format_balance(b['GRAM'])} GRAM\n\n"
        f"<tg-emoji emoji-id='5407016676342401484'>☺️</tg-emoji> <a href='{crypto_websites['SOL']}'>Solana</a>: {format_balance(b['SOL'])} SOL\n\n"
        f"<tg-emoji emoji-id='5406978786140918829'>☺️</tg-emoji> <a href='{crypto_websites['TRX']}'>TRON</a>: {format_balance(b['TRX'])} TRX\n\n"
        f"<tg-emoji emoji-id='5409133571233319295'>☺️</tg-emoji> <a href='{crypto_websites['BTC']}'>Bitcoin</a>: {format_balance(b['BTC'])} BTC\n\n"
        f"<tg-emoji emoji-id='5406930321729948822'>☺️</tg-emoji> <a href='{crypto_websites['ETH']}'>Ethereum</a>: {format_balance(b['ETH'])} ETH\n\n"
        f"<tg-emoji emoji-id='5406581441536495663'>🐶</tg-emoji> <a href='{crypto_websites['DOGE']}'>Dogecoin</a>: {format_balance(b['DOGE'])} DOGE\n\n"
        f"<tg-emoji emoji-id='5407128573125366746'>☺️</tg-emoji> <a href='{crypto_websites['LTC']}'>Litecoin</a>: {format_balance(b['LTC'])} LTC\n\n"
        f"<tg-emoji emoji-id='5406671889252781489'>☺️</tg-emoji> <a href='{crypto_websites['BNB']}'>Binance Coin</a>: {format_balance(b['BNB'])} BNB\n\n"
        f"<tg-emoji emoji-id='5406575600380974539'>☺️</tg-emoji> <a href='{crypto_websites['USDC']}'>USD Coin</a>: {format_balance(b['USDC'])} USDC\n\n"
        f"<tg-emoji emoji-id='5407080001340215945'>😊</tg-emoji> <a href='{crypto_websites['XAUT']}'>Tether Gold</a>: {format_balance(b['XAUT'])} XAUT\n\n"
        f"≈ {total_btc_formatted} BTC"
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
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji>    "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/1'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.  "
    )
    await message.answer(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )

@dp.callback_query(lambda c: c.data == "wallet")
async def open_wallet(callback: types.CallbackQuery):
    await callback.message.edit_text(
        get_wallet_text(callback.from_user.id),
        parse_mode='HTML',
        disable_web_page_preview=True,  # Скрывает предпросмотр ссылок
        reply_markup=wallet_keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    text = (
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji>    "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/1'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.  "
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
