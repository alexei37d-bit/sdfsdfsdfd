import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from database import Database

BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# ID администратора
ADMIN_IDS = [7921743592]

crypto_websites = {
    "USDT":  "https://tether.to",  "GRAM":  "https://ton.org",  "SOL":  "https://solana.com",
    "TRX":  "https://tron.network",  "BTC":  "https://bitcoin.org",  "ETH":  "https://ethereum.org",
    "DOGE":  "https://dogecoin.com",  "LTC":  "https://litecoin.org",  "BNB":  "https://www.bnbchain.org",
    "USDC":  "https://www.centre.io/usdc",  "XAUT":  "https://tether.to/en/tether-gold/"
}

USD_RATES = {
    "USDT": 1.0,  "USDC": 1.0,  "BTC": 65000,  "ETH": 3500,  "SOL": 150,
    "GRAM": 0.007,  "TRX": 0.12,  "DOGE": 0.15,  "LTC": 70,  "BNB": 600,  "XAUT": 2300
}

CURRENCY_ORDER = ["USDT", "GRAM", "SOL", "TRX", "BTC", "ETH", "DOGE", "LTC", "BNB", "USDC", "XAUT"]

CRYPTO_EMOJIS = {
    "USDT":  "5406841020769936275",
    "GRAM":  "5318901904686754959",
    "SOL":  "5407016676342401484",
    "TRX":  "5406978786140918829",
    "BTC":  "5409133571233319295",
    "ETH":  "5406930321729948822",
    "DOGE":  "5406581441536495663",
    "LTC":  "5407128573125366746",
    "BNB":  "5406671889252781489",
    "USDC":  "5406575600380974539",
    "XAUT":  "5407080001340215945"
}

# Хранилище состояний
user_states = {}

--- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def format_balance(value):
    if value == 0:
        return "0"
    return f"{value:.8f}".rstrip('0').rstrip('.')

def generate_invoice_id():
    while True:
        invoice_id = "IV" + ''.join(random.choices(string.digits, k=8))
        if not db.get_invoice(invoice_id):
            return invoice_id

def get_sorted_currencies(user_id):
    balances = db.get_all_balances(user_id)
    all_zero = all(balances.get(curr, 0) == 0 for curr in CURRENCY_ORDER)
    if all_zero:
        return CURRENCY_ORDER.copy()
    else:
        return sorted(CURRENCY_ORDER, key=lambda x: (-balances.get(x, 0), CURRENCY_ORDER.index(x)))

--- ТЕКСТЫ И КЛАВИАТУРЫ ---
def get_wallet_text(user_id: int):
    b = db.get_all_balances(user_id)
    if not b:
        b = {k: 0.0 for k in CURRENCY_ORDER}
    
    total_btc = sum([
        b.get("USDT", 0)*0.00001, b.get("GRAM", 0)*0.0000001, b.get("SOL", 0)*0.002,
        b.get("TRX", 0)*0.000002, b.get("BTC", 0), b.get("ETH", 0)*0.03,
        b.get("DOGE", 0)*0.000001, b.get("LTC", 0)*0.001,
        b.get("BNB", 0)*0.005, b.get("USDC", 0)*0.00001, b.get("XAUT", 0)*0.03
    ])
    
    sorted_currencies = get_sorted_currencies(user_id)
    text = f"<b><tg-emoji emoji-id='5310191758255099001'>👛</tg-emoji> Кошелек</b>\n\n"
    
    for currency in sorted_currencies:
        emoji_id = CRYPTO_EMOJIS[currency]
        balance = b.get(currency, 0)
        website = crypto_websites[currency]
        text += f"<tg-emoji emoji-id='{emoji_id}'>☺️</tg-emoji>  <a href='{website}'>{currency}</a>: {format_balance(balance)} {currency}\n\n"
        
    text += f"≈ {format_balance(total_btc)} BTC"
    return text

