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

# Кастомные эмоджи (ID) для кнопок меню
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

# Эмоджи для списка монет (🪙)
COIN_EMOJI_ID = "5246858196278075452" 

# Данные всех монет (Название, Тикер, Ссылка)
# Разбиты на страницы по 10 штук, чтобы соответствовать скриншотам
ALL_COINS = [
    # Страница 1
    {"name": "USDT", "ticker": "USDT", "link": "https://tether.to"},
    {"name": "GRAM", "ticker": "GRAM", "link": "https://ton.org"},
    {"name": "CES", "ticker": "CES", "link": "https://cescoin.io"},
    {"name": "XROCK", "ticker": "XROCK", "link": "https://xrocket.app"},
    {"name": "USDC", "ticker": "USDC", "link": "https://www.circle.com/usdc"},
    {"name": "SOL", "ticker": "SOL", "link": "https://solana.com"},
    {"name": "ETH", "ticker": "ETH", "link": "https://ethereum.org"},
    {"name": "TRX", "ticker": "TRX", "link": "https://tron.network"},
    {"name": "BTC", "ticker": "BTC", "link": "https://bitcoin.org"},
    {"name": "BNB", "ticker": "BNB", "link": "https://www.binance.com/en/bnb"},
    
    # Страница 2
    {"name": "XAUT", "ticker": "XAUT", "link": "https://www.tethergold.com"},
    {"name": "EVAA", "ticker": "EVAA", "link": "https://evaa.finance"},
    {"name": "DFC", "ticker": "DFC", "link": "https://coinmarketcap.com/currencies/defi-coin/"},
    {"name": "STBL", "ticker": "STBL", "link": "https://coinmarketcap.com/currencies/stable-token/"},
    {"name": "NOT", "ticker": "NOT", "link": "https://notcoin.world"},
    {"name": "JETTON", "ticker": "JETTON", "link": "https://coinmarketcap.com/currencies/jetton/"},
    {"name": "WEB3", "ticker": "WEB3", "link": "https://coinmarketcap.com/currencies/web3/"},
    {"name": "HYDRA", "ticker": "HYDRA", "link": "https://hydrachain.org"},
    {"name": "GEMSTON", "ticker": "GEMSTON", "link": "https://coinmarketcap.com/currencies/gemston/"},
    {"name": "GRBS", "ticker": "GRBS", "link": "https://coinmarketcap.com/currencies/grbs/"},

    # Страница 3
    {"name": "VIRUS", "ticker": "VIRUS", "link": "https://coinmarketcap.com/currencies/virus/"},
    {"name": "CATS", "ticker": "CATS", "link": "https://catsgang.app"},
    {"name": "ALENKA", "ticker": "ALENKA", "link": "https://coinmarketcap.com/currencies/alanka/"},
    {"name": "OPEN", "ticker": "OPEN", "link": "https://opentensor.tech"},
    {"name": "ANON", "ticker": "ANON", "link": "https://coinmarketcap.com/currencies/anon/"},
    {"name": "GRC", "ticker": "GRC", "link": "https://gridcoin.us"},
    {"name": "CATI", "ticker": "CATI", "link": "https://cati.network"},
    {"name": "BOLT", "ticker": "BOLT", "link": "https://bolt.mobi"},
    {"name": "DUREV", "ticker": "DUREV", "link": "https://coinmarketcap.com/currencies/durev/"},
    {"name": "MAJOR", "ticker": "MAJOR", "link": "https://major.bot"},

    # Страница 4
    {"name": "FID", "ticker": "FID", "link": "https://coinmarketcap.com/currencies/fid/"},
    {"name": "STON", "ticker": "STON", "link": "https://ston.fi"},
    {"name": "1MBABYDOGE", "ticker": "1MBABYDOGE", "link": "https://babydoge.com"},
    {"name": "DUST", "ticker": "DUST", "link": "https://dustprotocol.org"},
    {"name": "WOOF", "ticker": "WOOF", "link": "https://woofy.finance"},
    {"name": "DHD", "ticker": "DHD", "link": "https://coinmarketcap.com/currencies/dhd/"},
    {"name": "JVT", "ticker": "JVT", "link": "https://jetvault.io"},
    {"name": "MRDN", "ticker": "MRDN", "link": "https://coinmarketcap.com/currencies/mardan/"},
    {"name": "tsTON", "ticker": "tsTON", "link": "https://ton.org"},
    {"name": "BUILD", "ticker": "BUILD", "link": "https://coinmarketcap.com/currencies/build/"},

    # Страница 5
    {"name": "stXP", "ticker": "stXP", "link": "https://coinmarketcap.com/currencies/stxp/"},
    {"name": "SP", "ticker": "SP", "link": "https://coinmarketcap.com/currencies/sp/"},
    {"name": "TNX", "ticker": "TNX", "link": "https://coinmarketcap.com/currencies/tnx/"},
    {"name": "MELANIA", "ticker": "MELANIA", "link": "https://coinmarketcap.com/currencies/melania-meme/"},
    {"name": "GGT", "ticker": "GGT", "link": "https://coinmarketcap.com/currencies/ggt/"},
    {"name": "TRUMP", "ticker": "TRUMP", "link": "https://coinmarketcap.com/currencies/trump/"},
    {"name": "STORM", "ticker": "STORM", "link": "https://storm.trade"},
    {"name": "DOGS", "ticker": "DOGS", "link": "https://dogs.community"},
    {"name": "TAKE", "ticker": "TAKE", "link": "https://coinmarketcap.com/currencies/take/"},
    {"name": "RAFF", "ticker": "RAFF", "link": "https://raffle.xyz"},

    # Страница 6
    {"name": "GRM", "ticker": "GRM", "link": "https://coinmarketcap.com/currencies/grm/"},
    {"name": "TONNEL", "ticker": "TONNEL", "link": "https://tonnel.network"},
    {"name": "PUNK", "ticker": "PUNK", "link": "https://cryptopunks.app"},
    {"name": "KINGY", "ticker": "KINGY", "link": "https://coinmarketcap.com/currencies/kingy/"},
]

