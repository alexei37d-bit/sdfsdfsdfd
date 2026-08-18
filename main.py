import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8"
CHANNEL_LINK = "https://t.me/project_ImpassL"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кастомные эмоджи (ID) - ИСПОЛЬЗУЮТСЯ ТОЛЬКО В КНОПКАХ
EMOJI_ROCKET       =  "5258332798409783582"
EMOJI_WALLET       =  "5379639755933781390"
EMOJI_DEPOSIT      =  "5222153011815553801"
EMOJI_WITHDRAW     =  "5219926964625779761"
EMOJI_EXCHANGE     =  "5379733369040964216"
EMOJI_SWAP         =  "5222200204916201346"
EMOJI_BUY_SELL     =  "5377660282816468683"
EMOJI_P2P          =  "5380002586181015442"
EMOJI_QR           =  "5361580286037499439"
EMOJI_SHOW_MORE    =  "5379800318991177888"

# Обычные эмодзи для кнопок кошелька (где нет премиум)
EMOJI_TRANSFER     = "🔄"
EMOJI_SECURITY     = "🔗"

# Ссылки на официальные сайты криптовалют
COIN_LINKS = {
    "USDT": "https://tether.to/",
    "GRAM": "https://ton.org/",
    "CES": "#", 
    "XROCK": "#", 
    "USDC": "https://www.centre.io/usdc",
    "SOL": "https://solana.com/",
    "ETH": "https://ethereum.org/",
    "TRX": "https://tron.network/",
    "BTC": "https://bitcoin.org/"
}

# ===== ЛОГИКА БАЛАНСОВ =====
def get_user_balance(user_id: int):
    """Возвращает словарь с балансами пользователя."""
    # Здесь потом будет запрос к БД. Сейчас заглушка.
    return {
        "usdt": 0.00,
        "gram": 0.00,
        "ces": 0.00,
        "xrock": 0.00,
        "usdc": 0.00,
        "sol": 0.00,
        "eth": 0.00,
        "trx": 0.00,
        "btc": 0.00,
        "total_usd": 0.00
    }

def format_crypto_amount(amount):
    """Форматирует число: убирает лишние нули, оставляет до 8 знаков."""
    if amount == 0:
        return "0"
    # Форматируем до 8 знаков, затем убираем trailing zeros
    formatted = f"{amount:.8f}"
    return formatted.rstrip('0').rstrip('.')

