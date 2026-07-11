import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import config
from database import init_db, AsyncSessionLocal, User, get_user
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# ⚙️ GROUPS SETTINGS
# ==========================================
GROUPS = {
    "g1": {"name": "Stripchat", "price": 99, "usd_price": 3, "chat_id": "-1004445000742", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADyh4AAmjCeUaIxOc4OANLJxYE"},
    "g2": {"name": "Indian Students", "price": 99, "usd_price": 3, "chat_id": "-1004458938934", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADiR4AAmjCeUastMuPKJmT_hYE"},
    "g3": {"name": "Pure tamil", "price": 99, "usd_price": 3, "chat_id": "-1003893753935", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADix4AAmjCeUaiYnw8VfpWHxYE"},
    "g4": {"name": "Forced", "price": 199, "usd_price": 3, "chat_id": "-1003978784189", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjB4AAmjCeUZFY7dmTyGcVBYE"},
    "g5": {"name": "self made", "price": 99, "usd_price": 3, "chat_id": "-1003589926855", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjh4AAmjCeUY17uH7NGywPhYE"},
    "g6": {"name": "hidden secret", "price": 99, "usd_price": 3, "chat_id": "-1004407356883", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlB4AAmjCeUYrdi34PirAWhYE"},
    "g7": {"name": "bad parents", "price": 149, "usd_price": 3, "chat_id": "-1003969174282", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADlR4AAmjCeUZGaDMBp5MGoBYE"},
    "g8": {"name": "fingerings", "price": 99, "usd_price": 3, "chat_id": "-1004435164752", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmh4AAmjCeUb7rxcaimfZWxYE"},
    "g9": {"name": "dickflash", "price": 99, "usd_price": 3, "chat_id": "-1003870700155", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADoB4AAmjCeUZIwdgTLPeNlxYE"},
    "g10": {"name": "car videos", "price": 49, "usd_price": 3, "chat_id": "-1004351633034", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADox4AAmjCeUbkZylaMcGdpBYE"},
    "g11": {"name": "ip cam cctv", "price": 99, "usd_price": 3, "chat_id": "-1003739836678", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADpR4AAmjCeUbG-D-ej2NRmRYE"},
    "g12": {"name": "only fans", "price": 99, "usd_price": 3, "chat_id": "-1003960924467", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADqR4AAmjCeUYp7NSXggaRfBYE"},
    "g13": {"name": "Indian Teen", "price": 199, "usd_price": 5, "chat_id": "-1003985171544", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADqh4AAmjCeUaem-bfAQORlhYE"},
    "g14": {"name": "Arbic Stuffs", "price": 99, "usd_price": 3, "chat_id": "-1004409206399", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADrR4AAmjCeUZrD1n7ZSUqFxYE"},
    "g15": {"name": "mallu", "price": 99, "usd_price": 3, "chat_id": "-1004320995574", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADUAwAAmjCgUbyd4xysXvrtxYE"},
    "g16": {"name": "Quality Link Group", "price": 499, "usd_price": 5, "chat_id": "-1003599861740", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADmA0AAmjCgUYg1UY_ofR7vxYE"},
    "g17": {"name": "mom son", "price": 199, "usd_price": 3, "chat_id": "-1004336932131", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADfRQAAghnMUYQOCV4bNnbxBYE"},
    "g18": {"name": "pakistani Cxp", "price": 199, "usd_price": 3, "chat_id": "-1003928326633", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD8QkAAp4PiEZ7T8vtPnvP7BYE"},
    "g19": {"name": "tamil cxp", "price": 199, "usd_price": 3, "chat_id": "-1004292111897", "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQAD_wkAAp4PiEaDKqDxyG7DNxYE"}
}

# Pricing standards
EXCHANGE_RATE = 85.0 # 1 USD = ~85 INR
STARS_PER_USD = 50 

# ==========================================
# 🗂 STATES
# ==========================================
class BotState(StatesGroup):
    waiting_for_captcha = State()
    waiting_for_deposit_amount = State()
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
            [KeyboardButton(text="📂 Demo Channels"), KeyboardButton(text="👥 Refer & Earn")],
            [KeyboardButton(text="📢 Main Channel"), KeyboardButton(text="📞 Contact Admin")]
        ],
        resize_keyboard=True
    )

def buy_groups_kb():
    kb = [[KeyboardButton(text=f"📦 {data['name']} - ₹{data['price']} / ${data['usd_price']}")] for g_id, data in GROUPS.items()]
    kb.append([KeyboardButton(text="🔙 Back")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def deposit_methods_kb(amount_usd: float):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Amazon Gift Card", callback_data=f"dep_amazon_{amount_usd}")],
        [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data=f"dep_stars_{amount_usd}")],
        [InlineKeyboardButton(text="🪙 USDT (TRC20)", callback_data=f"dep_crypto_USDT_{amount_usd}"),
         InlineKeyboardButton(text="₿ BTC", callback_data=f"dep_crypto_BTC_{amount_usd}")],
        [InlineKeyboardButton(text="🔷 ETH", callback_data=f"dep_crypto_ETH_{amount_usd}"),
         InlineKeyboardButton(text="🟣 SOL", callback_data=f"dep_crypto_SOL_{amount_usd}")]
    ])

def i_paid_kb(method: str, amount_usd: float):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I Paid", callback_data=f"ipaid_{method}_{amount_usd}")]
    ])

def admin_approve_deposit_kb(user_id: int, amount_inr: float, amount_usd: float):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"apprdep_{user_id}_{amount_inr}_{amount_usd}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"rejdep_{user_id}")]
    ])

def group_purchase_kb(g_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pay with Wallet Balance", callback_data=f"buywallet_{g_id}")]
    ])

# ==========================================
# 🛡️ CAPTCHA & VERIFICATION MIDDLEWARE
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: Command):
    async with AsyncSessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        
        # Handle referral argument
        if command.args and command.args.isdigit() and not user.is_verified:
            ref_id = int(command.args)
            if ref_id != message.from_user.id:
                user.referrer_id = ref_id
                await session.commit()

        if user.is_verified:
            await message.answer("Welcome back to the Premium Store! 🛍️", reply_markup=main_menu_kb())
            return
            
        # Generate Captcha
        num1, num2 = random.randint(1, 10), random.randint(1, 10)
        await state.update_data(captcha_answer=num1 + num2)
        await state.set_state(BotState.waiting_for_captcha)
        await message.answer(f"🛡️ **Security Check**\nTo use this bot, please solve this math problem:\n\n**What is {num1} + {num2}?**", parse_mode="Markdown")

@dp.message(StateFilter(BotState.waiting_for_captcha))
async def process_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answer = data.get("captcha_answer")
    
    if message.text.strip().isdigit() and int(message.text.strip()) == correct_answer:
        async with AsyncSessionLocal() as session:
            user = await get_user(session, message.from_user.id)
            user.is_verified = True
            
            # Process Referral Reward
            if user.referrer_id:
                referrer = await get_user(session, user.referrer_id)
                if referrer.total_referrals < 100:
                    referrer.total_referrals += 1
                    referrer.balance_inr += 5.0
                    referrer.balance_usd += 0.05
                    referrer.referral_earnings_inr += 5.0
                    try:
                        await bot.send_message(referrer.id, "🎉 **Referral Success!**\nSomeone joined using your link. You earned ₹5 ($0.05)!")
                    except:
                        pass
            await session.commit()
            
        await state.clear()
        await message.answer("✅ Verification successful! Welcome to the store.", reply_markup=main_menu_kb())
    else:
        num1, num2 = random.randint(1, 10), random.randint(1, 10)
        await state.update_data(captcha_answer=num1 + num2)
        await message.answer(f"❌ Incorrect. Please try again:\n**What is {num1} + {num2}?**", parse_mode="Markdown")

# ==========================================
# 👤 WALLET & PROFILE
# ==========================================
@dp.message(F.text == "👤 Profile & Wallet")
async def show_profile(message: Message):
    async with AsyncSessionLocal() as session:
        user = await get_user(session, message.from_user.id)
        text = (
            f"👤 **Your Profile**\n"
            f"ID: `{user.id}`\n\n"
            f"💰 **Wallet Balance:**\n"
            f"₹{user.balance_inr:.2f}  |  ${user.balance_usd:.2f}\n\n"
            f"To buy groups, please deposit balance first."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Deposit Money", callback_data="deposit_money")]])
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "deposit_money")
async def request_deposit_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotState.waiting_for_deposit_amount)
    await callback.message.answer("💵 Enter the amount in **USD** you want to deposit (e.g., 5 or 10):", parse_mode="Markdown")
    await callback.answer()

@dp.message(StateFilter(BotState.waiting_for_deposit_amount))
async def process_deposit_amount(message: Message, state: FSMContext):
    try:
        amount_usd = float(message.text.strip())
        if amount_usd <= 0:
            raise ValueError
        await state.clear()
        await message.answer(
            f"💵 Deposit Amount: **${amount_usd}** (approx ₹{amount_usd * EXCHANGE_RATE:.2f})\n\nSelect a payment method:",
            reply_markup=deposit_methods_kb(amount_usd), parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("❌ Invalid amount. Please enter a valid number (e.g., 5).")

# ==========================================
# 💰 DEPOSIT METHODS
# ==========================================
@dp.callback_query(F.data.startswith("dep_crypto_"))
async def process_crypto_deposit(callback: CallbackQuery):
    _, _, crypto, amount_usd = callback.data.split("_")
    
    addresses = {
        "USDT": config.USDT_ADDRESS, "BTC": config.BTC_ADDRESS,
        "ETH": config.ETH_ADDRESS, "SOL": config.SOL_ADDRESS
    }
    address = addresses.get(crypto, "Not Configured")
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={address}"
    caption = (
        f"🪙 **{crypto} Payment**\n\n"
        f"Amount to Send: **${amount_usd}**\n\n"
        f"Network Address:\n`{address}`\n\n"
        f"Tap the address to copy. Send exact amount and click **✅ I Paid**."
    )
    await callback.message.answer_photo(photo=qr_url, caption=caption, reply_markup=i_paid_kb(f"crypto_{crypto}", amount_usd), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("dep_amazon_"))
async def process_amazon_deposit(callback: CallbackQuery, state: FSMContext):
    amount_usd = callback.data.split("_")[2]
    await state.update_data(deposit_usd=amount_usd)
    await state.set_state(BotState.waiting_for_amazon_card)
    await callback.message.answer(f"🎁 **Amazon Gift Card**\n\nPlease send your **${amount_usd}** Amazon Gift Card Code or Photo now.", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("dep_stars_"))
async def process_stars_deposit(callback: CallbackQuery):
    amount_usd = float(callback.data.split("_")[2])
    stars_cost = int(amount_usd * STARS_PER_USD)
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Wallet Deposit",
        description=f"Deposit ${amount_usd} into your bot wallet.",
        payload=f"starsdep_{callback.from_user.id}_{amount_usd}",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="Wallet Funds", amount=stars_cost)]
    )
    await callback.answer()

# --- Stars Checkout Logic ---
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("starsdep_"):
        _, user_id, amount_usd = payload.split("_")
        amount_usd = float(amount_usd)
        amount_inr = amount_usd * EXCHANGE_RATE
        
        async with AsyncSessionLocal() as session:
            user = await get_user(session, int(user_id))
            user.balance_usd += amount_usd
            user.balance_inr += amount_inr
            await session.commit()
            
        await message.answer(f"⭐️ **Stars Deposit Successful!**\nYour wallet has been credited with **${amount_usd}** (₹{amount_inr:.2f}).", parse_mode="Markdown")
        await bot.send_message(config.OWNER_ID, f"⭐️ **Auto-Deposit!** User `{user_id}` deposited ${amount_usd} via Stars.")

# --- I Paid & Screenshots ---
@dp.callback_query(F.data.startswith("ipaid_"))
async def handle_i_paid(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    method = f"{parts[1]}_{parts[2]}" if parts[1] == "crypto" else parts[1]
    amount_usd = parts[-1]
    
    await state.update_data(method=method, amount_usd=amount_usd)
    await state.set_state(BotState.waiting_for_screenshot)
    await callback.message.answer(f"📸 Please send your **Payment Screenshot** here now.", parse_mode="Markdown")
    await callback.answer()

@dp.message(StateFilter(BotState.waiting_for_amazon_card))
async def receive_amazon_card(message: Message, state: FSMContext):
    data = await state.get_data()
    amount_usd = data.get('deposit_usd')
    amount_inr = float(amount_usd) * EXCHANGE_RATE
    
    msg_id = message.message_id
    caption = f"🚨 **Amazon Card Request**\nUser: {message.from_user.full_name} (`{message.from_user.id}`)\nAmount: **${amount_usd}**"
    await bot.send_message(chat_id=config.OWNER_ID, text=caption, parse_mode="Markdown")
    await bot.forward_message(chat_id=config.OWNER_ID, from_chat_id=message.chat.id, message_id=msg_id)
    await bot.send_message(chat_id=config.OWNER_ID, text="Approve or Reject?", reply_markup=admin_approve_deposit_kb(message.from_user.id, amount_inr, float(amount_usd)))
    
    await message.answer("✅ Gift Card sent to admin. Wait for balance approval.")
    await state.clear()

@dp.message(StateFilter(BotState.waiting_for_screenshot), F.photo)
async def handle_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    method = data['method']
    amount_usd = float(data['amount_usd'])
    amount_inr = amount_usd * EXCHANGE_RATE
    
    caption = (
        f"🚨 **New {method.upper()} Deposit**\n"
        f"User: `{message.from_user.id}`\n"
        f"Requested Amount: **${amount_usd}**"
    )
    await bot.send_photo(
        chat_id=config.OWNER_ID, photo=message.photo[-1].file_id, 
        caption=caption, reply_markup=admin_approve_deposit_kb(message.from_user.id, amount_inr, amount_usd), parse_mode="Markdown"
    )
    await message.answer("✅ Screenshot submitted. Balance will be updated upon admin approval.")
    await state.clear()

# ==========================================
# 🔧 ADMIN ACTIONS
# ==========================================
@dp.callback_query(F.data.startswith("apprdep_"))
async def approve_deposit(callback: CallbackQuery):
    _, user_id, amount_inr, amount_usd = callback.data.split("_")
    user_id = int(user_id)
    amount_inr, amount_usd = float(amount_inr), float(amount_usd)
    
    async with AsyncSessionLocal() as session:
        user = await get_user(session, user_id)
        user.balance_inr += amount_inr
        user.balance_usd += amount_usd
        await session.commit()
        
    await bot.send_message(chat_id=user_id, text=f"✅ **Deposit Approved!**\nYour wallet has been credited with **${amount_usd}** (₹{amount_inr:.2f}).", parse_mode="Markdown")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply("✅ Approved.")

@dp.callback_query(F.data.startswith("rejdep_"))
async def reject_deposit(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    await bot.send_message(chat_id=int(user_id), text="❌ **Deposit Rejected!** Contact admin if you think this is a mistake.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply("❌ Rejected.")

@dp.message(Command("addbalance", "removebalance"))
async def manual_balance_update(message: Message, command: Command):
    if message.from_user.id != config.OWNER_ID:
        return
    try:
        args = command.args.split()
        target_id, amount_usd = int(args[0]), float(args[1])
        amount_inr = amount_usd * EXCHANGE_RATE
        
        async with AsyncSessionLocal() as session:
            user = await get_user(session, target_id)
            if command.command == "addbalance":
                user.balance_usd += amount_usd
                user.balance_inr += amount_inr
                msg = f"✅ Added ${amount_usd} to {target_id}"
            else:
                user.balance_usd = max(0, user.balance_usd - amount_usd)
                user.balance_inr = max(0, user.balance_inr - amount_inr)
                msg = f"✅ Removed ${amount_usd} from {target_id}"
            await session.commit()
        await message.answer(msg)
    except:
        await message.answer("Usage: /addbalance <user_id> <amount_usd>")

# ==========================================
# 🛒 BUY GROUPS (Via Wallet)
# ==========================================
@dp.message(F.text == "🛒 Buy Groups")
async def show_buy_menu(message: Message):
    await message.answer("Select a group to buy:", reply_markup=buy_groups_kb())

@dp.message(F.text.startswith("📦"))
async def show_group_details(message: Message):
    group_name = message.text.replace("📦 ", "").split(" - ₹")[0]
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            text = (
                f"You selected: **{data['name']}**\n"
                f"Price: **₹{data['price']} / ${data['usd_price']}**\n\n"
                f"Click below to purchase using your Wallet Balance."
            )
            await message.answer(text, reply_markup=group_purchase_kb(g_id), parse_mode="Markdown")
            return

@dp.callback_query(F.data.startswith("buywallet_"))
async def process_wallet_purchase(callback: CallbackQuery):
    g_id = callback.data.split("_")[1]
    group = GROUPS[g_id]
    
    async with AsyncSessionLocal() as session:
        user = awai
