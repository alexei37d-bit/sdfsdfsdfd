import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from database import Database

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# ID администраторов (ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ID)
ADMIN_IDS = [123456789, 987654321]  # <-- Впишите сюда ID админов через запятую

# ИСПРАВЛЕНО: Убраны пробелы в ключах!
crypto_websites = {
    "USDT": "https://tether.to", "GRAM": "https://ton.org", "SOL": "https://solana.com",
    "TRX": "https://tron.network", "BTC": "https://bitcoin.org", "ETH": "https://ethereum.org",
    "DOGE": "https://dogecoin.com", "LTC": "https://litecoin.org", "BNB": "https://www.bnbchain.org",
    "USDC": "https://www.centre.io/usdc", "XAUT": "https://tether.to/en/tether-gold/"
}

USD_RATES = {
    "USDT": 1.0, "USDC": 1.0, "BTC": 65000, "ETH": 3500, "SOL": 150,
    "GRAM": 0.007, "TRX": 0.12, "DOGE": 0.15, "LTC": 70, "BNB": 600, "XAUT": 2300
}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def format_balance(value):
    if value == 0: return "0"
    return f"{value:.8f}".rstrip('0').rstrip('.')

def get_usd_value(amount, currency):
    rate = USD_RATES.get(currency, 0)
    val = amount * rate
    if val < 0.01: return "< 0.01"
    return f"{val:.2f}"

async def generate_check_image(currency: str, amount: float):
    usd_val = get_usd_value(amount, currency)
    url = (
        f"https://imggen.send.tg/checks/image?"
        f"asset={currency}&asset_amount={amount}"
        f"&fiat=USD&fiat_amount={usd_val}"
        f"&main=asset&v4"
    )
    return url

# --- ТЕКСТЫ И КЛАВИАТУРЫ ---
def get_wallet_text(user_id: int):
    b = db.get_all_balances(user_id)
    if not b:
        b = {k: 0.0 for k in ["USDT", "GRAM", "SOL", "TRX", "BTC", "ETH", "DOGE", "LTC", "BNB", "USDC", "XAUT"]}
    
    total_btc = sum([
        b["USDT"]*0.00001, b["GRAM"]*0.0000001, b["SOL"]*0.002, b["TRX"]*0.000002,
        b["BTC"], b["ETH"]*0.03, b["DOGE"]*0.000001, b["LTC"]*0.001,
        b["BNB"]*0.005, b["USDC"]*0.00001, b["XAUT"]*0.03
    ])
    
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
        f"≈ {format_balance(total_btc)} BTC"
    )
    return text

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

wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пополнить", callback_data="deposit"), InlineKeyboardButton(text="Вывести", callback_data="withdraw")],
    [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")]
])

# --- FSM ДЛЯ ЧЕКОВ ---
class CheckCreation(StatesGroup):
    waiting_for_amount = State()
    selected_currency = State()

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    db.add_user(message.from_user.id)
    
    # ДОБАВЛЕНО: Начисление 100 USDT админам один раз при балансе 0
    if message.from_user.id in ADMIN_IDS:
        usdt_balance = db.get_balance(message.from_user.id, "USDT")
        if usdt_balance == 0:
            db.update_balance(message.from_user.id, "USDT", 100)
    
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("check_"):
        check_id = args[1].replace("check_", "")
        await activate_check_logic(message, check_id)
        return
    
    text = (
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/6'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.  "
    )
    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=main_keyboard)