# Функция получения баланса (всегда 0)
def get_balance(ticker):
    return 0.0

async def build_wallet_page(page_num: int):
    """Создает клавиатуру для конкретной страницы кошелька."""
    builder = InlineKeyboardBuilder()
    
    # Определяем диапазон монет для текущей страницы (по 10 на страницу)
    start_idx = (page_num - 1) * 10
    end_idx = start_idx + 10
    coins_on_page = ALL_COINS[start_idx:end_idx]
    
    # Добавляем кнопки монет
    for coin in coins_on_page:
        balance = get_balance(coin['ticker'])
        text = f"{coin['ticker']}: {balance} {coin['ticker']}"
        # Используем callback_data для открытия ссылки или информации
        builder.row(InlineKeyboardButton(text=text, url=coin['link']))

    # Пагинация (1 2 3 4 5 6 7)
    pagination_row = []
    total_pages = 7
    
    # Кнопка "Назад" (<)
    if page_num > 1:
        pagination_row.append(InlineKeyboardButton(text="‹", callback_data=f"wallet_page_{page_num-1}"))
    
    # Цифры страниц
    for i in range(1, total_pages + 1):
        if i == page_num:
            pagination_row.append(InlineKeyboardButton(text=f"•{i}•", callback_data="noop"))
        else:
            pagination_row.append(InlineKeyboardButton(text=str(i), callback_data=f"wallet_page_{i}"))
            
    # Кнопка "Вперед" (>)
    if page_num < total_pages:
        pagination_row.append(InlineKeyboardButton(text="›", callback_data=f"wallet_page_{page_num+1}"))
        
    builder.row(*pagination_row)

    # Нижние кнопки
    builder.row(
        InlineKeyboardButton(text="Пополнение", callback_data="deposit", icon_custom_emoji_id=EMOJI_DEPOSIT),
        InlineKeyboardButton(text="Вывод",      callback_data="withdraw", icon_custom_emoji_id=EMOJI_WITHDRAW),
    )
    builder.row(InlineKeyboardButton(text="Общий баланс", callback_data="total_balance"))
    
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        f'<tg-emoji emoji-id="{EMOJI_ROCKET}">🚀</tg-emoji> xRocket — это бот-кошелёк для\n'
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
    
    await message.answer(text=welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    try:
        await message.delete()
    except Exception:
        pass

@dp.callback_query(lambda c: c.data == "open_wallet")
async def open_wallet(callback: types.CallbackQuery):
    # Открываем сразу 1 страницу
    keyboard = await build_wallet_page(1)
    
    wallet_text = (
        f'<b><tg-emoji emoji-id="{EMOJI_WALLET}"></tg-emoji> Мой кошелёк</b>\n\n'
        f'≈ 0.01 $\n\n'
        'Чтобы настроить отображение, нажми на кнопку "Отображение балансов".'
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text=wallet_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("wallet_page_"))
async def switch_wallet_page(callback: types.CallbackQuery):
    page_num = int(callback.data.split("_")[2])
    keyboard = await build_wallet_page(page_num)
    
    wallet_text = (
        f'<b><tg-emoji emoji-id="{EMOJI_WALLET}">👛</tg-emoji> Мой кошелёк</b>\n\n'
        f'≈ 0.01 $\n\n'
        'Чтобы настроить отображение, нажми на кнопку "Отображение балансов".'
    )
    
    await callback.message.edit_text(text=wallet_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: True)
async def dummy_callback(callback: types.CallbackQuery):
    if callback.data != "noop":
        await callback.answer("Раздел в разработке 🚧", show_alert=True)
    else:
        await callback.answer()

async def main():
    print("✅ Бот запущен! Отправьте /start для проверки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