def get_main_keyboard(user_id):
    """Собирает главную клавиатуру с персональной ссылкой на Web App (с балансом пользователя)"""
    return InlineKeyboardMarkup(inline_keyboard=[
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

--- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    db.add_user(message.from_user.id)
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("IV"):
        invoice_id = args[1]
        await handle_invoice_payment_start(message, invoice_id)
        return

    if message.from_user.id in ADMIN_IDS:
        usdt_balance = db.get_balance(message.from_user.id, "USDT")
        if usdt_balance == 0:
            db.update_balance(message.from_user.id, "USDT", 100)

    text = (
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/6'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.  "
    )
    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=get_main_keyboard(message.from_user.id))

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
        "<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji>  "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/6'>Мультивалютный криптокошелек</a>\n\n"
        "Покупайте, продавайте, храните,\n"
        "отправляйте и платите криптовалютой,\n"
        "когда хотите.\n\n"
        "Подписывайтесь на  <a href='https://t.me/Crypto_Bot_RUSSIA'>наш канал</a> и вступайте в\n"
        "<a href='https://t.me/Crypto_Bot_Russian_Chat'>наш чат</a>.   "
    )
    try:
        await callback.message.edit_text(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=get_main_keyboard(callback.from_user.id))
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

--- ЛОГИКА СЧЕТОВ ---
@dp.callback_query(lambda c: c.data == "invoices")
async def open_invoices(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    text = (
        "Здесь вы можете создать счет\n"
        "для получения оплаты или сбора\n"
        "средств в криптовалюте. Смотрите  "
        "<a href='https://t.me/Crypto_Bot_RUSSIA/7'>инструкцию ›</a>"
    )
    user_invoices = db.get_active_invoices_for_list(user_id)
    keyboard_rows = []
    keyboard_rows.append([InlineKeyboardButton(text="Создать счет", callback_data="create_invoice")])
    if user_invoices:
        keyboard_rows.append([InlineKeyboardButton(text=f"Активные счета ({len(user_invoices)})", callback_data="view_invoices")])
    keyboard_rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    try:
        await callback.message.edit_text(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data == "create_invoice")
async def choose_invoice_type(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_states[user_id] = {'step': 'choose_type'}
    text = "Выберите тип счета."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Одноразовый", callback_data="invoice_single"),
            InlineKeyboardButton(text="Многоразовый", callback_data="invoice_multi")
        ],
        [InlineKeyboardButton(text="‹ Назад к счетам", callback_data="invoices")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data in ["invoice_single", "invoice_multi"])
async def select_invoice_type(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    invoice_type = "single" if callback.data == "invoice_single" else "multi"
    user_states[user_id] = {
        'step': 'select_currencies',
        'invoice_type': invoice_type,
        'selected_currencies': set(),
        'show_dots': False
    }
    await show_currency_selection(callback)
    await callback.answer()

async def show_currency_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    state = user_states[user_id]
    text = (
        "Выберите одну или больше криптовалют,\n"
        "которыми может быть оплачен счет."
    )
    keyboard_rows = []
    for i in range(0, len(CURRENCY_ORDER), 3):
        row = []
        for j in range(i, min(i+3, len(CURRENCY_ORDER))):
            currency = CURRENCY_ORDER[j]
            selected = currency in state['selected_currencies']
            dot = " ·" if (selected or (not state['selected_currencies'] and state.get('show_dots', False))) else ""
            btn_text = f"{currency}{dot}"
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"toggle_currency_{currency}"))
        keyboard_rows.append(row)
    
    nav_buttons = [
        InlineKeyboardButton(text="Далее›", callback_data="invoice_next_after_currency"),
        InlineKeyboardButton(text="‹ Изменить тип счета", callback_data="create_invoice")
    ]
    keyboard_rows.append(nav_buttons)
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e