@dp.callback_query(lambda c: c.data == "wallet")
async def open_wallet(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text(get_wallet_text(callback.from_user.id), parse_mode='HTML', disable_web_page_preview=True, reply_markup=wallet_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    text = (
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/6'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.  "
    )
    try:
        await callback.message.edit_text(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=main_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

# ================= СИСТЕМА ЧЕКОВ =================

@dp.callback_query(lambda c: c.data == "checks")
async def checks_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    active_checks = db.get_user_checks(user_id)
    
    text = (
        "Здесь вы можете создавать чек для мгновенной отправки криптовалюты любому пользователю.\n"
        "<a href='https://telegra.ph/Checks-Instruction'>Смотреть инструкцию ›</a>"
    )
    
    buttons = [
        [InlineKeyboardButton(text="Создать чек", callback_data="create_check_start")],
        [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")]
    ]
    
    if active_checks:
        buttons.insert(1, [InlineKeyboardButton(text=f"Активные чеки ({len(active_checks)})", callback_data="my_active_checks")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "create_check_start")
async def create_check_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balances = db.get_all_balances(user_id)
    
    available_currencies = []
    for curr, bal in balances.items():
        if curr == 'user_id': continue
        usd_val = bal * USD_RATES.get(curr, 0)
        if usd_val >= 0.02:
            available_currencies.append((curr, bal))
            
    if not available_currencies:
        text = "Недостаточно монет. Сумма одного чека не может быть меньше чем $0.02.\nСначала пополните баланс!"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад к чекам", callback_data="checks")]])
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        text = "Выберите криптовалюту для создания чека:"
        rows = []
        temp_row = []
        for curr, bal in available_currencies:
            btn_text = f"{curr} ({format_balance(bal)})"
            temp_row.append(InlineKeyboardButton(text=btn_text, callback_data=f"select_check_curr_{curr}"))
            if len(temp_row) == 2:
                rows.append(temp_row)
                temp_row = []
        if temp_row: rows.append(temp_row)
        rows.append([InlineKeyboardButton(text="‹ Назад к чекам", callback_data="checks")])
        kb = InlineKeyboardMarkup(inline_keyboard=rows)
        await callback.message.edit_text(text, reply_markup=kb)
        
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("select_check_curr_"))
async def select_check_currency_fsm(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[-1]
    await state.set_state(CheckCreation.waiting_for_amount)
    await state.update_data(selected_currency=currency)
    
    text = f"Пришлите сумму чека в {currency}.\nЕсли вы хотите создать мультичек, введите кратную вашему балансу сумму одной активации."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад", callback_data="checks")]])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@dp.message(CheckCreation.waiting_for_amount)
async def process_check_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency = data.get("selected_currency")
    
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        return
        
    min_amount_usd = 0.02
    current_usd = amount * USD_RATES.get(currency, 0)
    
    if current_usd < min_amount_usd:
        await message.answer(f"Минимальная сумма чека $0.02. Для {currency} это примерно {min_amount_usd / USD_RATES.get(currency, 1):.4f}.")
        return
        
    balance = db.get_balance(message.from_user.id, currency)
    if balance < amount:
        await message.answer("Недостаточно средств на балансе.")
        await state.clear()
        return
        
    db.update_balance(message.from_user.id, currency, -amount)
    
    check_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    db.create_check(check_id, message.from_user.id, currency, amount)
    
    img_url = await generate_check_image(currency, amount)
    usd_val = get_usd_value(amount, currency)
    
    caption = (
        f"<b>Чек</b>\n\n"
        f"Сумма: {amount} {currency} (${usd_val})\n\n"
        f"Любой может активировать этот чек.\n\n"
        f"Скопируйте ссылку, чтобы поделиться чеком:\n"
        f"<code>https://t.me/{bot.username}?start=check_{check_id}</code>\n\n"
        f"⚠️ Никогда не делайте скриншот вашего чека и не отправляйте его никому!"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Конвертировать в подарок", callback_data="convert_gift")],
        [InlineKeyboardButton(text="Поделиться чеком", switch_inline_query=check_id)],
        [InlineKeyboardButton(text="Показать QR-код", callback_data=f"show_qr_{check_id}")],
        [InlineKeyboardButton(text="Удалить чек", callback_data=f"delete_check_{check_id}")],
        [InlineKeyboardButton(text="‹ Назад к списку чеков", callback_data="my_active_checks")]
    ])
    
    await message.answer_photo(photo=img_url, caption=caption, parse_mode='HTML', reply_markup=kb)
    await state.clear()

@dp.callback_query(lambda c: c.data == "my_active_checks")
async def my_active_checks(callback: types.CallbackQuery):
    checks = db.get_user_checks(callback.from_user.id)
    if not checks:
        await callback.answer("У вас нет активных чеков", show_alert=True)
        return
        
    rows = []
    for check in checks[:10]:
        usd_val = get_usd_value(check['amount'], check['currency'])
        btn_text = f"{check['currency']} {check['amount']} (${usd_val})"
        rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"manage_check_{check['id']}")])
    rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="checks")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await callback.message.edit_text("Ваши активные чеки:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("manage_check_"))
async def manage_check(callback: types.CallbackQuery):
    check_id = callback.data.split("_")[-1]
    check = db.get_check(check_id)
    
    if not check or check['creator_id'] != callback.from_user.id:
        await callback.answer("Чек не найден", show_alert=True)
        return
        
    img_url = await generate_check_image(check['currency'], check['amount'])
    usd_val = get_usd_value(check['amount'], check['currency'])
    
    caption = (
        f"<b>Чек</b>\n\n"
        f"Сумма: {check['amount']} {check['currency']} (${usd_val})\n\n"
        f"Ссылка: <code>https://t.me/{bot.username}?start=check_{check_id}</code>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться чеком", switch_inline_query=check_id)],
        [InlineKeyboardButton(text="Удалить чек", callback_data=f"delete_check_{check_id}")],
        [InlineKeyboardButton(text="‹ Назад к списку чеков", callback_data="my_active_checks")]
    ])
    
    try:
        await callback.message.edit_media(media=InputMediaPhoto(media=img_url, caption=caption, parse_mode='HTML'), reply_markup=kb)
    except Exception:
        await callback.message.edit_text(caption, parse_mode='HTML', reply_markup=kb)
        
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("delete_check_"))
async def delete_check(callback: types.CallbackQuery):
    check_id = callback.data.split("_")[-1]
    check = db.get_check(check_id)
    
    if check and check['creator_id'] == callback.from_user.id:
        db.delete_check(check_id, callback.from_user.id)
        db.update_balance(callback.from_user.id, check['currency'], check['amount'])
        await callback.message.delete()
        await callback.answer("Чек удален. Средства возвращены.", show_alert=True)
    else:
        await callback.answer("Ошибка или чек уже удален", show_alert=True)

