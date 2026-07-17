import asyncio
import logging
import random
import time
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
from sqlalchemy import select, update
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import config
from database import init_db, AsyncSessionLocal, User, PurchaseHistory, SecurityLog, get_user

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

EXCHANGE_RATE = 85.0

# ==========================================
# ⚙️ GROUPS & PAYMENT SETTINGS
# ==========================================
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
    "g21": {"name": " Gay cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1004435458777", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"},
    "g22": {"name": " Spy ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003864900874", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"},
    "g23": {"name": " Mallu cxp ", "price": 199, "usd_price": 5, "stars": 233, "chat_id": "-1003993043440", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"},
    "g24": {"name": " All Links In One ", "price": 799, "usd_price": 20, "stars": 933, "chat_id": "-1003599861740", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD9QgAAhoLqUYNLwST4Tz1jxYE"}

}

# Configuration Addresses
USDT_ADDRESS = config.USDT_ADDRESS
BTC_ADDRESS = config.BTC_ADDRESS
ETH_ADDRESS = config.ETH_ADDRESS
SOL_ADDRESS = config.SOL_ADDRESS

# ==========================================
# 🛑 ANTI-ABUSE MIDDLEWARE (Rate Limit & Shadow Ban)
# ==========================================
THROTTLING_CACHE = {}  # {user_id: [timestamps]}
BANNED_USERS = set()

class SecurityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
            
        if user.id in BANNED_USERS:
            return # Silent drop for shadowbanned users

        now = time.time()
        timestamps = THROTTLING_CACHE.get(user.id, [])
        # Keep timestamps from the last 3 seconds
        timestamps = [t for t in timestamps if now - t < 3.0]
        timestamps.append(now)
        THROTTLING_CACHE[user.id] = timestamps
        
        # If more than 5 messages in 3 seconds -> Suspected Bot/Spammer
        if len(timestamps) > 5:
            if len(timestamps) == 6: # Log once per burst
                async with AsyncSessionLocal() as session:
                    log = SecurityLog(user_id=user.id, username=user.username, reason="Burst Rate Limit (Spam)")
                    session.add(log)
                    await session.commit()
                if isinstance(event, Message):
                    await event.answer("⚠️ You are sending requests too fast. Please slow down.")
            return # Drop execution
            
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
            [KeyboardButton(text="📢 Main Channel"), KeyboardButton(text="🤝 Referral Program")],
            [KeyboardButton(text="📞 Contact Admin")]
        ],
        resize_keyboard=True
    )

def cancel_menu_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Back to Main Menu")]], resize_keyboard=True)

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
# 🔗 SAFE INVITE GENERATOR (Retry & Wallet Refund System)
# ==========================================
async def safe_invite_generator(chat_id: str, user_id: int, amount_inr: float, amount_usd: float) -> str:
    """Attempts to generate a link 3 times. If failed, refunds to wallet automatically."""
    for attempt in range(3):
        try:
            link = await bot.create_chat_invite_link(chat_id=chat_id, member_limit=1)
            return link.invite_link
        except Exception as e:
            logging.error(f"Invite generation failed (Attempt {attempt+1}): {e}")
            await asyncio.sleep(1.5) # Short delay before retry
    
    # If all 3 attempts fail, execute refund protocol
    async with AsyncSessionLocal() as session:
        user = await get_user(session, user_id)
        user.balance_inr += amount_inr
        user.balance_usd += amount_usd
        await session.commit()
        
    await bot.send_message(
        user_id, 
        f"⚠️ **Invite Link Error**\n\nYour payment was successful, but we couldn't generate your group invite link right now due to a network issue. \n\n✅ The amount of **₹{amount_inr:.2f}** has been safely credited to your wallet. You can use this balance to purchase the group directly from your wallet without paying again.",
        parse_mode="Markdown"
    )
    return None

# ==========================================
# 🤖 INTERACTIVE CAPTCHA & REFERRAL SYSTEM
# ==========================================
def generate_captcha_kb(correct_ans: int):
    # Generate 3 random wrong answers
    options = [correct_ans, correct_ans + random.randint(1,5), correct_ans - random.randint(1,5), correct_ans + random.randint(6,9)]
    options = list(set(options)) # ensure uniqueness
    while len(options) < 4:
        options.append(correct_ans + random.randint(10,20))
        options = list(set(options))
    
    random.shuffle(options)
    
    buttons = []
    for opt in options:
        # Check answer via callback data
        callback = "captcha_pass" if opt == correct_ans else "captcha_fail"
        buttons.append(InlineKeyboardButton(text=str(opt), callback_data=callback))
    
    # 2x2 grid
    return InlineKeyboardMarkup(inline_keyboard=[buttons[:2], buttons[2:]])

@dp.message(CommandStart(), StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext, command: Command):
    await state.clear()
    
    referrer_id = None
    if command.args and command.args.isdigit():
        referrer_id = int(command.args)
        if referrer_id == message.from_user.id:
            referrer_id = None # No self-referrals
            
    num1 = random.randint(5, 15)
    num2 = random.randint(5, 15)
    correct_ans = num1 + num2
    
    await state.update_data(
        captcha_ans=correct_ans, 
        captcha_time=time.time(), 
        attempts=0,
        temp_referrer=referrer_id
    )
    await state.set_state(PaymentState.captcha_verification)
    
    await message.answer(
        f"🤖 **Security Check Required**\n\nTo prevent abuse, please solve this math problem within 60 seconds:\n\n👉 **{num1} + {num2} = ?**", 
        reply_markup=generate_captcha_kb(correct_ans),
        parse_mode="Markdown"
    )

@dp.callback_query(StateFilter(PaymentState.captcha_verification), F.data.startswith("captcha_"))
async def process_captcha(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_passed = time.time() - data.get("captcha_time", 0)
    attempts = data.get("attempts", 0) + 1
    
    if time_passed > 60:
        await callback.message.edit_text("⏳ Time limit exceeded. Please type /start to generate a new CAPTCHA.")
        await state.clear()
        return

    if callback.data == "captcha_pass":
        # Verification Success! Register user & process referral
        referrer_id = data.get("temp_referrer")
        await state.clear()
        
        async with AsyncSessionLocal() as session:
            # Check if user already exists
            user_exists = await session.get(User, callback.from_user.id)
            user = await get_user(session, callback.from_user.id)
            user.is_active = True # Ensure active
            
            # Award Referral only if user is completely NEW
            if not user_exists and referrer_id:
                referrer = await get_user(session, referrer_id)
                # Max 100 limit
                if referrer.referrals_count < 100:
                    referrer.referrals_count += 1
                    referrer.balance_inr += 5.0
                    referrer.balance_usd += (5.0 / EXCHANGE_RATE)
                    referrer.referral_earnings += 5.0
                    user.referrer_id = referrer_id
                    
                    try:
                        await bot.send_message(referrer_id, f"🎉 **New Referral!**\nA user joined using your link. You earned **₹5.0**!")
                    except Exception:
                        pass
                        
            await session.commit()
            
        await callback.message.edit_text("✅ Verification Successful!")
        await callback.message.answer("Welcome to the Premium Store! 🛍️\nPlease select an option below:", reply_markup=main_menu_kb())
        
    else:
        # Failed attempt
        if attempts >= 3:
            BANNED_USERS.add(callback.from_user.id) # Shadowban temporary
            await callback.message.edit_text("❌ Too many failed attempts. You have been restricted for security reasons.")
            async with AsyncSessionLocal() as session:
                log = SecurityLog(user_id=callback.from_user.id, username=callback.from_user.username, reason="Failed CAPTCHA 3 times")
                session.add(log)
                await session.commit()
            await state.clear()
        else:
            await state.update_data(attempts=attempts)
            await callback.answer("❌ Incorrect answer. Try again.", show_alert=True)

# ==========================================
# 🛑 GLOBAL CANCEL & MENU HANDLERS
# ==========================================
MENU_COMMANDS = ["🛒 Buy Groups", "👤 Profile & Wallet", "📂 Demo Channels", "📜 Purchase History", "📢 Main Channel", "📞 Contact Admin", "🤝 Referral Program", "🔙 Back to Main Menu"]

@dp.message(F.text.in_(MENU_COMMANDS), StateFilter('*'))
async def handle_menu_buttons(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        user = await get_user(session, message.from_user.id)

    if message.text in ["🔙 Back to Main Menu"]:
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
        text = (f"👤 **Your Profile**\nID: `{user.id}`\n\n"
                f"💰 **Wallet Balance:**\n₹{user.balance_inr:.2f}  |  ${user.balance_usd:.2f}")
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Deposit Money", callback_data="deposit_money")]])
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    elif message.text == "📜 Purchase History":
        records = (await session.execute(select(PurchaseHistory).where(PurchaseHistory.user_id == message.from_user.id).order_by(PurchaseHistory.timestamp.desc()).limit(10))).scalars().all()
        if not records:
            return await message.answer("No purchase history found.")
        text = "📜 **Your Last Purchases:**\n\n"
        for r in records:
            sym = "₹" if r.currency == "INR" else "$"
            text += f"▪️ **{r.product_name}** - {sym}{r.price}\n   Method: {r.method} | Status: {r.status}\n   Date: {r.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
        await message.answer(text, parse_mode="Markdown")
    elif message.text == "🤝 Referral Program":
        bot_info = await bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        remaining = max(0, 100 - user.referrals_count)
        
        text = (
            f"🤝 **Referral Program**\n\n"
            f"Invite friends and earn **₹5.0** for every active user who joins and verifies via your link!\n\n"
            f"🔗 **Your Referral Link:**\n`{ref_link}`\n\n"
            f"📊 **Your Stats:**\n"
            f"• Total Referrals: {user.referrals_count}\n"
            f"• Total Earnings: ₹{user.referral_earnings:.2f}\n"
            f"• Remaining Limit: {remaining} users\n\n"
            f"_(Self-referrals or fake accounts will not be rewarded.)_"
        )
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
        result = await session.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()
        
    if not users:
        return await message.answer("No active users found in the database.")
        
    sent, failed, blocked, deleted = 0, 0, 0, 0
    await message.answer(f"Starting broadcast to {len(users)} users. This may take a while...")
    
    dead_users = []
    
    for user in users:
        try:
            await bot.copy_message(chat_id=user.id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            dead_users.append(user.id)
            if isinstance(e, TelegramForbiddenError):
                blocked += 1
            else:
                deleted += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
            
    if dead_users:
        async with AsyncSessionLocal() as session:
            await session.execute(update(User).where(User.id.in_(dead_users)).values(is_active=False))
            await session.commit()
            
    stats = (
        f"✅ **Broadcast Complete!**\n\n"
        f"👥 Total Users Attempted: {len(users)}\n"
        f"✅ Successful: {sent}\n"
        f"🧹 Cleaned Inactive/Blocked: {len(dead_users)}\n"
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

@dp.message(Command("stars"))
async def cmd_stars_dashboard(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    await message.answer(
        "⭐ **Telegram Stars Dashboard**\n\n"
        "Note: Real-time total balance is managed via BotFather.\n"
        "To view your exact earnings and withdraw, please visit:\n"
        "👉 https://fragment.com/my/bots\n\n"
        "Check your @BotFather balance for the most accurate stats.", 
        parse_mode="Markdown"
    )

@dp.message(Command("withdrawstars"))
async def cmd_withdraw_stars(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    await message.answer(
        "💸 **Withdrawal Instructions**\n\n"
        "Telegram does not allow bots to withdraw Stars directly via API.\n\n"
        "**To withdraw your Stars:**\n"
        "1. Open @BotFather on Telegram.\n"
        "2. Select your bot and go to 'Monetization' > 'Telegram Stars'.\n"
        "3. Alternatively, go to [Fragment.com](https://fragment.com/my/bots).\n"
        "4. Connect your wallet and convert your Stars to TON.\n\n"
        "This is the only official method to cash out your earnings.", 
        parse_mode="Markdown", disable_web_page_preview=True
    )

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
            
            invite_link = await safe_invite_generator(group['chat_id'], user.id, group['price'], group['usd_price'])
            if invite_link:
                await callback.message.answer(f"✅ **Purchase Successful using Wallet!**\n\n👉 Join here: {invite_link}", parse_mode="Markdown")
                await bot.send_message(config.OWNER_ID, f"🛍️ **Wallet Sale!** User `{user.id}` bought {group['name']}.")
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
            
            invite_link = await safe_invite_generator(group['chat_id'], user.id, group['price'], group['usd_price'])
            if invite_link:
                await bot.send_message(user_id, f"✅ **Payment verified successfully.**\nHere is your invite link:\n👉 {invite_link}", parse_mode="Markdown")
                
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
                
                invite_link = await safe_invite_generator(group['chat_id'], user.id, group['price'], group['usd_price'])
                if invite_link:
                    await message.answer(f"⭐️ **Stars Payment Successful!**\nJoin here:\n👉 {invite_link}", parse_mode="Markdown")

# ==========================================
# 🚀 INITIALIZATION
# ==========================================
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
