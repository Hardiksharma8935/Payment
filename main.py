import asyncio
import logging
import random
import urllib.parse
from datetime import datetime
from aiogram import Bot, Dispatcher, F, BaseMiddleware
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import config
from database import init_db, AsyncSessionLocal, User, PurchaseHistory, get_user, SecurityLog

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

EXCHANGE_RATE = 85.0

GROUPS = {
    "g1": {"name": "Stripchat", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004445000742", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADyh4AAmjCeUaIxOc4OANLJxYE"},
    "g2": {"name": "Indian Students", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004458938934", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADiR4AAmjCeUastMuPKJmT_hYE"},
    "g3": {"name": "Pure tamil", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003893753935", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADix4AAmjCeUaiYnw8VfpWHxYE"},
    "g4": {"name": "Forced", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1003997365417", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjB4AAmjCeUZFY7dmTyGcVBYE"},
    "g5": {"name": "self made ", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003589926855", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjh4AAmjCeUY17uH7NGywPhYE"},
    "g6": {"name": "hidden secret", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004407356883", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlB4AAmjCeUYrdi34PirAWhYE"},
    "g7": {"name": "bad parents", "price": 149, "usd_price": 3, "stars": 133, "chat_id": "-1003969174282", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlR4AAmjCeUZGaDMBp5MGoBYE"},
    "g8": {"name": "fingerings", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004435164752", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmh4AAmjCeUb7rxcaimfZWxYE"},
    "g9": {"name": "dickflash", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003870700155", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADoB4AAmjCeUZIwdgTLPeNlxYE"},
    "g10": {"name": "car videos", "price": 49, "usd_price": 3, "stars": 133, "chat_id": "-1004351633034", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADox4AAmjCeUbkZylaMcGdpBYE"},
    "g11": {"name": "ip cam cctv", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003739836678", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADpR4AAmjCeUbG-D-ej2NRmRYE"},
    "g12": {"name": "only fans", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1003960924467", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADqR4AAmjCeUYp7NSXggaRfBYE"},
    "g13": {"name": "Indian cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003985171544", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD-wwAAhoLqUZbB0VsNbmtkhYE"},
    "g14": {"name": "Arbic Stuffs", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004409206399", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADrR4AAmjCeUZrD1n7ZSUqFxYE"},
    "g15": {"name": "mallu", "price": 99, "usd_price": 3, "stars": 133, "chat_id": "-1004320995574", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADUAwAAmjCgUbyd4xysXvrtxYE"},
    "g16": {"name": "All In One ", "price": 499, "usd_price": 10, "stars": 833, "chat_id": "-1003599861740", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmA0AAmjCgUYg1UY_ofR7vxYE"},
    "g17": {"name": " mom son ", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1003688683917", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADfRQAAghnMUYQOCV4bNnbxBYE"},
    "g18": {"name": " pakistani Cxp", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1003928326633", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD8QkAAp4PiEZ7T8vtPnvP7BYE"},
    "g19": {"name": " tamil cxp ", "price": 199, "usd_price": 3, "stars": 133, "chat_id": "-1004462050531", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD_wkAAp4PiEaDKqDxyG7DNxYE"},
    "g20": {"name": " foreign cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1004458448520", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"},
    "g21": {"name": " Gay cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1004435458777", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"}
    "g22": {"name": " Spy ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003864900874", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"}
    "g23": {"name": " Mallu cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003993043440", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"}
    "g24": {"name": " All Links In One ", "price": 799, "usd_price": 20, "stars": 933, "chat_id": "-1003599861740", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"}

}


# Configurable Crypto Addresses
USDT_ADDRESS = config.USDT_ADDRESS
BTC_ADDRESS = config.BTC_ADDRESS
ETH_ADDRESS = config.ETH_ADDRESS
SOL_ADDRESS = config.SOL_ADDRESS

# Security Config
THROTTLING_CACHE = {}  # Format: {user_id: last_timestamp}
BANNED_USERS = set()   # In-memory Shadow Ban List

# ==========================================
# 🛑 MIDDLEWARES (Rate Limiting & Shadow Ban)
# ==========================================
class SecurityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
            
        # 1. Shadow Ban Filter
        if user.id in BANNED_USERS:
            return  # Completely drop the execution silently

        # 2. Rate Limiting (Anti-Flood)
        now = datetime.utcnow().timestamp()
        last_time = THROTTLING_CACHE.get(user.id, 0)
        
        if now - last_time < 1.0:  # 1 message per second constraint
            THROTTLING_CACHE[user.id] = now
            if isinstance(event, Message):
                async with AsyncSessionLocal() as session:
                    log = SecurityLog(user_id=user.id, username=user.username, reason="Flood/Throttling Limit Triggered")
                    session.add(log)
                    await session.commit()
                return await event.answer("⚠️ System Warning: Please do not spam inputs.")
            return

        THROTTLING_CACHE[user.id] = now
        return await handler(event, data)

dp.message.middleware(SecurityMiddleware())
dp.callback_query.middleware(SecurityMiddleware())

# ==========================================
# 🗂 STATES
# ==========================================
class PaymentState(StatesGroup):
    waiting_for_currency = State()
    waiting_for_amount = State()
    waiting_for_screenshot = State()
    waiting_for_amazon_card = State()
    broadcast_msg = State()
    captcha_verification = State()

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
        [InlineKeyboardButton(text="🇺🇸 Deposit in USD ($)", callback_data=f"curr_USD")]
    ])

def payment_methods_kb(intent: str, param: str, currency: str = "INR"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Crypto (USDT, BTC, ETH, SOL...)", callback_data=f"method_cryptomenu_{intent}_{param}_{currency}")],
        [InlineKeyboardButton(text="💳 UPI", callback_data=f"method_upi_{intent}_{param}_{currency}")],
        [InlineKeyboardButton(text="🎁 Amazon Gift Card", callback_data=f"method_amazon_{intent}_{param}_{currency}"),
         InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data=f"method_stars_{intent}_{param}_{currency}")]
    ])

def crypto_selection_kb(intent: str, param: str, currency: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="₮ USDT", callback_data=f"method_crypto_USDT_{intent}_{param}_{currency}"),
         InlineKeyboardButton(text="₿ BTC", callback_data=f"method_crypto_BTC_{intent}_{param}_{currency}")],
        [InlineKeyboardButton(text="🔷 ETH", callback_data=f"method_crypto_ETH_{intent}_{param}_{currency}"),
         InlineKeyboardButton(text="🟣 SOL", callback_data=f"method_crypto_SOL_{intent}_{param}_{currency}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data=f"method_back_{intent}_{param}_{currency}")]
    ])

def i_paid_kb(intent: str, param: str, method: str, currency: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I paid", callback_data=f"ipaid_{method}_{intent}_{param}_{currency}")]
    ])

def admin_approval_kb(user_id: int, intent: str, param: str, currency: str, method: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"appr_{intent}_{user_id}_{param}_{currency}_{method}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_{intent}_{user_id}_{param}_{currency}_{method}")]
    ])

# ==========================================
# 🛑 CAPTCHA SYSTEM (Anti-Bot Verification)
# ==========================================
@dp.message(CommandStart(), StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    correct_ans = num1 + num2
    
    await state.update_data(captcha_ans=correct_ans)
    await state.set_state(PaymentState.captcha_verification)
    
    await message.answer(f"🤖 **Human Verification Required**\nTo maintain compliance, please solve this math problem:\n\n👉 What is `{num1} + {num2}`?", parse_mode="Markdown")

@dp.message(StateFilter(PaymentState.captcha_verification))
async def process_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    expected = data.get("captcha_ans")
    
    try:
        user_ans = int(message.text.strip())
        if user_ans == expected:
            await state.clear()
            async with AsyncSessionLocal() as session:
                await get_user(session, message.from_user.id)
            await message.answer("✅ Verification Successful!", reply_markup=main_menu_kb())
        else:
            raise ValueError
    except ValueError:
        async with AsyncSessionLocal() as session:
            log = SecurityLog(user_id=message.from_user.id, username=message.from_user.username, reason="Failed Verification Attempt")
            session.add(log)
            await session.commit()
        await message.answer("❌ Incorrect answer. Please type `/start` to try again.")

# ==========================================
# 🛑 GLOBAL CANCEL & MENU HANDLERS
# ==========================================
MENU_COMMANDS = ["🛒 Buy Groups", "👤 Profile & Wallet", "📂 Demo Channels", "📜 Purchase History", "📢 Main Channel", "📞 Contact Admin", "🔙 Back to Main Menu"]

@dp.message(F.text.in_(MENU_COMMANDS), StateFilter('*'))
async def handle_menu_buttons(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        await get_user(session, message.from_user.id)

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

# ==========================================
# 📢 SECURITY DASHBOARD & ADMIN COMMANDS
# ==========================================
@dp.message(Command("security"))
async def cmd_security_dashboard(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(5))
        logs = result.scalars().all()
        
    text = "🛡️ **Security & Anti-Abuse Controls**\n\n**Recent Suspicious Logs:**\n"
    if not logs:
        text += "_No recent security triggers._\n"
    for l in logs:
        text += f"• `{l.user_id}` (@{l.username}) - {l.reason}\n"
        
    text += "\n**Quick Tools:**\n`/shadowban <user_id>`\n`/shadowunban <user_id>`"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("shadowban"))
async def cmd_shadowban(message: Message, command: Command):
    if message.from_user.id != config.OWNER_ID:
        return
    try:
        target_id = int(command.args.strip())
        BANNED_USERS.add(target_id)
        await message.answer(f"🔒 User `{target_id}` added to shadowban list.", parse_mode="Markdown")
    except Exception:
        await message.answer("Usage: `/shadowban <user_id>`")

@dp.message(Command("shadowunban"))
async def cmd_shadowunban(message: Message, command: Command):
    if message.from_user.id != config.OWNER_ID:
        return
    try:
        target_id = int(command.args.strip())
        BANNED_USERS.discard(target_id)
        await message.answer(f"🔓 User `{target_id}` removed from shadowban list.", parse_mode="Markdown")
    except Exception:
        await message.answer("Usage: `/shadowunban <user_id>`")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if message.from_user.id == config.OWNER_ID:
        await message.answer("📢 Send the message (Text or Photo) you want to broadcast to all users:")
        await state.set_state(PaymentState.broadcast_msg)

@dp.message(StateFilter(PaymentState.broadcast_msg))
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id))
        users = result.scalars().all()
        
    if not users:
        return await message.answer("No users found in the database.")
        
    sent, failed, blocked, deleted = 0, 0, 0, 0
    await message.answer(f"Starting broadcast to {len(users)} users. This may take a while...")
    
    for uid in users:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except TelegramForbiddenError:
            blocked += 1
        except TelegramBadRequest:
            deleted += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
            
    stats = (
        f"✅ **Broadcast Complete!**\n\n"
        f"👥 Total Users: {len(users)}\n"
        f"✅ Successful: {sent}\n"
        f"🚫 Blocked Bot: {blocked}\n"
        f"👻 Deleted Accs: {deleted}\n"
        f"❌ Failed Other: {failed}"
    )
    await message.answer(stats, parse_mode="Markdown")

@dp.message(Command("addbalance", "removebalance"))
async def manual_balance_update(message: Message, command: Command):
    if message.from_user.id != config.OWNER_ID:
        return
    try:
        args = command.args.split()
        if len(args) != 2:
            raise ValueError
            
        target_id = int(args[0])
        amount_inr = float(args[1])
        amount_usd = amount_inr / EXCHANGE_RATE
        
        async with AsyncSessionLocal() as session:
            user = await get_user(session, target_id)
            if command.command == "addbalance":
                user.balance_inr += amount_inr
                user.balance_usd += amount_usd
                msg = f"✅ Successfully **added** ₹{amount_inr:.2f} to user `{target_id}`."
            else:
                user.balance_inr = max(0, user.balance_inr - amount_inr)
                user.balance_usd = max(0, user.balance_usd - amount_usd)
                msg = f"✅ Successfully **removed** ₹{amount_inr:.2f} from user `{target_id}`."
            await session.commit()
            
        await message.answer(msg, parse_mode="Markdown")
        
        try:
            if command.command == "addbalance":
                await bot.send_message(target_id, f"🎁 **Admin Added Balance!**\nYour wallet has been credited with **₹{amount_inr:.2f}**.", parse_mode="Markdown")
            else:
                await bot.send_message(target_id, f"⚠️ **Balance Deducted!**\n**₹{amount_inr:.2f}** has been removed from your wallet by the Admin.", parse_mode="Markdown")
        except Exception:
            pass
            
    except Exception:
        await message.answer("⚠️ **Incorrect Format!**\nUsage: `/addbalance <user_id> <amount_in_INR>`\nExample: `/addbalance 123456789 500`", parse_mode="Markdown")

# ==========================================
# 📂 DEMO CHANNELS
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
# 💳 PAYMENT PROCESSING MENUS
# ==========================================
@dp.callback_query(F.data.startswith("method_cryptomenu_"))
async def process_cryptomenu(callback: CallbackQuery):
    _, _, intent, param, currency = callback.data.split("_")
    await callback.message.edit_text(
        "💰 Please select the cryptocurrency you want to pay with:",
        reply_markup=crypto_selection_kb(intent, param, currency)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("method_back_"))
async def process_back_method(callback: CallbackQuery):
    _, _, intent, param, currency = callback.data.split("_")
    await callback.message.edit_text(
        "👇 Select your payment method:",
        reply_markup=payment_methods_kb(intent, param, currency)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("method_crypto_"))
async def process_crypto_payment(callback: CallbackQuery):
    _, _, coin, intent, param, currency = callback.data.split("_")
    
    if intent == "buy":
        group = GROUPS[param]
        amt_inr = group['price']
        amt_usd = group['usd_price']
    else:
        if currency == "INR":
            amt_inr = float(param)
            amt_usd = float(param) / EXCHANGE_RATE
        else:
            amt_usd = float(param)
            amt_inr = float(param) * EXCHANGE_RATE

    target_amount = amt_inr if currency == "INR" else amt_usd
    sym = "₹" if currency == "INR" else "$"
    
    addresses = {
        "USDT": USDT_ADDRESS,
        "BTC": BTC_ADDRESS,
        "ETH": ETH_ADDRESS,
        "SOL": SOL_ADDRESS
    }
    wallet_address = addresses.get(coin, "Not Configured")
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={wallet_address}"
    caption = (
        f"🪙 **{coin} Payment**\n\n"
        f"Amount to Send: **{sym}{target_amount:.2f}**\n\n"
        f"Network Address:\n`{wallet_address}`\n\n"
        f"Tap the address to copy it. Send the exact amount and click **✅ I paid**."
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer_photo(
        photo=qr_url, 
        caption=caption, 
        reply_markup=i_paid_kb(intent, param, coin, currency), 
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("method_amazon_"))
async def process_amazon(callback: CallbackQuery, state: FSMContext):
    _, _, intent, param, currency = callback.data.split("_")
    
    if intent == "buy":
        group = GROUPS[param]
        amt_inr = group['price']
    else:
        if currency == "INR":
            amt_inr = float(param)
        else:
            amt_inr = float(param) * EXCHANGE_RATE

    amt = amt_inr
    sym = "₹"
    
    await state.update_data(intent=intent, param=param, currency=currency, method="Amazon", amount=amt)
    await state.set_state(PaymentState.waiting_for_amazon_card)
    await callback.message.edit_text(f"🎁 **Amazon Gift Card**\n\nPlease send your **{sym}{amt:.2f}** Amazon Gift Card Code or Photo in this chat now.", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("method_stars_"))
async def process_stars(callback: CallbackQuery):
    _, _, intent, param, currency = callback.data.split("_")
    
    if intent == "buy":
        amt_usd = GROUPS[param]['usd_price']
        title = GROUPS[param]['name']
    else:
        amt_usd = float(param) if currency == "USD" else (float(param) / EXCHANGE_RATE)
        title = "Wallet Deposit"
        
    stars_cost = int(amt_usd * 50)
    payload = f"stars_{intent}_{param}_{currency}_{callback.from_user.id}_{stars_cost}"
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await bot.send_invoice(
        chat_id=callback.message.chat.id, title=title, description=f"Pay {stars_cost} Stars",
        payload=payload, provider_token="", currency="XTR",
        prices=[LabeledPrice(label=title, amount=stars_cost)]
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("method_upi_"))
async def process_upi(callback: CallbackQuery):
    _, _, intent, param, currency = callback.data.split("_")
    owner_username = config.OWNER_USERNAME.replace("@", "")
    deep_link = f"https://t.me/{owner_username}?text=UPI"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Contact Admin for UPI Payment", url=deep_link)],
        [InlineKeyboardButton(text="🔙 Back", callback_data=f"method_back_{intent}_{param}_{currency}")]
    ])
    
    await callback.message.edit_text(
        "To pay via UPI, please contact the Admin. Tap the button below.",
        reply_markup=kb
    )
    await callback.answer()

