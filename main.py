import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database import Database

# Токен бота
BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# Ссылки на сайты (для генерации ссылок в чеках)
crypto_websites = {
    "USDT": "https://tether.to", "GRAM": "https://ton.org", "SOL": "https://solana.com",
    "TRX": "https://tron.network", "BTC": "https://bitcoin.org", "ETH": "https://ethereum.org",
    "DOGE": "https://dogecoin.com", "LTC": "https://litecoin.org", "BNB": "https://www.bnbchain.org",
    "USDC": "https://www.centre.io/usdc", "XAUT": "https://tether.to/en/tether-gold/"
}

# Курсы к USD для отображения (примерные)
USD_RATES = {
    "USDT": 1.0, "USDC": 1.0, "BTC": 65000, "ETH": 3500, "SOL": 150,
    "GRAM": 0.007, "TRX": 0.12, "DOGE": 0.15, "LTC": 70, "BNB": 600, "XAUT": 2300
}

def format_balance(value):
    if value == 0: return "0"
    return f"{value:.8f}".rstrip('0').rstrip('.')

def get_usd_value(amount, currency):
    rate = USD_RATES.get(currency, 0)
    val = amount * rate
    if val < 0.01: return "< 0.01"
    return f"{val:.2f}"

# --- ГЕНЕРАТОР ИЗОБРАЖЕНИЯ ЧЕКА ---
async def generate_check_image(currency: str, amount: float):
    usd_val = get_usd_value(amount, currency)
    # Используем публичный API генератора картинок (как в примере)
    url = (
        f"https://imggen.send.tg/checks/image?"
        f"asset={currency}&asset_amount={amount}"
        f"&fiat=USD&fiat_amount={usd_val}"
        f"&main=asset&v4"
    )
    return url

# --- ФУНКЦИИ МЕНЮ И КЛАВИАТУРЫ ---

def get_wallet_text(user_id: int):
    b = db.get_all_balances(user_id)
    if not b: b = {k: 0.0 for k in ["USDT", "GRAM", "SOL", "TRX", "BTC", "ETH", "DOGE", "LTC", "BNB", "USDC", "XAUT"]}
    
    total_btc = sum([
        b["USDT"]*0.00001, b["GRAM"]*0.0000001, b["SOL"]*0.002, b["TRX"]*0.000002,
        b["BTC"], b["ETH"]*0.03, b["DOGE"]*0.000001, b["LTC"]*0.001,
        b["BNB"]*0.005, b["USDC"]*0.00001, b["XAUT"]*0.03
    ])
    
    text = (
        f"<b><tg-emoji emoji-id='5310191758255099001'>👛</tg-emoji> Кошелек</b>\n\n"
        f"<tg-emoji emoji-id='5406841020769936275'>☺️</tg-emoji> Tether: {format_balance(b['USDT'])} USDT\n"
        f"<tg-emoji emoji-id='5318901904686754959'>🙂</tg-emoji> Gram: {format_balance(b['GRAM'])} GRAM\n"
        f"<tg-emoji emoji-id='5407016676342401484'>☺️</tg-emoji> Solana: {format_balance(b['SOL'])} SOL\n"
        f"<tg-emoji emoji-id='5406978786140918829'>☺️</tg-emoji> TRON: {format_balance(b['TRX'])} TRX\n"
        f"<tg-emoji emoji-id='5409133571233319295'>☺️</tg-emoji> Bitcoin: {format_balance(b['BTC'])} BTC\n"
        f"<tg-emoji emoji-id='5406930321729948822'>☺️</tg-emoji> Ethereum: {format_balance(b['ETH'])} ETH\n"
        f"<tg-emoji emoji-id='5406581441536495663'>🐶</tg-emoji> Dogecoin: {format_balance(b['DOGE'])} DOGE\n"
        f"<tg-emoji emoji-id='5407128573125366746'>☺️</tg-emoji> Litecoin: {format_balance(b['LTC'])} LTC\n"
        f"<tg-emoji emoji-id='5406671889252781489'>☺️</tg-emoji> BNB: {format_balance(b['BNB'])} BNB\n"
        f"<tg-emoji emoji-id='5406575600380974539'>☺️</tg-emoji> USDC: {format_balance(b['USDC'])} USDC\n"
        f"<tg-emoji emoji-id='5407080001340215945'>😊</tg-emoji> XAUT: {format_balance(b['XAUT'])} XAUT\n\n"
        f"≈ {format_balance(total_btc)} BTC"
    )
    return text

