import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8"
CHANNEL_LINK = "https://t.me/project_ImpassL"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кастомные эмоджи (ID)
EMOJI_ROCKET       = "5258332798409783582"
EMOJI_WALLET       = "5379639755933781390"
EMOJI_DEPOSIT      = "5222153011815553801"
EMOJI_WITHDRAW     = "5219926964625779761"
EMOJI_EXCHANGE     = "5379733369040964216"
EMOJI_SWAP         = "5222200204916201346"
EMOJI_BUY_SELL     = "5377660282816468683"
EMOJI_P2P          = "5380002586181015442"
EMOJI_QR           = "5361580286037499439"
EMOJI_SHOW_MORE    = "5379800318991177888"

# Эмоджи для экрана кошелька
EMOJI_COIN_USDT    = "5413877074848932790"
EMOJI_COIN_GRAM    = "5294028881492226080"
EMOJI_COIN_CES     = "5247162782473808472"
EMOJI_COIN_XROCK   = "5287770667465337224"
EMOJI_COIN_USDC    = "5453937927035840798"
EMOJI_COIN_SOL     = "5433727851050329182"
EMOJI_COIN_ETH     = "5453866639168658609"
EMOJI_COIN_TRX     = "5453889668783303273"
EMOJI_COIN_BTC     = "5454111585448517733"

# Обычные эмодзи для кнопок кошелька (где нет премиум)
EMOJI_TRANSFER     = "🔄" 
EMOJI_SECURITY     = "🔗"


# ===== ЛОГИКА БАЛАНСОВ (ЗАГЛУШКА) =====
# Здесь ты потом подключишь реальную базу данных или API
def get_user_balance(user_id: int):
    """Возвращает словарь с балансами пользователя."""
    # ПОКА ЧТО У ВСЕХ НУЛИ. Когда сделаешь систему депозитов - меняй эту функцию
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


async def build_wallet_keyboard():
    """Клавиатура для экрана кошелька."""
    builder = InlineKeyboardBuilder()
    
    # Строка 1: Пополнение | Вывод
    builder.row(
        InlineKeyboardButton(text="Пополнение", callback_data="deposit", icon_custom_emoji_id=EMOJI_DEPOSIT),
        InlineKeyboardButton(text="Вывод",      callback_data="withdraw", icon_custom_emoji_id=EMOJI_WITHDRAW),
    )
    
    # Строка 2: Общий баланс (заглушка, можно убрать или сделать инфо-кнопкой)
    builder.row(InlineKeyboardButton(text="Общий баланс", callback_data="total_balance"))
    
    # Строка 3: Перевод между балансами
    builder.row(InlineKeyboardButton(text=f"{EMOJI_TRANSFER} Перевод между балансами", callback_data="transfer"))
    
    # Строка 4: Повысить безопасность
    builder.row(InlineKeyboardButton(text=f"{EMOJI_SECURITY} Повысить безопасность", callback_data="security"))
    
    # Строка 5: Отображение балансов
    builder.row(InlineKeyboardButton(text="Отображение балансов", callback_data="display_settings", icon_custom_emoji_id=EMOJI_WALLET))
    
    # Строка 7: Назад
    builder.row(InlineKeyboardButton(text="‹ Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        f'<tg-emoji emoji-id=\"5258332798409783582\">🚀</tg-emoji> xRocket — это бот-кошелёк для\n'
        'получения, отправки, покупки и хранения\n'
        'криптовалюты в Telegram.\n\n'
        f'Обо всех возможностях читай в <a href="{CHANNEL_LINK}">официальном канале</a>'
    )

    # Главное меню
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Кошелёк · 0.00 $", callback_data="open_wallet", icon_custom_emoji_id=EMOJI_WALLET))
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

    await message.answer(text=welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    try:
        await message.delete()
    except Exception:
        pass


@dp.callback_query(lambda c: c.data == "open_wallet")
async def open_wallet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    
    # Форматирование USDT: если 0 - без скобок, если > 0 - со скобками
    usdt_display = f"{balance['usdt']:.2f}"
    if balance['usdt'] > 0:
        usdt_line = f'<tg-emoji emoji-id="{EMOJI_COIN_USDT}"></tg-emoji> USDT: {usdt_display} (${balance["usdt"]:.2f})'
    else:
        usdt_line = f'<tg-emoji emoji-id="{EMOJI_COIN_USDT}"></tg-emoji> USDT: {usdt_display}'

    # Остальные монеты всегда без скобок (по ТЗ)
    lines = [
        f'<b><tg-emoji emoji-id="{EMOJI_WALLET}"></tg-emoji> Мой кошелек</b>',
        '',
        usdt_line,
        f'<tg-emoji emoji-id="{EMOJI_COIN_GRAM}"></tg-emoji> GRAM: {balance["gram"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_CES}"></tg-emoji> CES: {balance["ces"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_XROCK}"></tg-emoji> XROCK: {balance["xrock"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_USDC}"></tg-emoji> USDC: {balance["usdc"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_SOL}"></tg-emoji> SOL: {balance["sol"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_ETH}"></tg-emoji> ETH: {balance["eth"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_TRX}"></tg-emoji> TRX: {balance["trx"]:.2f}',
        f'<tg-emoji emoji-id="{EMOJI_COIN_BTC}"></tg-emoji> BTC: {balance["btc"]:.2f}',
        '',
        f'≈ {balance["total_usd"]:.2f} $',
        '',
        'Чтобы настроить отображение, нажми на кнопку "Отображение балансов".'
    ]
    
    wallet_text = '\n'.join(lines)
    keyboard = await build_wallet_keyboard()
    
    # Удаляем предыдущее сообщение (меню) и отправляем кошелек
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text=wallet_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    # Возврат в главное меню
    welcome_text = (
        f'<tg-emoji emoji-id="{EMOJI_ROCKET}"></tg-emoji> xRocket — это бот-кошелёк для\n'
        'получения, отправки, покупки и хранения\n'
        'криптовалюты в Telegram.\n\n'
        f'Обо всех возможностях читай в <a href="{CHANNEL_LINK}">официальном канале</a>'
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Кошелёк · 0.00 $", callback_data="open_wallet", icon_custom_emoji_id=EMOJI_WALLET))
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
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text=welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# Заглушки для остальных кнопок, чтобы бот не падал
@dp.callback_query(lambda c: True)
async def dummy_callback(callback: types.CallbackQuery):
    await callback.answer("Раздел в разработке 🚧", show_alert=True)


async def main():
    print("✅ Бот запущен! Отправьте /start для проверки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