# --- AMAZON CARD HANDLER ---
@dp.message(StateFilter(PaymentState.waiting_for_amazon_card))
async def receive_amazon_card(message: Message, state: FSMContext):
    data = await state.get_data()
    sym = "₹"
    amt = data.get('amount', 0.0)
    
    caption = f"🚨 **Amazon Card Verification**\nUser: `{message.from_user.id}`\nAmount: **{sym}{amt:.2f}**\nIntent: {data['intent']}"
    await bot.send_message(config.OWNER_ID, caption, parse_mode="Markdown")
    await bot.forward_message(config.OWNER_ID, message.chat.id, message.message_id)
    await bot.send_message(config.OWNER_ID, "Approve or Reject?", reply_markup=admin_approval_kb(message.from_user.id, data['intent'], data['param'], data['currency'], data['method']))
    
    await message.answer("✅ Gift card received. Your payment has been forwarded to the Admin for verification.\nPlease wait for approval.", reply_markup=main_menu_kb())
    await state.clear()

# --- SCREENSHOT HANDLER ---
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
        f"Amount: **{sym}{amt:.2f}**"
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
            await bot.send_message(user_id, f"✅ **Payment verified successfully.**\nYour wallet has been credited with **{sym}{amt:.2f}**.", parse_mode="Markdown")
            
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
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment, StateFilter('*'))
async def successful_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("stars_"):
        _, intent, param, currency, user_id, stars = payload.split("_")
        
        async with AsyncSessionLocal() as session:
            user = await get_user(session, int(user_id))
            
            if intent == "deposit":
                amt_usd = float(param) if currency == "USD" else float(param) / EXCHANGE_RATE
                amt_inr = amt_usd * EXCHANGE_RATE
                user.balance_usd += amt_usd
                user.balance_inr += amt_inr
                await session.commit()
                sym = "₹" if currency == "INR" else "$"
                amt = amt_inr if currency == "INR" else amt_usd
                await message.answer(f"⭐️ **Stars Deposit Successful!**\nWallet credited with **{sym}{amt:.2f}**.", parse_mode="Markdown")
                
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