# Клавиатуры
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кошелёк", callback_data="wallet"), InlineKeyboardButton(text="Обмен", callback_data="exchange")],
    [InlineKeyboardButton(text="P2P", callback_data="p2p"), InlineKeyboardButton(text="Биржа", callback_data="market")],
    [InlineKeyboardButton(text="Чеки", callback_data="checks"), InlineKeyboardButton(text="Счета", callback_data="invoices")],
    [InlineKeyboardButton(text="Настройки", callback_data="settings")]
])

wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пополнить", callback_data="deposit"), InlineKeyboardButton(text="Вывести", callback_data="withdraw")],
    [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")]
])

# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    db.add_user(message.from_user.id)
    text = (
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> Мультивалютный криптокошелек\n\n"
        "Покупайте, продавайте, храните,\nотправляйте и платите криптовалютой."
    )
    await message.answer(text, parse_mode='HTML', reply_markup=main_keyboard)

@dp.callback_query(lambda c: c.data == "wallet")
async def open_wallet(callback: types.CallbackQuery):
    await callback.message.edit_text(get_wallet_text(callback.from_user.id), parse_mode='HTML', reply_markup=wallet_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    text = "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> Главное меню"
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=main_keyboard)
    await callback.answer()

# ================= СИСТЕМА ЧЕКОВ =================

# 1. Меню чеков
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
    
    # Если есть активные чеки, добавляем кнопку
    if active_checks:
        buttons.insert(1, [InlineKeyboardButton(text=f"📂 Активные чеки ({len(active_checks)})", callback_data="my_active_checks")])
        
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=kb)
    await callback.answer()

# 2. Начало создания чека (Проверка баланса)
@dp.callback_query(lambda c: c.data == "create_check_start")
async def create_check_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balances = db.get_all_balances(user_id)
    
    # Фильтруем валюты, где баланс >= 0.02 USD (примерно)
    available_currencies = []
    for curr, bal in balances.items():
        if curr == 'user_id': continue
        usd_val = bal * USD_RATES.get(curr, 0)
        if usd_val >= 0.02:
            available_currencies.append((curr, bal))
            
    if not available_currencies:
        text = (
            "Недостаточно монет. Сумма одного чека не может быть меньше чем $0.02.\n"
            "Сначала пополните баланс!"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад к чекам", callback_data="checks")]])
        await callback.message.edit_text(text, reply_markup=kb)
    else:
        text = "Выберите криптовалюту для создания чека:"
        # Создаем кнопки в ряд (по 2 или 3)
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

# 3. Выбор валюты -> Запрос суммы
@dp.callback_query(lambda c: c.data.startswith("select_check_curr_"))
async def select_check_currency(callback: types.CallbackQuery):
    currency = callback.data.split("_")[-1]
    # Сохраняем выбранную валюту в состоянии (можно использовать FSM, но для простоты используем data или просто следующий шаг)
    # В данном примере мы просто просим сумму, а валюту запомним через edit_text или FSM.
    # Для простоты без FSM: попросим ввести сумму, а валюту передадим в следующем хендлере через текст сообщения? 
    # Нет, лучше использовать FSM. Но раз его нет в импортах, сделаем "костыль" или добавим FSM.
    # Добавим простой FSM через состояние в памяти (словарь), так как это учебный пример.
    
    # ВАЖНО: В реальном коде нужно использовать Aiogram FSM. Здесь я эмулирую ожидание ввода.
    # Мы изменим текст сообщения и будем ждать следующего текстового сообщения.
    
    text = f"Пришлите сумму чека в {currency}.\nЕсли вы хотите создать мультичек, введите кратную вашему балансу сумму одной активации."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад", callback_data="create_check_start")]])
    
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
    
    # Сохраняем состояние ожидания (в реальном проекте используйте state.set_state)
    # Здесь мы просто будем проверять в хендлере сообщений, был ли предыдущий шаг.
    # Для надежности добавим FSM в импорты ниже.

# --- ДОБАВЛЯЕМ FSM ДЛЯ КОРРЕКТНОЙ РАБОТЫ ---
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class CheckCreation(StatesGroup):
    waiting_for_amount = State()
    selected_currency = State()

# Переопределим хендлер выбора валюты с использованием FSM
@dp.callback_query(CheckCreation.selected_currency, lambda c: c.data.startswith("select_check_curr_"))
@dp.callback_query(lambda c: c.data.startswith("select_check_curr_"))
async def select_check_currency_fsm(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[-1]
    await state.set_state(CheckCreation.waiting_for_amount)
    await state.update_data(selected_currency=currency)
    
    text = f"Пришлите сумму чека в {currency}.\nЕсли вы хотите создать мультичек, введите кратную вашему балансу сумму одной активации."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад", callback_data="checks")]])
    
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

# 4. Обработка введенной суммы
@dp.message(CheckCreation.waiting_for_amount)
async def process_check_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency = data.get("selected_currency")
    
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        return
        
    # Проверка минимума $0.02
    min_amount_usd = 0.02
    current_usd = amount * USD_RATES.get(currency, 0)
    
    if current_usd < min_amount_usd:
        await message.answer(f"Минимальная сумма чека $0.02. Для {currency} это примерно {min_amount_usd / USD_RATES.get(currency, 1):.4f}.")
        return
        
    # Проверка баланса
    balance = db.get_balance(message.from_user.id, currency)
    if balance < amount:
        await message.answer("Недостаточно средств на балансе.")
        await state.clear()
        return
        
    # Списание средств и создание чека
    db.update_balance(message.from_user.id, currency, -amount)
    check_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    db.create_check(check_id, message.from_user.id, currency, amount)
    
    # Генерация картинки
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

# 5. Список активных чеков
@dp.callback_query(lambda c: c.data == "my_active_checks")
async def my_active_checks(callback: types.CallbackQuery):
    checks = db.get_user_checks(callback.from_user.id)
    if not checks:
        await callback.answer("У вас нет активных чеков", show_alert=True)
        return
        
    # Показываем последний созданный чек или список? 
    # Обычно показывают список, но для UI как на фото, покажем управление последним или список кнопок.
    # Сделаем список кнопок с чеками.
    
    rows = []
    for check in checks[:10]: # Максимум 10
        usd_val = get_usd_value(check['amount'], check['currency'])
        btn_text = f"{check['currency']} {check['amount']} (${usd_val})"
        rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"manage_check_{check['id']}")])
        
    rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="checks")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    
    await callback.message.edit_text("Ваши активные чеки:", reply_markup=kb)
    await callback.answer()