async def activate_check_logic(message: types.Message, check_id: str):
    check = db.get_check(check_id)
    if not check or not check['is_active']:
        await message.answer("Чек недействителен.")
        return
        
    activator_id = message.from_user.id
    if activator_id == check['creator_id']:
        await message.answer("Это ваш чек.")
        return
        
    db.update_balance(activator_id, check['currency'], check['amount'])
    db.activate_check(check_id, activator_id)
    
    usd_val = get_usd_value(check['amount'], check['currency'])
    
    # ДОБАВЛЕНО: Кнопка "Открыть кошелек"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть кошелек", callback_data="wallet")]
    ])
    
    await message.answer(
        f"<tg-emoji emoji-id='5312043357311111246'>📥</tg-emoji> Вы получили "
        f"<b>{check['amount']} {check['currency']}</b> (<b>${usd_val}</b>)",
        parse_mode='HTML',
        reply_markup=kb  # Кнопка остается навсегда
    )
    
    creator_id = check['creator_id']
    notify_text = (
        f"<tg-emoji emoji-id='5311998535032409760'>🎁</tg-emoji> "
        f"<a href='tg://user?id={activator_id}'>{message.from_user.first_name}</a> активировал(а) ваш чек "
        f"и получил(а) <b>{check['amount']} {check['currency']}</b> (<b>${usd_val}</b>)"
    )
    try:
        await bot.send_message(creator_id, notify_text, parse_mode='HTML')
    except:
        pass

@dp.inline_query(lambda q: True)
async def inline_handler(query: types.InlineQuery):
    text = query.query.strip()
    user_id = query.from_user.id
    results = []
    
    try:
        amount = float(text)
        if amount > 0:
            balances = db.get_all_balances(user_id)
            for curr, bal in balances.items():
                if curr == 'user_id': continue
                if bal >= amount:
                    usd_val = get_usd_value(amount, curr)
                    results.append(types.InlineQueryResultArticle(
                        id=f"create_{curr}_{amount}",
                        title=f"Чек на {amount} {curr}",
                        description=f"Баланс: {bal} {curr} (${get_usd_value(bal, curr)})",
                        input_message_content=types.InputTextMessageContent(message_text=f"Создание чека на {amount} {curr}..."),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Создать чек", callback_data=f"inline_create_{curr}_{amount}")]])
                    ))
            if results:
                await query.answer(results, cache_time=0, is_personal=True)
                return
    except ValueError:
        pass
        
    if text:
        check = db.get_check(text)
        if check and check['is_active']:
            usd_val = get_usd_value(check['amount'], check['currency'])
            results.append(types.InlineQueryResultArticle(
                id=text,
                title=f"Получить {check['amount']} {check['currency']}",
                description=f"Сумма: ${usd_val}",
                input_message_content=types.InputTextMessageContent(message_text=f"Активация чека на {check['amount']} {check['currency']}..."),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Активировать", callback_data=f"activate_{text}")]])
            ))
            await query.answer(results, cache_time=0)
            return
            
    await query.answer([], cache_time=0)

