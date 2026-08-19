import asyncio
import random
import string
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database

BOT_TOKEN = '8985331836:AAEQnX94VdKaezH4ybTuQNU-gDeiMaGLcW8'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# РЕАЛЬНЫЕ КУРСЫ (Обновляются автоматически)
REAL_RATES = {}
BACKUP_RATES = {
    "usdt": 1.0, "usdc": 1.0, "btc": 65000, "eth": 3500, "sol": 150,
    "gram": 0.007, "trx": 0.12, "doge": 0.15, "ltc": 70, "bnb": 600, "xaut": 2300
}

async def fetch_real_rates():
    """Получает реальные курсы с CoinGecko"""
    global REAL_RATES
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,tron,dogecoin,litecoin,binancecoin,tether,toncoin&vs_currencies=usd"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                mapping = {
                    "bitcoin": "btc", "ethereum": "eth", "solana": "sol", "tron": "trx",
                    "dogecoin": "doge", "litecoin": "ltc", "binancecoin": "bnb",
                    "tether": "usdt", "toncoin": "gram"
                }
                for coin, key in mapping.items():
                    if coin in data:
                        REAL_RATES[key] = data[coin]["usd"]
                print("✅ Курсы обновлены:", REAL_RATES)
    except Exception as e:
        print(f"⚠️ Ошибка обновления курсов: {e}")

def get_rate(currency: str) -> float:
    curr_lower = currency.lower()
    return REAL_RATES.get(curr_lower, BACKUP_RATES.get(curr_lower, 0))

def format_balance(value):
    if value == 0: return "0"
    return f"{value:.8f}".rstrip('0').rstrip('.')

def get_usd_value(amount, currency):
    val = amount * get_rate(currency)
    return f"{val:.2f}" if val >= 0.01 else "< 0.01"

# Генерация изображения чека (как на скриншоте)
async def generate_check_image(currency, amount):
    usd_val = get_usd_value(amount, currency)
    return (
        f"https://imggen.send.tg/checks/image?"
        f"asset={currency}&asset_amount={amount}"
        f"&fiat=USD&fiat_amount={usd_val}"
        f"&main=asset&v4"
    )

# Клавиатуры
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кошелёк", callback_data="wallet"), InlineKeyboardButton(text="Обмен", callback_data="exchange")],
    [InlineKeyboardButton(text="P2P", callback_data="p2p"), InlineKeyboardButton(text="Биржа", callback_data="market")],
    [InlineKeyboardButton(text="Чеки", callback_data="checks"), InlineKeyboardButton(text="Счета", callback_data="invoices")],
    [InlineKeyboardButton(text="Настройки", callback_data="settings")]
])

wallet_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пополнить", callback_data="deposit"), InlineKeyboardButton(text="Вывести", callback_data="withdraw")],
    [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")]
])

# Состояния для создания чека
class CheckFSM(StatesGroup):
    selecting_currency = State()
    entering_amount = State()

# ================= ХЕНДЛЕРЫ =================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()
    # Проверка на активацию чека по ссылке
    if len(args) > 1 and args[1].startswith("check_"):
        await activate_check(message, args[1].replace("check_", ""))
        return
        
    db.add_user(message.from_user.id)
    text = (
        "<tg-emoji emoji-id='5361914370068613491'></tg-emoji> Мультивалютный криптокошелек\n\n"
        "Покупайте, продавайте, храните,\nотправляйте и платите криптовалютой."
    )
    await message.answer(text, parse_mode='HTML', reply_markup=main_kb)

@dp.callback_query(lambda c: c.data == "wallet")
async def open_wallet(cb: types.CallbackQuery):
    b = db.get_all_balances(cb.from_user.id)
    if not b: b = {k: 0.0 for k in ["USDT","GRAM","SOL","TRX","BTC","ETH","DOGE","LTC","BNB","USDC","XAUT"]}
    
    total_btc = sum([b[c] * get_rate(c) / get_rate("BTC") for c in b if c != 'user_id'])
    
    text = f"<b><tg-emoji emoji-id='5310191758255099001'>👛</tg-emoji> Кошелек</b>\n\n"
    for curr in ["USDT","GRAM","SOL","TRX","BTC","ETH","DOGE","LTC","BNB","USDC","XAUT"]:
        if b.get(curr, 0) > 0 or curr in ["USDT", "BTC"]:
            text += f"<tg-emoji emoji-id='5406841020769936275'>☺️</tg-emoji> {curr}: {format_balance(b[curr])}\n"
            
    text += f"\n≈ {format_balance(total_btc)} BTC"
    await cb.message.edit_text(text, parse_mode='HTML', reply_markup=wallet_kb)
    await cb.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_main(cb: types.CallbackQuery):
    await cb.message.edit_text("<tg-emoji emoji-id='5361914370068613491'>👛</tg-emoji> Главное меню", parse_mode='HTML', reply_markup=main_kb)
    await cb.answer()

