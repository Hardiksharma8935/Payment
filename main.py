import asyncio
import logging
import urllib.parse
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from config import config
from database import init_db, AsyncSessionLocal, User, PurchaseHistory, get_user

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# ⚙️ GROUPS & PAYMENT SETTINGS
# ==========================================
GROUPS = {
    "g1": {"name": "Stripchat", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004445000742", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADyh4AAmjCeUaIxOc4OANLJxYE"},
    "g2": {"name": "Indian Students", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004458938934", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADiR4AAmjCeUastMuPKJmT_hYE"},
    "g3": {"name": "Pure tamil", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003893753935", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADix4AAmjCeUaiYnw8VfpWHxYE"},
    "g4": {"name": "Forced", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1003978784189", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjB4AAmjCeUZFY7dmTyGcVBYE"},
    "g5": {"name": "self made ", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003589926855", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjh4AAmjCeUY17uH7NGywPhYE"},
    "g6": {"name": "hidden secret", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004407356883", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlB4AAmjCeUYrdi34PirAWhYE"},
    "g7": {"name": "bad parents", "price": 149, "usd_price": 3, "stars": 133, "chat_id": "-1003969174282", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlR4AAmjCeUZGaDMBp5MGoBYE"},
    "g8": {"name": "fingerings", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004435164752", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmh4AAmjCeUb7rxcaimfZWxYE"},
    "g9": {"name": "dickflash", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003870700155", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADoB4AAmjCeUZIwdgTLPeNlxYE"},
    "g10": {"name": "car videos", "price": 49, "usd_price": 3, "stars": 133, "chat_id": "-1004351633034", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADox4AAmjCeUbkZylaMcGdpBYE"},
    "g11": {"name": "ip cam cctv", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003739836678", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADpR4AAmjCeUbG-D-ej2NRmRYE"},
    "g12": {"name": "only fans", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003960924467", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADqR4AAmjCeUYp7NSXggaRfBYE"},
    "g13": {"name": "Indian Teen ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003985171544", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADqh4AAmjCeUaem-bfAQORlhYE"},
    "g14": {"name": "Arbic Stuffs", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004409206399", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADrR4AAmjCeUZrD1n7ZSUqFxYE"},
    "g15": {"name": "mallu", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004320995574", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADUAwAAmjCgUbyd4xysXvrtxYE"},
    "g16": {"name": "Quality Link Group", "price": 499, "usd_price": 5, "stars": 633, "chat_id": "-1003599861740", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmA0AAmjCgUYg1UY_ofR7vxYE"},
    "g17": {"name": " mom son ", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1004336932131", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADfRQAAghnMUYQOCV4bNnbxBYE"},
    "g18": {"name": " pakistani Cxp", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1003928326633", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD8QkAAp4PiEZ7T8vtPnvP7BYE"},
    "g19": {"name": " tamil cxp ", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1004292111897", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD_wkAAp4PiEaDKqDxyG7DNxYE"}
}

UPI_ID = "Hardiksharma8935@fam"
USDT_ADDRESS = "0xba924a45fe0d1a4172d3230c767c7096d9854f97" # BEP20

EXCHANGE_RATE = 85.0

# ==========================================
# 🗂 STATES
# ==========================================
class PaymentState(StatesGroup):
    waiting_for_currency = State()
    waiting_for_amount = State()
    waiting_for_screenshot = State()
    waiting_for_amazon_card = State()
    broadcast_msg = State()

# ==========================================
# ⌨️ KEYBOARDS
# ==========================================
def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buy Groups"), KeyboardButton(text="👤 Profile & Wallet")],
            [KeyboardButton(text="📂 Demo Channels"), KeyboardButton(text="📜 Purchase History")],
            [KeyboardButton(text="📢 Main Channel"), KeyboardButton(text="📞 Contact Admin")]
        ],
        resize_keyboard=True
    )

def cancel_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Back to Main Menu")]], 
        resize_keyboard=True
    )

def buy_groups_kb():
    kb = [[KeyboardButton(text=f"📦 {data['name']} - ₹{data['price']} / ${data['usd_price']}")] for g_id, data in GROUPS.items()]
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def purchase_options_kb(g_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Buy Instantly", callback_data=f"opt_instant_{g_id}")],
        [InlineKeyboardButton(text="💰 Pay Using Wallet Balance", callback_data=f"opt_wallet_{g_id}")]
    ])