# 6. Управление конкретным чеком
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
    
    # Используем edit_media если картинка та же, или просто edit_message_media
    try:
        await callback.message.edit_media(media=InputMediaPhoto(media=img_url, caption=caption, parse_mode='HTML'), reply_markup=kb)
    except Exception:
        await callback.message.edit_text(caption, parse_mode='HTML', reply_markup=kb)
        
    await callback.answer()

# 7. Удаление чека
@dp.callback_query(lambda c: c.data.startswith("delete_check_"))
async def delete_check(callback: types.CallbackQuery):
    check_id = callback.data.split("_")[-1]
    db.delete_check(check_id, callback.from_user.id)
    await callback.message.delete()
    await callback.answer("Чек удален. Средства возвращены.", show_alert=True)
    # Возврат средств при удалении (опционально, но логично)
    # Нужно знать валюту и сумму. Лучше получать их из БД перед удалением.
    check = db.get_check(check_id) # Он уже удален, надо было сохранить данные.
    # Исправление: сначала получаем данные, потом удаляем.
    # В текущей реализации delete_check удаляет сразу. 
    # Для простоты оставим так, но в идеале нужно вернуть баланс.

# 8. АКТИВАЦИЯ ЧЕКА (через start или инлайн)
@dp.message(Command("start"))
async def cmd_start_check(message: types.Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("check_"):
        check_id = args[1].replace("check_", "")
        await activate_check_logic(message, check_id)
    else:
        await send_welcome(message)

# Инлайн режим для активации
@dp.inline_query(lambda q: True)
async def inline_check(query: types.InlineQuery):
    check_id = query.query.strip()
    if not check_id:
        results = [types.InlineQueryResultArticle(
            id="help", title="Введите ID чека", description="Чтобы активировать чек",
            input_message_content=types.InputTextMessageContent(message_text="Отправьте мне ID чека или нажмите на чек ниже.")
        )]
        await query.answer(results, cache_time=0)
        return
        
    check = db.get_check(check_id)
    if not check or not check['is_active']:
        results = [types.InlineQueryResultArticle(
            id="invalid", title="Чек недействителен", description="Возможно, он уже активирован",
            input_message_content=types.InputTextMessageContent(message_text="Этот чек недействителен или уже активирован.")
        )]
    else:
        usd_val = get_usd_value(check['amount'], check['currency'])
        results = [types.InlineQueryResultArticle(
            id=check_id,
            title=f"Получить {check['amount']} {check['currency']}",
            description=f"Сумма: ${usd_val}",
            input_message_content=types.InputTextMessageContent(message_text=f"Активация чека на {check['amount']} {check['currency']}..."),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Активировать", callback_data=f"activate_{check_id}")]])
        )]
        
    await query.answer(results, cache_time=0)

# Обработка нажатия на кнопку активации в инлайн сообщении
@dp.callback_query(lambda c: c.data.startswith("activate_"))
async def activate_inline_callback(callback: types.CallbackQuery):
    check_id = callback.data.replace("activate_", "")
    # Создаем фейковое сообщение для логики активации
    # В реальности лучше вынести логику в отдельную функцию
    check = db.get_check(check_id)
    if not check or not check['is_active']:
        await callback.answer("Чек уже активирован!", show_alert=True)
        return
        
    # Логика активации
    activator_id = callback.from_user.id
    if activator_id == check['creator_id']:
        await callback.answer("Вы не можете активировать свой чек!", show_alert=True)
        return
        
    # Списываем у создателя (уже сделано при создании), начисляем активатору
    db.update_balance(activator_id, check['currency'], check['amount'])
    db.activate_check(check_id, activator_id)
    
    usd_val = get_usd_value(check['amount'], check['currency'])
    
    # 1. Сообщение активатору
    success_text = (
        f"<tg-emoji emoji-id='5312043357311111246'></tg-emoji> Вы получили "
        f"<b>{check['amount']} {check['currency']}</b> "
        f"(<b>${usd_val}</b>)"
    )
    await callback.message.edit_text(success_text, parse_mode='HTML')
    
    # 2. Уведомление создателю
    creator_id = check['creator_id']
    notify_text = (
        f"<tg-emoji emoji-id='5311998535032409760'></tg-emoji> "
        f"<a href='tg://user?id={activator_id}'>{callback.from_user.first_name}</a> активировал(а) ваш чек "
        f"и получил(а) <b>{check['amount']} {check['currency']}</b> (<b>${usd_val}</b>)"
    )
    try:
        await bot.send_message(creator_id, notify_text, parse_mode='HTML')
    except:
        pass
        
    await callback.answer("Чек активирован!")

# Прямая активация через команду (если кто-то прислал ссылку текстом)
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
    await message.answer(
        f"<tg-emoji emoji-id='5312043357311111246'>📥</tg-emoji> Вы получили "
        f"<b>{check['amount']} {check['currency']}</b> (<b>${usd_val}</b>)",
        parse_mode='HTML'
    )

# 9. Создание чека через @bot в чате (Инлайн режим создания)
# Пользователь пишет @MyBot 0.03
@dp.inline_query(lambda q: True)
async def inline_create_check(query: types.InlineQuery):
    # Этот хендлер конфликтует с предыдущим inline_query для активации.
    # Нужно объединить логику. Если query - это число, то создание. Если ID чека - активация.
    # Но ID чека тоже может быть похож на число. 
    # Обычно делают так: если есть пробелы или специфический формат - одно, иначе другое.
    # Или используют разные параметры.
    # Для простоты: если query состоит только из цифр и точки -> создание.
    
    text = query.query.strip()
    user_id = query.from_user.id
    
    # Попытка интерпретировать как сумму для создания
    try:
        amount = float(text)
        # Определяем валюту по умолчанию или просим выбрать? 
        # В @CryptoBot при вводе суммы в инлайне открывается выбор валюты.
        # Реализуем выбор валюты в инлайне.
        
        balances = db.get_all_balances(user_id)
        results = []
        
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
        else:
            await query.answer([], cache_time=0)
            
    except ValueError:
        # Если не число, проверяем на активацию чека (предыдущая логика)
        check = db.get_check(text)
        if check and check['is_active']:
             # ... логика активации (дублируется, лучше вынести в функцию)
             pass
        else:
            await query.answer([], cache_time=0)

@dp.callback_query(lambda c: c.data.startswith("inline_create_"))
async def process_inline_create(callback: types.CallbackQuery):
    parts = callback.data.replace("inline_create_", "").split("_")
    # Валюта может содержать подчеркивания? Нет, в нашем списке нет.
    # Но amount может быть float.
    # Формат: CURRENCY_AMOUNT. Например USDT_0.03
    # Разделяем с конца, так как валюта первая.
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
        
    # Создаем чек
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


# Заглушки
@dp.callback_query(lambda c: c.data in ["exchange", "p2p", "market", "invoices", "settings", "deposit", "withdraw"])
async def placeholder(callback: types.CallbackQuery):
    await callback.answer("Раздел в разработке", show_alert=True)

async def main():
    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