# --- СИСТЕМА ЧЕКОВ ---

@dp.callback_query(lambda c: c.data == "checks")
async def checks_menu(cb: types.CallbackQuery):
    active = db.get_user_checks(cb.from_user.id)
    text = "Здесь вы можете создавать чек для мгновенной отправки криптовалюты любому пользователю.\n<a href='https://telegra.ph/Checks-Instruction'>Смотреть инструкцию ›</a>"
    
    btns = [[InlineKeyboardButton(text="Создать чек", callback_data="create_check_start")]]
    if active:
        btns.insert(1, [InlineKeyboardButton(text=f"📂 Активные чеки ({len(active)})", callback_data="my_active_checks")])
    btns.append([InlineKeyboardButton(text="‹ Назад", callback_data="back_to_main")])
    
    await cb.message.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    await cb.answer()

@dp.callback_query(lambda c: c.data == "create_check_start")
async def create_check_start(cb: types.CallbackQuery, state: FSMContext):
    balances = db.get_all_balances(cb.from_user.id)
    available = [(c, b) for c, b in balances.items() if c != 'user_id' and b * get_rate(c) >= 0.02]
    
    if not available:
        txt = "Недостаточно монет. Минимальная сумма чека $0.02.\nСначала пополните баланс!"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад к чекам", callback_data="checks")]])
        await cb.message.edit_text(txt, reply_markup=kb)
    else:
        await state.set_state(CheckFSM.selecting_currency)
        rows = []
        temp = []
        for curr, bal in available:
            temp.append(InlineKeyboardButton(text=f"{curr} ({format_balance(bal)})", callback_data=f"sel_curr_{curr}"))
            if len(temp) == 2: rows.append(temp); temp = []
        if temp: rows.append(temp)
        rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="checks")])
        
        await cb.message.edit_text("Выберите криптовалюту для чека:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@dp.callback_query(CheckFSM.selecting_currency, lambda c: c.data.startswith("sel_curr_"))
async def select_curr(cb: types.CallbackQuery, state: FSMContext):
    curr = cb.data.replace("sel_curr_", "")
    await state.update_data(currency=curr)
    await state.set_state(CheckFSM.entering_amount)
    
    txt = f"Пришлите сумму чека в {curr}.\nДля мультичека введите кратную балансу сумму одной активации."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Назад", callback_data="create_check_start")]])
    await cb.message.edit_text(txt, reply_markup=kb)
    await cb.answer()

@dp.message(CheckFSM.entering_amount)
async def process_amount(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    curr = data['currency']
    
    try: amount = float(msg.text.replace(',', '.'))
    except: 
        await msg.answer("Введите число."); return
        
    min_usd = 0.02
    if amount * get_rate(curr) < min_usd:
        await msg.answer(f"Минимум ${min_usd}. Для {curr} это ~{min_usd/get_rate(curr):.4f}."); return
        
    bal = db.get_balance(msg.from_user.id, curr)
    if bal < amount:
        await msg.answer("Недостаточно средств."); await state.clear(); return
        
    # Создание чека
    db.update_balance(msg.from_user.id, curr, -amount)
    cid = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    db.create_check(cid, msg.from_user.id, curr, amount)
    
    img = await generate_check_image(curr, amount)
    usd = get_usd_value(amount, curr)
    cap = (
        f"<b>Чек</b>\n\nСумма: {amount} {curr} (${usd})\n\n"
        f"Любой может активировать этот чек.\n\n"
        f"Ссылка: <code>https://t.me/{bot.username}?start=check_{cid}</code>\n\n"
        f"️ Никогда не делайте скриншот чека!"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Конвертировать в подарок", callback_data="gift")],
        [InlineKeyboardButton(text="Поделиться чеком", switch_inline_query=cid)],
        [InlineKeyboardButton(text="Удалить чек", callback_data=f"del_chk_{cid}")],
        [InlineKeyboardButton(text="‹ Назад к списку", callback_data="my_active_checks")]
    ])
    
    await msg.answer_photo(photo=img, caption=cap, parse_mode='HTML', reply_markup=kb)
    await state.clear()

@dp.callback_query(lambda c: c.data == "my_active_checks")
async def my_checks(cb: types.CallbackQuery):
    checks = db.get_user_checks(cb.from_user.id)
    if not checks:
        await cb.answer("Нет активных чеков", show_alert=True); return
        
    rows = []
    for ch in checks[:10]:
        usd = get_usd_value(ch['amount'], ch['currency'])
        rows.append([InlineKeyboardButton(text=f"{ch['currency']} {ch['amount']} (${usd})", callback_data=f"manage_{ch['id']}")])
    rows.append([InlineKeyboardButton(text="‹ Назад", callback_data="checks")])
    
    await cb.message.edit_text("Ваши активные чеки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@dp.callback_query(lambda c: c.data.startswith("manage_"))
async def manage_cb(cb: types.CallbackQuery):
    cid = cb.data.replace("manage_", "")
    ch = db.get_check(cid)
    if not ch or ch['creator_id'] != cb.from_user.id:
        await cb.answer("Чек не найден", show_alert=True); return
        
    img = await generate_check_image(ch['currency'], ch['amount'])
    usd = get_usd_value(ch['amount'], ch['currency'])
    cap = f"<b>Чек</b>\n\nСумма: {ch['amount']} {ch['currency']} (${usd})\n\n<code>https://t.me/{bot.username}?start=check_{cid}</code>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться", switch_inline_query=cid)],
        [InlineKeyboardButton(text="Удалить чек", callback_data=f"del_chk_{cid}")],
        [InlineKeyboardButton(text="‹ Назад", callback_data="my_active_checks")]
    ])
    
    try: await cb.message.edit_media(InputMediaPhoto(media=img, caption=cap, parse_mode='HTML'), reply_markup=kb)
    except: await cb.message.edit_text(cap, parse_mode='HTML', reply_markup=kb)
    await cb.answer()