def demo_groups_kb():
    kb = [[KeyboardButton(text=f"📁 {data['name']} Demo")] for g_id, data in GROUPS.items()]
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def currency_selection_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇮🇳 Deposit in INR (₹)", callback_data="curr_INR")],
        [InlineKeyboardButton(text="🇺🇸 Deposit in USD ($)", callback_data="curr_USD")]
    ])

def payment_methods_kb(intent: str, param: str, currency: str = "INR"):
    # intent: 'deposit' or 'buy'. param is amount for deposit, g_id for buy.
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 UPI", callback_data=f"method_upi_{intent}_{param}_{currency}"),
         InlineKeyboardButton(text="₮ USDT (BEP20)", callback_data=f"method_usdt_{intent}_{param}_{currency}")],
        [InlineKeyboardButton(text="🎁 Amazon Gift Card", callback_data=f"method_amazon_{intent}_{param}_{currency}"),
         InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data=f"method_stars_{intent}_{param}_{currency}")]
    ])

def i_paid_kb(intent: str, param: str, method: str, currency: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I paid", callback_data=f"ipaid_{method}_{intent}_{param}_{currency}")]
    ])

def admin_approval_kb(user_id: int, intent: str, param: str, currency: str, method: str):
    # param = amount (deposit) or g_id (buy)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"appr_{intent}_{user_id}_{param}_{currency}_{method}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_{intent}_{user_id}_{param}_{currency}_{method}")]
    ])

# ==========================================
# 🛑 GLOBAL CANCEL & MENU HANDLERS
# ==========================================
MENU_COMMANDS = ["🛒 Buy Groups", "👤 Profile & Wallet", "📂 Demo Channels", "📜 Purchase History", "📢 Main Channel", "📞 Contact Admin", "🔙 Back to Main Menu"]

@dp.message(F.text.in_(MENU_COMMANDS), StateFilter('*'))
async def handle_menu_buttons(message: Message, state: FSMContext):
    await state.clear() # Clears any pending action automatically!
    async with AsyncSessionLocal() as session:
        await get_user(session, message.from_user.id) # Ensure user exists

    if message.text in ["🔙 Back to Main Menu", "/start"]:
        await message.answer("Main Menu:", reply_markup=main_menu_kb())
    elif message.text == "🛒 Buy Groups":
        await message.answer("Select a group to buy:", reply_markup=buy_groups_kb())
    elif message.text == "📂 Demo Channels":
        await message.answer("Select a group to see its demo:", reply_markup=demo_groups_kb())
    elif message.text == "📞 Contact Admin":
        await message.answer(f"👉 https://t.me/{config.OWNER_USERNAME}")
    elif message.text == "📢 Main Channel":
        await message.answer(f"👉 https://t.me/{config.MAIN_CHANNEL.replace('@', '')}")
    elif message.text == "👤 Profile & Wallet":
        async with AsyncSessionLocal() as session:
            user = await get_user(session, message.from_user.id)
            text = (f"👤 **Your Profile**\nID: `{user.id}`\n\n"
                    f"💰 **Wallet Balance:**\n₹{user.balance_inr:.2f}  |  ${user.balance_usd:.2f}")
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Deposit Money", callback_data="deposit_money")]])
            await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    elif message.text == "📜 Purchase History":
        async with AsyncSessionLocal() as session:
            records = (await session.execute(select(PurchaseHistory).where(PurchaseHistory.user_id == message.from_user.id).order_by(PurchaseHistory.timestamp.desc()).limit(10))).scalars().all()
            if not records:
                return await message.answer("No purchase history found.")
            text = "📜 **Your Last Purchases:**\n\n"
            for r in records:
                sym = "₹" if r.currency == "INR" else "$"
                text += f"▪️ **{r.product_name}** - {sym}{r.price}\n   Method: {r.method} | Status: {r.status}\n   Date: {r.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
            await message.answer(text, parse_mode="Markdown")

