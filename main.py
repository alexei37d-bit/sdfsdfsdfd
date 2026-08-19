import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный от @BotFather
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Формируем текст с inline-ссылками
    text = (
        "<tg-emoji emoji-id=\"5361914370068613491\">👛</tg-emoji> "
        "<a href=\"https://t.me/CryptoBotRU/14\">Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "<a href=\"https://t.me/CryptoBotRU/228\">отправляйте</a> и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href=\"https://t.me/CryptoBotRU\">наш канал</a> и вступайте в\n"
        "<a href=\"https://t.me/CryptoBotRussian\">наш чат</a>."
    )
    
    await message.answer(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