@dp.callback_query(lambda c: c.data.startswith("del_chk_"))
async def del_check(cb: types.CallbackQuery):
    cid = cb.data.replace("del_chk_", "")
    if db.delete_check(cid, cb.from_user.id):
        await cb.message.delete()
        await cb.answer("Чек удален. Средства возвращены.", show_alert=True)
    else:
        await cb.answer("Ошибка удаления", show_alert=True)

# АКТИВАЦИЯ ЧЕКА
async def activate_check(msg: types.Message, check_id: str):
    ch = db.get_check(check_id)
    if not ch or not ch['is_active']:
        await msg.answer("Чек недействителен."); return
    if msg.from_user.id == ch['creator_id']:
        await msg.answer("Это ваш чек."); return
        
    db.update_balance(msg.from_user.id, ch['currency'], ch['amount'])
    db.activate_check(check_id, msg.from_user.id)
    
    usd = get_usd_value(ch['amount'], ch['currency'])
    await msg.answer(
        f"<tg-emoji emoji-id='5312043357311111246'></tg-emoji> Вы получили "
        f"<b>{ch['amount']} {ch['currency']}</b> (<b>${usd}</b>)", parse_mode='HTML'
    )
    
    # Уведомление создателю
    try:
        await bot.send_message(ch['creator_id'], 
            f"<tg-emoji emoji-id='5311998535032409760'>🦋</tg-emoji> "
            f"<a href='tg://user?id={msg.from_user.id}'>{msg.from_user.first_name}</a> активировал(а) ваш чек "
            f"и получил(а) <b>{ch['amount']} {ch['currency']}</b> (<b>${usd}</b>)", parse_mode='HTML')
    except: pass