@dp.message(CommandStart(), StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        await get_user(session, message.from_user.id)
    await message.answer("Welcome to the Premium Store! 🛍️\nPlease select an option below:", reply_markup=main_menu_kb())

# ==========================================
# 📂 DEMO CHANNELS FIX
# ==========================================
@dp.message(F.text.endswith("Demo"), StateFilter('*'))
async def show_demo_content(message: Message, state: FSMContext):
    await state.clear()
    group_name = message.text.replace("📁 ", "").replace(" Demo", "")
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📺 View Demo", url=data['demo'])]])
            await message.answer(f"**{group_name} Demo:**\nClick the button below to view the demo samples.", reply_markup=kb, parse_mode="Markdown")
            return

# ==========================================
# 🛒 BUY GROUPS (Instant vs Wallet)
# ==========================================
@dp.message(F.text.startswith("📦"), StateFilter('*'))
async def show_purchase_options(message: Message, state: FSMContext):
    await state.clear()
    group_name = message.text.replace("📦 ", "").split(" - ₹")[0]
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            text = f"You selected: **{data['name']}**\nPrice: **₹{data['price']} / ${data['usd_price']}**\n\nHow would you like to pay?"
            await message.answer(text, reply_markup=purchase_options_kb(g_id), parse_mode="Markdown")
            return

@dp.callback_query(F.data.startswith("opt_instant_"))
async def instant_buy_selected(callback: CallbackQuery):
    g_id = callback.data.split("_")[2]
    await callback.message.edit_text("👇 Select your payment method for Instant Purchase:", reply_markup=payment_methods_kb("buy", g_id, "INR"))

@dp.callback_query(F.data.startswith("opt_wallet_"))
async def wallet_buy_selected(callback: CallbackQuery):
    g_id = callback.data.split("_")[2]
    group = GROUPS[g_id]
    
    async with AsyncSessionLocal() as session:
        user = await get_user(session, callback.from_user.id)
        if user.balance_inr >= group['price']:
            user.balance_inr -= group['price']
            user.balance_usd -= group['usd_price']
            
            history = PurchaseHistory(user_id=user.id, product_name=group['name'], price=group['price'], currency="INR", method="Wallet", status="Approved")
            session.add(history)
            await session.commit()
            
            try:
                link = await bot.create_chat_invite_link(chat_id=group['chat_id'], member_limit=1)
                await callback.message.answer(f"✅ **Purchase Successful using Wallet!**\n\n👉 Join here: {link.invite_link}", parse_mode="Markdown")
                await bot.send_message(config.OWNER_ID, f"🛍️ **Wallet Sale!** User `{user.id}` bought {group['name']}.")
            except Exception:
                await callback.message.answer("Payment successful, but error generating link. Admin notified.")
        else:
            await callback.answer("❌ Insufficient Wallet Balance. Please deposit money first.", show_alert=True)

# ==========================================
# 💰 DEPOSIT CURRENCY FLOW
# ==========================================
@dp.callback_query(F.data == "deposit_money")
async def ask_currency(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("💵 Which currency do you want to deposit in?", reply_markup=currency_selection_kb())

@dp.callback_query(F.data.startswith("curr_"))
async def ask_amount(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(deposit_currency=currency)
    await state.set_state(PaymentState.waiting_for_amount)
    
    sym = "₹" if currency == "INR" else "$"
    await callback.message.answer(f"Enter the amount in **{currency} ({sym})** you want to deposit (e.g., 500 or 10):", parse_mode="Markdown", reply_markup=cancel_menu_kb())
    await callback.answer()

@dp.message(StateFilter(PaymentState.waiting_for_amount))
async def process_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    currency = data.get('deposit_currency', 'INR')
    sym = "₹" if currency == "INR" else "$"
    
    try:
        amount = float(message.text.strip())
        if amount <= 0: raise ValueError
        await state.clear()
        await message.answer(f"💵 Deposit Amount: **{sym}{amount}**\n\nSelect a payment method:", reply_markup=payment_methods_kb("deposit", str(amount), currency))
    except ValueError:
        await message.answer("❌ Invalid amount. Please enter a valid number.")

# ==========================================
# 💳 PAYMENT PROCESSING
# ==========================================
@dp.callback_query(F.data.startswith("method_"))
async def process_method(callback: CallbackQuery):
    _, method, intent, param, currency = callback.data.split("_")
    
    # Calculate exact amount required
    if intent == "buy":
        group = GROUPS[param]
        amt_inr = group['price']
        amt_usd = group['usd_price']
    else:
        # Deposit
        if currency == "INR":
            amt_inr = float(param)
            amt_usd = float(param) / EXCHANGE_RATE
        else:
            amt_usd = float(param)
            amt_inr = float(param) * EXCHANGE_RATE

    if method == "upi":
        upi_url = f"upi://pay?pa={UPI_ID}&pn=PremiumStore&am={amt_inr}&cu=INR"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={urllib.parse.quote(upi_url, safe=':/?=@&')}"
        caption = f"💳 **UPI Payment**\n\nAmount: **₹{amt_inr:.2f}**\nUPI ID: `{UPI_ID}`\n\nScan QR or copy UPI ID. Click **✅ I paid** after sending."
        await callback.message.answer_photo(photo=qr_url, caption=caption, reply_markup=i_paid_kb(intent, param, method, currency), parse_mode="Markdown")

    elif method == "usdt":
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={USDT_ADDRESS}"
        caption = f"₮ **USDT (BEP20) Payment**\n\nAmount: **${amt_usd:.2f}**\nAddress: `{USDT_ADDRESS}`\n\nSend exactly to this BEP20 address. Click **✅ I paid** after sending."
        await callback.message.answer_photo(photo=qr_url, caption=caption, reply_markup=i_paid_kb(intent, param, method, currency), parse_mode="Markdown")

    elif method == "amazon":
        # BUG FIX: Shows correct INR/USD symbol
        sym = "₹" if currency == "INR" else "$"
        amt = amt_inr if currency == "INR" else amt_usd
        
        # We use FSM to catch the next message (photo/text)
        state = dp.fsm.resolve_context(bot, callback.from_user.id, callback.message.chat.id)
        await state.update_data(intent=intent, param=param, currency=currency, method=method, amount=amt)
        await state.set_state(PaymentState.waiting_for_amazon_card)
        await callback.message.answer(f"🎁 **Amazon Gift Card**\n\nPlease send your **{sym}{amt:.2f}** Amazon Gift Card Code or Photo in this chat now.", parse_mode="Markdown", reply_markup=cancel_menu_kb())

    elif method == "stars":
        stars_cost = int(amt_usd * 50) # 1 USD = 50 Stars approx
        title = "Wallet Deposit" if intent == "deposit" else GROUPS[param]['name']
        payload = f"stars_{intent}_{param}_{currency}_{callback.from_user.id}_{stars_cost}"
        
        await bot.send_invoice(
            chat_id=callback.message.chat.id, title=title, description=f"Pay {stars_cost} Stars",
            payload=payload, provider_token="", currency="XTR",
            prices=[LabeledPrice(label=title, amount=stars_cost)]
        )
    await callback.answer()

# --- AMAZON CARD HANDLER ---
@dp.message(StateFilter(PaymentState.waiting_for_amazon_card))
async def receive_amazon_card(message: Message, state: FSMContext):
    data = await state.get_data()
    sym = "₹" if data['currency'] == "INR" else "$"
    
    caption = f"🚨 **Amazon Card Verification**\nUser: `{message.from_user.id}`\nAmount: **{sym}{data['amount']:.2f}**\nIntent: {data['intent']}"
    await bot.send_message(config.OWNER_ID, caption, parse_mode="Markdown")
    await bot.forward_message(config.OWNER_ID, message.chat.id, message.message_id)
    await bot.send_message(config.OWNER_ID, "Approve or Reject?", reply_markup=admin_approval_kb(message.from_user.id, data['intent'], data['param'], data['currency'], data['method']))
    
    await message.answer("✅ Gift card received. Your payment has been forwarded to the Admin for verification.\nPlease wait for approval.")
    await state.clear()

# --- SCREENSHOT HANDLER (BUG FIX: 8) ---
@dp.callback_query(F.data.startswith("ipaid_"))
async def handle_i_paid(callback: CallbackQuery, state: FSMContext):
    _, method, intent, param, currency = callback.data.split("_")
    await state.update_data(method=method, intent=intent, param=param, currency=currency)
    await state.set_state(PaymentState.waiting_for_screenshot)
    await callback.message.answer("📸 Please send your **Payment Screenshot** here now.", parse_mode="Markdown", reply_markup=cancel_menu_kb())
    await callback.answer()

@dp.message(StateFilter(PaymentState.waiting_for_screenshot), F.photo)
async def handle_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    intent, param, currency, method = data['intent'], data['param'], data['currency'], data['method']
    
    if intent == "buy":
        amt = GROUPS[param]['price'] if currency == "INR" else GROUPS[param]['usd_price']
    else:
        amt = float(param)
        
    sym = "₹" if currency == "INR" else "$"
    
    caption = (
        f"🚨 **New {method.upper()} Payment Proof**\n"
        f"User: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"ID: `{message.from_user.id}`\n"
        f"Intent: **{intent.upper()}**\n"
        f"Amount: **{sym}{amt}**"
    )
    
    await bot.send_photo(
        chat_id=config.OWNER_ID, photo=message.photo[-1].file_id, 
        caption=caption, reply_markup=admin_approval_kb(message.from_user.id, intent, param, currency, method), parse_mode="Markdown"
    )
    
    await message.answer("✅ **Payment proof sent successfully.**\nYour payment has been forwarded to the Admin for verification.\nPlease wait for approval.", reply_markup=main_menu_kb(), parse_mode="Markdown")
    await state.clear()

# ==========================================
# 🔧 ADMIN ACTIONS (Approval / Rejection)
# ==========================================
@dp.callback_query(F.data.startswith("appr_"))
async def approve_payment(callback: CallbackQuery):
    _, intent, user_id, param, currency, method = callback.data.split("_")
    user_id = int(user_id)
    
    async with AsyncSessionLocal() as session:
        user = await get_user(session, user_id)
        
        if intent == "deposit":
            amt = float(param)
            if currency == "INR":
                user.balance_inr += amt
                user.balance_usd += amt / EXCHANGE_RATE
            else:
                user.balance_usd += amt
                user.balance_inr += amt * EXCHANGE_RATE
            await session.commit()
            
            sym = "₹" if currency == "INR" else "$"
            await bot.send_message(user_id, f"✅ **Payment verified successfully.**\nYour wallet has been credited with **{sym}{amt}**.", parse_mode="Markdown")
            
        elif intent == "buy":
            group = GROUPS[param]
            history = PurchaseHistory(user_id=user.id, product_name=group['name'], price=group['price'], currency="INR", method=method, status="Approved")
            session.add(history)
            await session.commit()
            try:
                link = await bot.create_chat_invite_link(chat_id=group['chat_id'], member_limit=1)
                await bot.send_message(user_id, f"✅ **Payment verified successfully.**\nHere is your invite link:\n👉 {link.invite_link}", parse_mode="Markdown")
            except Exception:
                await bot.send_message(user_id, "Payment verified, but error generating link. Admin notified.")
                
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply("✅ Approved.")

@dp.callback_query(F.data.startswith("rej_"))
async def reject_payment(callback: CallbackQuery):
    _, intent, user_id, param, currency, method = callback.data.split("_")
    user_id = int(user_id)
    
    if intent == "buy":
        group = GROUPS[param]
        async with AsyncSessionLocal() as session:
            history = PurchaseHistory(user_id=user_id, product_name=group['name'], price=group['price'], currency="INR", method=method, status="Rejected")
            session.add(history)
            await session.commit()
            
    await bot.send_message(user_id, "❌ **Your payment could not be verified.**\nPlease contact support or upload a valid payment proof.", parse_mode="Markdown")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply("❌ Rejected.")

# --- Stars Automatic Handler ---
@dp.message(F.successful_payment, StateFilter('*'))
async def successful_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("stars_"):
        _, intent, param, currency, user_id, stars = payload.split("_")
        
        async with AsyncSessionLocal() as session:
            user = await get_user(session, int(user_id))
            
            if intent == "deposit":
                amt_usd = float(param)
                amt_inr = amt_usd * EXCHANGE_RATE
                user.balance_usd += amt_usd
                user.balance_inr += amt_inr
                await session.commit()
                await message.answer(f"⭐️ **Stars Deposit Successful!**\nWallet credited with **${amt_usd}**.", parse_mode="Markdown")
                
            elif intent == "buy":
                group = GROUPS[param]
                history = PurchaseHistory(user_id=user.id, product_name=group['name'], price=group['price'], currency="INR", method="Stars", status="Approved")
                session.add(history)
                await session.commit()
                try:
                    link = await bot.create_chat_invite_link(chat_id=group['chat_id'], member_limit=1)
                    await message.answer(f"⭐️ **Stars Payment Successful!**\nJoin here:\n👉 {link.invite_link}", parse_mode="Markdown")
                except Exception:
                    pass

# ==========================================
# 🚀 INITIALIZATION
# ==========================================
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