@dp.callback_query(lambda c: c.data.startswith("toggle_currency_"))
async def toggle_currency(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    currency = callback.data.replace("toggle_currency_", "")
    state = user_states[user_id]
    if currency in state['selected_currencies']:
        state['selected_currencies'].remove(currency)
    else:
        state['selected_currencies'].add(currency)
    state['show_dots'] = True
    await show_currency_selection(callback)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "invoice_next_after_currency")
async def after_currency_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    state = user_states[user_id]
    if not state['selected_currencies']:
        state['selected_currencies'] = set(CURRENCY_ORDER)
    state['step'] = 'enter_amount'
    currencies_str = ", ".join(sorted(state['selected_currencies']))
    text = f"Пришлите сумму счета в USD (мин. 0.01) с оплатой в {currencies_str}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="‹ Изменить монету", callback_data="select_currencies_again")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data == "select_currencies_again")
async def back_to_currency_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_states[user_id]['step'] = 'select_currencies'
    user_states[user_id]['show_dots'] = True
    await show_currency_selection(callback)
    await callback.answer()

@dp.message(lambda m: m.text and m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'enter_amount')
async def process_amount(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    try:
        amount = float(message.text)
        # ПРОВЕРКА НА МИНИМАЛЬНУЮ СУММУ 0.01
        if amount < 0.01:
            await message.answer("❌ Минимальная сумма счета составляет 0.01 USD. Попробуйте еще раз.")
            return
        
        state['amount_usd'] = amount
        state['step'] = 'invoice_created'
        invoice_id = generate_invoice_id()
        state['invoice_id'] = invoice_id
        currencies_list = sorted(list(state['selected_currencies']))
        db.create_invoice(
            invoice_id=invoice_id,
            creator_id=user_id,
            amount_usd=amount,
            currencies=currencies_list,
            invoice_type=state['invoice_type']
        )
        await show_invoice_details(message, invoice_id)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (число).")

async def show_invoice_details(message_or_callback, invoice_id):
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        return
    
    # Проверка владельца для отображения кнопок управления
    is_owner = False
    if isinstance(message_or_callback, types.CallbackQuery):
        is_owner = (message_or_callback.from_user.id == invoice['creator_id'])
    elif isinstance(message_or_callback, types.Message):
        # При создании счета автор всегда владелец
        is_owner = True 

    currencies_str = ", ".join(invoice['currencies'])
    bot_username = (await bot.get_me()).username
    text = (
        f"Счет #{invoice_id}\n\n"
        f"Сумма: ${invoice['amount_usd']}\n\n"
        f"Любой может оплатить этот счет в {currencies_str}.\n\n"
        f"Скопируйте ссылку, чтобы поделиться счетом:\n"
        f"https://t.me/{bot_username}?start={invoice_id}"
    )
    
    keyboard_rows = [
        [InlineKeyboardButton(text="Поделиться счетом", switch_inline_query=invoice_id)]
    ]
    
    # Кнопки управления только для владельца
    if is_owner:
        keyboard_rows.append([InlineKeyboardButton(text="Разрешения", callback_data=f"invoice_permissions_{invoice_id}")])
        keyboard_rows.append([InlineKeyboardButton(text="Удалить счет", callback_data=f"delete_invoice_{invoice_id}")])
        
    keyboard_rows.append([InlineKeyboardButton(text="‹ Назад к списку счетов", callback_data="invoices")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    if isinstance(message_or_callback, types.CallbackQuery):
        try:
            await message_or_callback.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise e
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("invoice_permissions_"))
async def show_invoice_permissions(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("invoice_permissions_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice:
        await callback.answer("Счет не найден.", show_alert=True)
        return
        
    # ПРОВЕРКА ВЛАДЕЛЬЦА
    if callback.from_user.id != invoice['creator_id']:
        await callback.answer("Это не ваш счет.", show_alert=True)
        return

    comments_status = "Вкл." if invoice['allow_comments'] else "Выкл."
    anonymous_status = "Вкл." if invoice['allow_anonymous'] else "Выкл."
    text = (
        "Разрешите или запретите оплачивать счет анонимно  "
        "и добавлять коментарии при оплате."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Коментарии: {comments_status}", callback_data=f"toggle_comments_{invoice_id}")],
        [InlineKeyboardButton(text=f"Анонимные платежы: {anonymous_status}", callback_data=f"toggle_anonymous_{invoice_id}")],
        [InlineKeyboardButton(text="‹ Назад к счету", callback_data=f"view_invoice_{invoice_id}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("toggle_comments_"))
async def toggle_comments(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("toggle_comments_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice or callback.from_user.id != invoice['creator_id']:
        await callback.answer("Ошибка доступа.", show_alert=True)
        return

    new_value = 0 if invoice['allow_comments'] else 1
    db.update_invoice_settings(invoice_id, allow_comments=new_value)
    await show_invoice_permissions(callback)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("toggle_anonymous_"))
async def toggle_anonymous(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("toggle_anonymous_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice or callback.from_user.id != invoice['creator_id']:
        await callback.answer("Ошибка доступа.", show_alert=True)
        return

    new_value = 0 if invoice['allow_anonymous'] else 1
    db.update_invoice_settings(invoice_id, allow_anonymous=new_value)
    await show_invoice_permissions(callback)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("delete_invoice_"))
async def confirm_delete_invoice(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("delete_invoice_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice or callback.from_user.id != invoice['creator_id']:
        await callback.answer("Ошибка доступа.", show_alert=True)
        return

    text = "❌ Вы уверены, что хотите удалить этот счет?"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=f"confirm_delete_{invoice_id}"),
            InlineKeyboardButton(text="Нет", callback_data=f"view_invoice_{invoice_id}")
        ]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def delete_invoice(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("confirm_delete_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice or callback.from_user.id != invoice['creator_id']:
        await callback.answer("Ошибка доступа.", show_alert=True)
        return

    db.delete_invoice(invoice_id)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer("Счет удален.")

@dp.callback_query(lambda c: c.data.startswith("view_invoice_"))
async def view_invoice(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("view_invoice_", "")
    await show_invoice_details(callback, invoice_id)

@dp.callback_query(lambda c: c.data == "view_invoices")
async def view_all_invoices(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    invoices_ids = db.get_active_invoices_for_list(user_id)
    if not invoices_ids:
        await callback.answer("У вас нет активных счетов.", show_alert=True)
        return
    
    keyboard_rows = []
    for inv_id in invoices_ids:
        keyboard_rows.append([InlineKeyboardButton(text=f"Счет {inv_id}", callback_data=f"view_invoice_{inv_id}")])
    keyboard_rows.append([InlineKeyboardButton(text="‹ Назад к счетам", callback_data="invoices")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    try:
        await callback.message.edit_text("Ваши активные счета:", reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

--- SHARE INVOICE (INLINE QUERY) ---
@dp.inline_query(lambda q: True)
async def inline_query_handler(query: types.InlineQuery):
    query_text = query.query.strip()
    if not query_text.startswith("IV"):
        return
    
    invoice = db.get_invoice(query_text)
    if not invoice or not invoice['is_active']:
        return
        
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        return

    bot_username = (await bot.get_me()).username
    if invoice['invoice_type'] == 'multi':
        title_text = f"Многоразовый счет на ${invoice['amount_usd']}"
    else:
        title_text = f"Счет на ${invoice['amount_usd']}"
        
    result = types.InlineQueryResultArticle(
        id=query_text,
        title="Поделиться счетом",
        description="Нажмите, чтобы поделиться этим счетом.",
        input_message_content=types.InputTextMessageContent(
            message_text=f"<tg-emoji emoji-id=\"5312043357311111246\">📥</tg-emoji> {title_text}",
            parse_mode="HTML"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=f"https://t.me/{bot_username}?start={query_text}")]
        ])
    )
    await query.answer(results=[result], cache_time=0)

--- PAY INVOICE ---
async def handle_invoice_payment_start(message, invoice_id):
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['is_active']:
        await message.answer("Счет не найден или не активен.")
        return
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        await message.answer("Счет уже оплачен.")
        return

    text = f"Выберите монету для оплаты счета #{invoice_id} на сумму ${invoice['amount_usd']}."
    keyboard_rows = []
    for currency in invoice['currencies']:
        rate = USD_RATES.get(currency, 1)
        amount_in_currency = invoice['amount_usd'] / rate
        btn_text = f"{currency} · {format_balance(amount_in_currency)} {currency}"
        keyboard_rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"pay_invoice_{invoice_id}_{currency}")])
    keyboard_rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await message.answer(text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("pay_invoice_"))
async def select_payment_currency(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    invoice_id = parts[2]
    currency = parts[3]
    
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['is_active']:
        await callback.answer("Счет не найден или не активен.", show_alert=True)
        return
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        await callback.answer("Счет уже оплачен.", show_alert=True)
        return

    rate = USD_RATES.get(currency, 1)
    amount_in_currency = invoice['amount_usd'] / rate
    user_id = callback.from_user.id
    
    user_states[user_id] = {
        'step': 'confirm_payment',
        'invoice_id': invoice_id,
        'currency': currency,
        'amount_in_currency': amount_in_currency,
        'comment': '',
        'is_anonymous': 0
    }
    
    # Определяем доступность функций исходя из настроек счета
    allow_anon = invoice['allow_anonymous']
    allow_comm = invoice['allow_comments']
    
    anon_btn_text = f"Оплатить анонимно: {'Да' if user_states[user_id]['is_anonymous'] else 'Нет'}"
    if not allow_anon:
        anon_btn_text = "Анонимность запрещена"

    text = (
        f"<tg-emoji emoji-id=\"5312043357311111246\">📥</tg-emoji> <b>Подтвердите оплату счета #{invoice_id}</b>\n\n"
        f"<b>Отправляете:</b> <b>{format_balance(amount_in_currency)} {currency} (${invoice['amount_usd']})</b>\n\n"
        f"Вы уверены, что хотите оплатить этот счет?"
    )
    
    kb_rows = [
        [InlineKeyboardButton(text=f"💳 Оплатить {format_balance(amount_in_currency)} {currency}", callback_data=f"process_payment_{invoice_id}_{currency}")]
    ]
    
    if allow_anon:
        kb_rows.append([InlineKeyboardButton(text=anon_btn_text, callback_data=f"toggle_pay_anonymous_{invoice_id}")])
    
    if allow_comm:
        kb_rows.append([InlineKeyboardButton(text="Добавить коментарий", callback_data=f"add_comment_{invoice_id}")])
        
    kb_rows.append([InlineKeyboardButton(text="‹ Назад к оплате", callback_data=f"back_to_payment_select_{invoice_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    try:
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("toggle_pay_anonymous_"))
async def toggle_pay_anonymous(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("toggle_pay_anonymous_", "")
    user_id = callback.from_user.id
    
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['allow_anonymous']:
         await callback.answer("Анонимная оплата запрещена создателем счета.", show_alert=True)
         return

    if user_id in user_states and user_states[user_id].get('step') == 'confirm_payment':
        current = user_states[user_id].get('is_anonymous', 0)
        user_states[user_id]['is_anonymous'] = 1 - current
        # Перерисовываем экран, чтобы обновить текст кнопки
        await select_payment_currency(callback)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("add_comment_"))
async def add_comment(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("add_comment_", "")
    user_id = callback.from_user.id
    
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['allow_comments']:
         await callback.answer("Комментарии запрещены создателем счета.", show_alert=True)
         return

    user_states[user_id]['step'] = 'enter_comment'
    user_states[user_id]['invoice_id'] = invoice_id
    text = "Пришлите комментарий к платежу, который будет виден в уведомлении об оплате (до 1024 символов)."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="‹ Назад к оплате", callback_data=f"back_to_payment_select_{invoice_id}")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.message(lambda m: m.text and m.from_user.id in user_states and user_states[m.from_user.id].get('step') == 'enter_comment')
async def process_comment(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    comment = message.text[:1024]
    state['comment'] = comment
    state['step'] = 'confirm_payment'
    invoice_id = state['invoice_id']
    await select_payment_currency_by_data(message, invoice_id, state['currency'])

async def select_payment_currency_by_data(message, invoice_id, currency):
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['is_active']:
        await message.answer("Счет не найден или не активен.")
        return
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        await message.answer("Счет уже оплачен.")
        return

    rate = USD_RATES.get(currency, 1)
    amount_in_currency = invoice['amount_usd'] / rate
    
    allow_anon = invoice['allow_anonymous']
    allow_comm = invoice['allow_comments']
    
    # Получаем актуальное состояние из стейта, если он есть (при возврате из комментария)
    user_id = message.from_user.id
    is_anon_state = 0
    if user_id in user_states and user_states[user_id].get('step') == 'confirm_payment':
        is_anon_state = user_states[user_id].get('is_anonymous', 0)

    anon_btn_text = f"Оплатить анонимно: {'Да' if is_anon_state else 'Нет'}"
    if not allow_anon:
        anon_btn_text = "Анонимность запрещена"

    text = (
        f"<tg-emoji emoji-id=\"5312043357311111246\">📥</tg-emoji> <b>Подтвердите оплату счета #{invoice_id}</b>\n\n"
        f"<b>Отправляете:</b> <b>{format_balance(amount_in_currency)} {currency} (${invoice['amount_usd']})</b>\n\n"
        f"Вы уверены, что хотите оплатить этот счет?"
    )
    
    kb_rows = [
        [InlineKeyboardButton(text=f"💳 Оплатить {format_balance(amount_in_currency)} {currency}", callback_data=f"process_payment_{invoice_id}_{currency}")]
    ]
    
    if allow_anon:
        kb_rows.append([InlineKeyboardButton(text=anon_btn_text, callback_data=f"toggle_pay_anonymous_{invoice_id}")])
        
    if allow_comm:
        kb_rows.append([InlineKeyboardButton(text="Добавить коментарий", callback_data=f"add_comment_{invoice_id}")])
        
    kb_rows.append([InlineKeyboardButton(text="‹ Назад к оплате", callback_data=f"back_to_payment_select_{invoice_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    await message.answer(text, parse_mode='HTML', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("back_to_payment_select_"))
async def back_to_payment_select(callback: types.CallbackQuery):
    invoice_id = callback.data.replace("back_to_payment_select_", "")
    invoice = db.get_invoice(invoice_id)
    
    if not invoice or not invoice['is_active']:
        await callback.answer("Счет не найден или не активен.", show_alert=True)
        return
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        await callback.answer("Счет уже оплачен.", show_alert=True)
        return

    text = f"Выберите монету для оплаты счета #{invoice_id} на сумму ${invoice['amount_usd']}."
    keyboard_rows = []
    for currency in invoice['currencies']:
        rate = USD_RATES.get(currency, 1)
        amount_in_currency = invoice['amount_usd'] / rate
        btn_text = f"{currency} · {format_balance(amount_in_currency)} {currency}"
        keyboard_rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"pay_invoice_{invoice_id}_{currency}")])
    keyboard_rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise e
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("process_payment_"))
async def process_payment(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    invoice_id = parts[2]
    currency = parts[3]
    user_id = callback.from_user.id
    
    invoice = db.get_invoice(invoice_id)
    if not invoice or not invoice['is_active']:
        await callback.answer("Счет не найден или не активен.", show_alert=True)
        return
    if invoice['invoice_type'] == 'single' and invoice['is_paid']:
        await callback.answer("Счет уже оплачен.", show_alert=True)
        return

    state = user_states.get(user_id, {})
    rate = USD_RATES.get(currency, 1)
    amount_in_currency = invoice['amount_usd'] / rate
    
    payer_balance = db.get_balance(user_id, currency)
    if payer_balance < amount_in_currency:
        text = "❌ Недостаточно средств."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_payment_select_{invoice_id}")]
        ])
        try:
            await callback.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest:
            pass
        await callback.answer()
        return

    is_anonymous = state.get('is_anonymous', 0)
    comment = state.get('comment', '')
    
    # ПРОВЕРКИ БЕЗОПАСНОСТИ И НАСТРОЕК
    if invoice['allow_anonymous'] == 0 and is_anonymous == 1:
        await callback.answer("Создатель счета запретил анонимную оплату.", show_alert=True)
        return
        
    if invoice['allow_comments'] == 0 and comment:
        await callback.answer("Создатель счета запретил комментарии.", show_alert=True)
        return

    # ТРАНЗАКЦИЯ БАЛАНСА
    try:
        # Списываем у плательщика
        db.add_to_balance(user_id, currency, -amount_in_currency)
        # Зачисляем создателю
        db.add_to_balance(invoice['creator_id'], currency, amount_in_currency)
        
        # Обновляем статус счета
        if invoice['invoice_type'] == 'single':
            db.mark_invoice_paid(invoice_id)
            
        # Логируем платеж
        db.add_payment(invoice_id, user_id, currency, amount_in_currency, invoice['amount_usd'], comment, is_anonymous)
        
    except Exception as e:
        # В случае ошибки базы данных пытаемся откатить (если БД поддерживает) или уведомляем
        print(f"Error during payment transaction: {e}")
        await callback.answer("Произошла ошибка при обработке платежа. Средства не списаны.", show_alert=True)
        return

    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer()
    
    ok_msg = await bot.send_message(user_id, "👌")
    await asyncio.sleep(2)
    
    payer_text = (
        f"<tg-emoji emoji-id=\"5312043357311111246\">📥</tg-emoji> Вы оплатили счёт #{invoice_id} "
        f"на сумму <b>{format_balance(amount_in_currency)} {currency} (${invoice['amount_usd']})</b>."
    )
    if comment:
        payer_text += f"\n\n<tg-emoji emoji-id=\"5312103894875143512\">💬</tg-emoji> {comment}"
        
    try:
        await bot.send_message(user_id, payer_text, parse_mode='HTML')
    except:
        pass

    if is_anonymous:
        payer_name = "Аноним"
    else:
        try:
            user = await bot.get_chat(user_id)
            payer_name = user.full_name or user.username or "Пользователь"
        except:
            payer_name = "Пользователь"
            
    emoji_id = CRYPTO_EMOJIS.get(currency, "5310191758255099001")
    creator_text = (
        f"<b>{payer_name}</b> оплатил(а) ваш счет #{invoice_id}. "
        f"Вы получили <tg-emoji emoji-id=\"{emoji_id}\">☺️</tg-emoji> <b>{format_balance(amount_in_currency)} {currency} (${invoice['amount_usd']})</b>."
    )
    if comment:
        creator_text += f"\n\n<tg-emoji emoji-id=\"5312103894875143512\">💬</tg-emoji> {comment}"
        
    try:
        await bot.send_message(invoice['creator_id'], creator_text, parse_mode='HTML')
    except:
        pass

--- ЗАГЛУШКИ ДЛЯ ОСТАЛЬНЫХ КНОПОК ---
@dp.callback_query(lambda c: c.data in [
    "exchange", "p2p", "market", "checks",
    "cryptopay", "giveaways", "subscriptions", "settings",
    "deposit", "withdraw"
])
async def placeholder(callback: types.CallbackQuery):
    await callback.answer("Раздел пока в разработке", show_alert=True)

async def main():
    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
