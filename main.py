import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8"
CHANNEL_LINK = "https://t.me/project_ImpassL"

# Создаем бота и диспетчер ДО всех функций
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кастомные эмоджи (ID)
EMOJI_ROCKET    = "5258332798409783582"
EMOJI_WALLET    = "5379639755933781390"
EMOJI_DEPOSIT   = "5222153011815553801"
EMOJI_WITHDRAW  = "5219926964625779761"
EMOJI_EXCHANGE  = "5379733369040964216"
EMOJI_SWAP      = "5222200204916201346"
EMOJI_BUY_SELL  = "5377660282816468683"
EMOJI_P2P       = "5380002586181015442"
EMOJI_QR        = "5361580286037499439"
EMOJI_SHOW_MORE = "5379800318991177888"


async def build_keyboard():
    """Собирает клавиатуру с кастомными эмоджи."""
    builder = InlineKeyboardBuilder()

    # Строка 1 — Кошелёк
    builder.row(InlineKeyboardButton(
        text="Кошелёк · 0.01 $",
        callback_data="wallet",
        custom_emoji_id=EMOJI_WALLET
    ))

    # Строка 2 — Пополнить | Вывести
    builder.row(
        InlineKeyboardButton(text="Пополнить", callback_data="deposit", custom_emoji_id=EMOJI_DEPOSIT),
        InlineKeyboardButton(text="Вывести",   callback_data="withdraw", custom_emoji_id=EMOJI_WITHDRAW),
    )

    # Строка 3 — Биржа | Обмен
    builder.row(
        InlineKeyboardButton(text="Биржа",     callback_data="exchange", custom_emoji_id=EMOJI_EXCHANGE),
        InlineKeyboardButton(text="Обмен",     callback_data="swap",     custom_emoji_id=EMOJI_SWAP),
    )

    # Строка 4 — Купить/Продать | P2P Маркет
    builder.row(
        InlineKeyboardButton(text="Купить/Продать", callback_data="buy_sell", custom_emoji_id=EMOJI_BUY_SELL),
        InlineKeyboardButton(text="P2P Маркет",     callback_data="p2p",      custom_emoji_id=EMOJI_P2P),
    )

    # Строка 5 — Оплатить по QR | Показать ещё
    builder.row(
        InlineKeyboardButton(text="Оплатить по QR", callback_data="qr_pay",    custom_emoji_id=EMOJI_QR),
        InlineKeyboardButton(text="Показать ещё",   callback_data="show_more", custom_emoji_id=EMOJI_SHOW_MORE),
    )

    # Строка 6 — Открыть приложение (Web App)
    builder.row(InlineKeyboardButton(
        text="Открыть приложение",
        web_app=WebAppInfo(url="https://t.me/xRocketBot/app"),
        custom_emoji_id=EMOJI_ROCKET,
    ))

    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Удаляем сообщение пользователя /start
    try:
        await message.delete()
    except Exception:
        pass

    # Формируем текст приветствия (используем одинарные кавычки для href)
    welcome_text = (
        '<tg-emoji emoji-id="5258332798409783582"></tg-emoji> xRocket — это бот-кошелёк для\n'
        'получения, отправки, покупки и хранения\n'
        'криптовалюты в Telegram.\n\n'
        f'Обо всех возможностях читай в <a href="{CHANNEL_LINK}">официальном канале</a>'
    )

    keyboard = await build_keyboard()

    await message.answer(
        text=welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def main():
    print("✅ Бот запущен! Отправьте /start для проверки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