async def build_wallet_keyboard():
    """Клавиатура для экрана кошелька."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Пополнение", callback_data="deposit", icon_custom_emoji_id=EMOJI_DEPOSIT),
        InlineKeyboardButton(text="Вывод",      callback_data="withdraw", icon_custom_emoji_id=EMOJI_WITHDRAW),
    )
    builder.row(InlineKeyboardButton(text="Общий баланс", callback_data="total_balance"))
    builder.row(InlineKeyboardButton(text=f"{EMOJI_TRANSFER} Перевод между балансами", callback_data="transfer"))
    builder.row(InlineKeyboardButton(text=f"{EMOJI_SECURITY} Повысить безопасность", callback_data="security"))
    builder.row(InlineKeyboardButton(text="Отображение балансов", callback_data="display_settings", icon_custom_emoji_id=EMOJI_WALLET))
    builder.row(InlineKeyboardButton(text="‹ Назад", callback_data="back_to_menu"))
    return builder.as_markup()

async def build_main_menu_keyboard(total_balance: float):
    """Клавиатура главного меню с динамическим балансом."""
    builder = InlineKeyboardBuilder()
    # Показываем сумму в кнопке
    balance_str = format_crypto_amount(total_balance)
    builder.row(InlineKeyboardButton(text=f"Кошелёк · {balance_str} $", callback_data="open_wallet", icon_custom_emoji_id=EMOJI_WALLET))
    
    builder.row(
        InlineKeyboardButton(text="Пополнить", callback_data="deposit", icon_custom_emoji_id=EMOJI_DEPOSIT),
        InlineKeyboardButton(text="Вывести",   callback_data="withdraw", icon_custom_emoji_id=EMOJI_WITHDRAW),
    )
    builder.row(
        InlineKeyboardButton(text="Биржа",     callback_data="exchange", icon_custom_emoji_id=EMOJI_EXCHANGE),
        InlineKeyboardButton(text="Обмен",     callback_data="swap",     icon_custom_emoji_id=EMOJI_SWAP),
    )
    builder.row(
        InlineKeyboardButton(text="Купить/Продать", callback_data="buy_sell", icon_custom_emoji_id=EMOJI_BUY_SELL),
        InlineKeyboardButton(text="P2P Маркет",     callback_data="p2p",      icon_custom_emoji_id=EMOJI_P2P),
    )
    builder.row(
        InlineKeyboardButton(text="Оплатить по QR", callback_data="qr_pay",    icon_custom_emoji_id=EMOJI_QR),
        InlineKeyboardButton(text="Показать ещё",   callback_data="show_more", icon_custom_emoji_id=EMOJI_SHOW_MORE),
    )
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    welcome_text = (
        f'<tg-emoji emoji-id="{EMOJI_ROCKET}"></tg-emoji> xRocket — это бот-кошелёк для\n'
        'получения, отправки, покупки и хранения\n'
        'криптовалюты в Telegram.\n\n'
        f'Обо всех возможностях читай в <a href="{CHANNEL_LINK}">официальном канале</a>'
    )
    
    keyboard = await build_main_menu_keyboard(balance['total_usd'])
    await message.answer(text=welcome_text, reply_markup=keyboard, parse_mode="HTML")
    try:
        await message.delete()
    except Exception:
        pass

@dp.callback_query(lambda c: c.data == "open_wallet")
async def open_wallet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    
    # Функция для создания строки монеты
    def create_coin_line(emoji_id, symbol, amount):
        formatted_amt = format_crypto_amount(amount)
        link = COIN_LINKS.get(symbol, "#")
        
        # Если баланс больше 0, добавляем ($value)
        if amount > 0:
            # Для простоты пока считаем 1 к 1, тут можно добавить реальный курс
            usd_val = format_crypto_amount(amount) 
            return f'<tg-emoji emoji-id="{emoji_id}"></tg-emoji> <a href="{link}">{symbol}</a>: {formatted_amt} ({usd_val}$)'
        else:
            return f'<tg-emoji emoji-id="{emoji_id}"></tg-emoji> <a href="{link}">{symbol}</a>: {formatted_amt}'

    lines = [
        f'<b><tg-emoji emoji-id=\"5379639755933781390\">👛</tg-emoji> Мой кошелек</b>',
        '',
         <tg-emoji emoji-id=\"5413877074848932790\">🪙</tg-emoji> "USDT", balance['usdt']),
         <tg-emoji emoji-id=\"5294028881492226080\">🪙</tg-emoji> "GRAM", balance['gram']),
         <tg-emoji emoji-id=\"5247162782473808472\">🪙</tg-emoji> "CES", balance['ces']),
         <tg-emoji emoji-id=\"5287770667465337224\">🪙</tg-emoji> "XROCK", balance['xrock']),
         <tg-emoji emoji-id=\"5453937927035840798\">🪙</tg-emoji> "USDC", balance['usdc']),
         <tg-emoji emoji-id=\"5433727851050329182\">🪙</tg-emoji> "SOL", balance['sol']),
         <tg-emoji emoji-id=\"5453866639168658609\">🪙</tg-emoji> "ETH", balance['eth']),
         <tg-emoji emoji-id=\"5453889668783303273\">🪙</tg-emoji> "TRX", balance['trx']),
         <tg-emoji emoji-id=\"5454111585448517733\">🪙</tg-emoji> "BTC", balance['btc']),
        '',
        f'≈ {format_crypto_amount(balance["total_usd"])} $',
        '',
        'Чтобы настроить отображение, нажми на кнопку "Отображение балансов".'
    ]
    
    wallet_text = '\n'.join(lines)
    keyboard = await build_wallet_keyboard()
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(text=wallet_text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    
    welcome_text = (
        f'<tg-emoji emoji-id="{EMOJI_ROCKET}"></tg-emoji> xRocket — это бот-кошелёк для\n'
        'получения, отправки, покупки и хранения\n'
        'криптовалюты в Telegram.\n\n'
        f'Обо всех возможностях читай в <a href="{CHANNEL_LINK}">официальном канале</a>'
    )
    
    keyboard = await build_main_menu_keyboard(balance['total_usd'])
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(text=welcome_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# Заглушки для остальных кнопок
@dp.callback_query(lambda c: True)
async def dummy_callback(callback: types.CallbackQuery):
    await callback.answer("Раздел в разработке 🚧", show_alert=True)

async def main():
    print("✅ Бот запущен! Отправьте /start для проверки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