# ИНЛАЙН РЕЖИМ (Создание и Активация)
@dp.inline_query()
async def inline_handler(query: types.InlineQuery):
    txt = query.query.strip()
    uid = query.from_user.id
    
    # Попытка создать чек (если введено число)
    try:
        amt = float(txt)
        bals = db.get_all_balances(uid)
        results = []
        for c, b in bals.items():
            if c == 'user_id': continue
            if b >= amt:
                usd = get_usd_value(amt, c)
                results.append(types.InlineQueryResultArticle(
                    id=f"cr_{c}_{amt}", title=f"Чек на {amt} {c}",
                    description=f"Баланс: {b} {c} (${get_usd_value(b,c)})",
                    input_message_content=types.InputTextMessageContent(message_text=f"Создание чека..."),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Создать", callback_data=f"icr_{c}_{amt}")]])
                ))
        if results: await query.answer(results, cache_time=0, is_personal=True)
        else: await query.answer([], cache_time=0)
    except ValueError:
        # Попытка активации (если введен ID чека)
        ch = db.get_check(txt)
        if ch and ch['is_active']:
            usd = get_usd_value(ch['amount'], ch['currency'])
            res = [types.InlineQueryResultArticle(
                id=txt, title=f"Получить {ch['amount']} {ch['currency']}",
                description=f"${usd}",
                input_message_content=types.InputTextMessageContent(message_text="Активация чека..."),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Активировать", callback_data=f"act_{txt}")]])
            )]
            await query.answer(res, cache_time=0)
        else:
            await query.answer([], cache_time=0)

@dp.callback_query(lambda c: c.data.startswith("icr_"))
async def inline_create(cb: types.CallbackQuery):
    parts = cb.data.replace("icr_", "").split("_")
    curr, amt_str = parts[0], "_".join(parts[1:])
    try: amt = float(amt_str)
    except: await cb.answer("Ошибка", show_alert=True); return
    
    if db.get_balance(cb.from_user.id, curr) < amt:
        await cb.answer("Недостаточно средств", show_alert=True); return
        
    db.update_balance(cb.from_user.id, curr, -amt)
    cid = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    db.create_check(cid, cb.from_user.id, curr, amt)
    
    img = await generate_check_image(curr, amt)
    usd = get_usd_value(amt, curr)
    cap = f"<b>Чек</b>\n\n{amt} {curr} (${usd})\n\n<code>https://t.me/{bot.username}?start=check_{cid}</code>"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться", switch_inline_query=cid)],
        [InlineKeyboardButton(text="Удалить", callback_data=f"del_chk_{cid}")]
    ])
    
    await cb.message.edit_media(InputMediaPhoto(media=img, caption=cap, parse_mode='HTML'), reply_markup=kb)
    await cb.answer("Чек создан!")

@dp.callback_query(lambda c: c.data.startswith("act_"))
async def inline_activate(cb: types.CallbackQuery):
    cid = cb.data.replace("act_", "")
    ch = db.get_check(cid)
    if not ch or not ch['is_active']:
        await cb.answer("Чек уже активирован!", show_alert=True); return
    if cb.from_user.id == ch['creator_id']:
        await cb.answer("Нельзя активировать свой чек!", show_alert=True); return
        
    db.update_balance(cb.from_user.id, ch['currency'], ch['amount'])
    db.activate_check(cid, cb.from_user.id)
    
    usd = get_usd_value(ch['amount'], ch['currency'])
    await cb.message.edit_text(
        f"<tg-emoji emoji-id='5312043357311111246'>📥</tg-emoji> Вы получили "
        f"<b>{ch['amount']} {ch['currency']}</b> (<b>${usd}</b>)", parse_mode='HTML'
    )
    
    try:
        await bot.send_message(ch['creator_id'],
            f"<tg-emoji emoji-id='5311998535032409760'>🦋</tg-emoji> "
            f"<a href='tg://user?id={cb.from_user.id}'>{cb.from_user.first_name}</a> активировал(а) чек "
            f"на <b>{ch['amount']} {ch['currency']}</b> (<b>${usd}</b>)", parse_mode='HTML')
    except: pass
    await cb.answer("Активировано!")

# Заглушки
@dp.callback_query(lambda c: c.data in ["exchange","p2p","market","invoices","settings","deposit","withdraw","gift"])
async def placeholder(cb: types.CallbackQuery):
    await cb.answer("Раздел в разработке", show_alert=True)

async def main():
    print("🚀 Бот запущен с реальными курсами...")
    await fetch_real_rates()
    # Обновляем курсы каждую минуту
    async def rate_updater():
        while True:
            await fetch_real_rates()
            await asyncio.sleep(60)
            
    asyncio.create_task(rate_updater())
    
    try: await dp.start_polling(bot)
    finally: db.close()

if __name__ == '__main__':
    asyncio.run(main())
