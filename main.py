import telebot
from telebot import types

BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "<tg-emoji emoji-id=\"5361914370068613491\">👛</tg-emoji> "
        "<a href=\"https://t.me/CryptoBotRU/14\">Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "<a href=\"https://t.me/CryptoBotRU/228\">отправляйте</a> и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href=\"https://t.me/CryptoBotRU\">наш канал</a> и вступайте в\n"
        "<a href=\"https://t.me/CryptoBotRussian\">наш чат</a>."
    )
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='HTML',
        disable_web_page_preview=True
    )

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
