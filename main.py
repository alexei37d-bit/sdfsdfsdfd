import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Токен бота
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Текст приветствия
    text = (
        "<tg-emoji emoji-id=\"5361914370068613491\">👛</tg-emoji> "
        "<a href=\"https://t.me/CryptoBotRU/14\">Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "<a href=\"https://t.me/CryptoBotRU/228\">отправляйте</a> и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href=\"https://t.me/CryptoBotRU\">наш канал</a> и вступайте в\n"
        "<a href=\"https://t.me/CryptoBotRussian\">наш чат</a>."
    )
    
    # Создаем клавиатуру с кастомными эмодзи
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
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
    
    await message.answer(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=keyboard
    )

# Обработчик нажатий на кнопки (пока просто заглушка)
@dp.callback_query(lambda c: True)
async def handle_callback(callback: types.CallbackQuery):
    await callback.answer(f"Вы нажали: {callback.data}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