@dp.callback_query(lambda c: c.data.startswith("inline_create_"))
async def process_inline_create(callback: types.CallbackQuery):
    data_part = callback.data.replace("inline_create_", "")
    parts = data_part.split("_")
    currency = parts[0]
    amount_str = "_".join(parts[1:])
    
    try:
        amount = float(amount_str)
    except:
        await callback.answer("Ошибка суммы", show_alert=True)
        return
        
    user_id = callback.from_user.id
    balance = db.get_balance(user_id, currency)
    
    if balance < amount:
        await callback.answer("Недостаточно средств", show_alert=True)
        return
        
    db.update_balance(user_id, currency, -amount)
    
    check_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    db.create_check(check_id, user_id, currency, amount)
    
    img_url = await generate_check_image(currency, amount)
    usd_val = get_usd_value(amount, currency)
    
    caption = (
        f"<b>Чек</b>\n\n"
        f"Сумма: {amount} {currency} (${usd_val})\n\n"
        f"Ссылка: <code>https://t.me/{bot.username}?start=check_{check_id}</code>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться чеком", switch_inline_query=check_id)],
        [InlineKeyboardButton(text="Удалить чек", callback_data=f"delete_check_{check_id}")]
    ])
    
    await callback.message.edit_media(media=InputMediaPhoto(media=img_url, caption=caption, parse_mode='HTML'), reply_markup=kb)
    await callback.answer("Чек создан!")

@dp.callback_query(lambda c: c.data.startswith("activate_"))
async def activate_inline_callback(callback: types.CallbackQuery):
    check_id = callback.data.replace("activate_", "")
    check = db.get_check(check_id)
    
    if not check or not check['is_active']:
        await callback.answer("Чек уже активирован!", show_alert=True)
        return
        
    activator_id = callback.from_user.id
    if activator_id == check['creator_id']:
        await callback.answer("Вы не можете активировать свой чек!", show_alert=True)
        return
        
    db.update_balance(activator_id, check['currency'], check['amount'])
    db.activate_check(check_id, activator_id)
    
    usd_val = get_usd_value(check['amount'], check['currency'])
    
    # ДОБАВЛЕНО: Кнопка "Открыть кошелек"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть кошелек", callback_data="wallet")]
    ])
    
    success_text = (
        f"<tg-emoji emoji-id='5312043357311111246'>📥</tg-emoji> Вы получили "
        f"<b>{check['amount']} {check['currency']}</b> "
        f"(<b>${usd_val}</b>)"
    )
    await callback.message.edit_text(success_text, parse_mode='HTML', reply_markup=kb)
    
    creator_id = check['creator_id']
    notify_text = (
        f"<tg-emoji emoji-id='5311998535032409760'>🎁</tg-emoji> "
        f"<a href='tg://user?id={activator_id}'>{callback.from_user.first_name}</a> активировал(а) ваш чек "
        f"и получил(а) <b>{check['amount']} {check['currency']}</b> (<b>${usd_val}</b>)"
    )
    try:
        await bot.send_message(creator_id, notify_text, parse_mode='HTML')
    except:
        pass
        
    await callback.answer("Чек активирован!")

@dp.callback_query(lambda c: c.data in ["exchange", "p2p", "market", "invoices", "cryptopay", "giveaways", "subscriptions", "settings", "deposit", "withdraw", "convert_gift"])
async def placeholder(callback: types.CallbackQuery):
    await callback.answer(f"Раздел '{callback.data}' пока в разработке", show_alert=True)

async def main():
    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
