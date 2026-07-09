import asyncio
import logging
import urllib.parse
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# ⚙️ GROUPS & PAYMENT SETTINGS
# ==========================================
# Stars (XTR) ki price integer me hoti hai (1 Star = ~₹1.5). 
# Aapne hisaab se "stars" ki value set kar lein.
GROUPS = {
    "g1": {
        "name": "Shat", 
        "price": 199, 
        "stars": 133, # ₹199 / 1.5 = ~133 Stars
        "chat_id": "-1004445000742", 
        "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADyh4AAmjCeUaIxOc4OANLJxYE"
    },
    "g2": {
        "name": "Ian Students", 
        "price": 199, 
        "stars": 133, 
        "chat_id": "-1004458938934", 
        "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADiR4AAmjCeUastMuPKJmT_hYE"
    },
    "g3": {
        "name": "Pure l", 
        "price": 199, 
        "stars": 133, # ₹199 / 1.5 = ~133 Stars
        "chat_id": "-1003893753935", 
        "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADix4AAmjCeUaiYnw8VfpWHxYE"
    },
    "g4": {
        "name": "Frced", 
        "price": 199, 
        "stars": 133, # ₹199 / 1.5 = ~133 Stars
        "chat_id": "-1003978784189", 
        "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjB4AAmjCeUZFY7dmTyGcVBYE"
    },
    "g5": {
        "name": "self made ", 
        "price": 199, 
        "stars": 133, # ₹199 / 1.5 = ~133 Stars
        "chat_id": "-1003589926855", 
        "demo": "https://t.me/DemoNovazenithXbot?start=BQADAQADjh4AAmjCeUY17uH7NGywPhYE"
    },
    
}

UPI_ID = "Hardiksharma8935@fam"
USDT_ADDRESS = "0xba924a45fe0d1a4172d3230c767c7096d9854f97" # Apna BEP20 address daalein

# ==========================================
# 🗂 STATES
# ==========================================
class PaymentState(StatesGroup):
    waiting_for_screenshot = State()
    waiting_for_amazon_card = State()
    waiting_for_amazon_confirm = State()
    broadcast_msg = State()

# ==========================================
# ⌨️ KEYBOARDS
# ==========================================
def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Demo Channels"), KeyboardButton(text="🛒 Buy Groups")],
            [KeyboardButton(text="👤 Contact Admin"), KeyboardButton(text="📢 Main Channel")]
        ],
        resize_keyboard=True
    )

def buy_groups_kb():
    kb = [[KeyboardButton(text=f"📦 {data['name']} - ₹{data['price']}")] for g_id, data in GROUPS.items()]
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def demo_groups_kb():
    kb = [[KeyboardButton(text=f"📁 {data['name']} Demo")] for g_id, data in GROUPS.items()]
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# 4 Payment Methods Keyboard
def payment_methods_kb(g_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 UPI", callback_data=f"method_upi_{g_id}"),
         InlineKeyboardButton(text="₮ USDT (BEP20)", callback_data=f"method_usdt_{g_id}")],
        [InlineKeyboardButton(text="🎁 Amazon Gift Card", callback_data=f"method_amazon_{g_id}"),
         InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data=f"method_stars_{g_id}")]
    ])

# I Paid Keyboard
def i_paid_kb(g_id: str, method: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I paid", callback_data=f"ipaid_{method}_{g_id}")]
    ])

def admin_approval_kb(user_id: int, g_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}_{g_id}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}_{g_id}")]
    ])

# ==========================================
# 🛠 UTILITIES (Save Users for Broadcast)
# ==========================================
def save_user(user_id):
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

# ==========================================
# 🤖 HANDLERS
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user.id)
    await message.answer("Welcome to the Premium Store! 🛍️\nPlease select an option below:", reply_markup=main_menu_kb())

@dp.message(F.text == "🔙 Back to Main Menu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Main Menu:", reply_markup=main_menu_kb())

@dp.message(F.text == "👤 Contact Admin")
async def contact_admin(message: Message):
    await message.answer(f"👉 https://t.me/{config.OWNER_USERNAME}")

@dp.message(F.text == "📢 Main Channel")
async def main_channel(message: Message):
    await message.answer(f"👉 https://t.me/{config.MAIN_CHANNEL.replace('@', '')}")

# --- DEMO ---
@dp.message(F.text == "📂 Demo Channels")
async def show_demo_menu(message: Message):
    await message.answer("Select a group to see its demo:", reply_markup=demo_groups_kb())

@dp.message(F.text.endswith("Demo"))
async def show_demo_content(message: Message):
    group_name = message.text.replace("📁 ", "").replace(" Demo", "")
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            await message.answer(f"**{group_name} Demo:**\n{data['demo']}", parse_mode="Markdown")
            return

# --- BUY MENU ---
@dp.message(F.text == "🛒 Buy Groups")
async def show_buy_menu(message: Message):
    await message.answer("Select a group to buy:", reply_markup=buy_groups_kb())

@dp.message(F.text.startswith("📦"))
async def show_payment_methods(message: Message):
    group_name = message.text.replace("📦 ", "").split(" - ₹")[0]
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            text = f"You selected: **{data['name']}**\nPrice: **₹{data['price']}**\n\n👇 Select your payment method:"
            await message.answer(text, reply_markup=payment_methods_kb(g_id), parse_mode="Markdown")
            return

# --- 1. UPI METHOD ---
@dp.callback_query(F.data.startswith("method_upi_"))
async def process_upi(callback: CallbackQuery):
    g_id = callback.data.split("_")[2]
    price = GROUPS[g_id]['price']
    
    # Auto Generate exact amount QR Code
    upi_url = f"upi://pay?pa={UPI_ID}&pn=PremiumStore&am={price}&cu=INR"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={urllib.parse.quote(upi_url)}"
    
    caption = f"💳 **UPI Payment**\n\nAmount: **₹{price}**\nUPI ID: `{UPI_ID}`\n\nScan the QR code above or copy the UPI ID to pay. After payment, click **✅ I paid**."
    await callback.message.answer_photo(photo=qr_url, caption=caption, reply_markup=i_paid_kb(g_id, "upi"), parse_mode="Markdown")
    await callback.answer()

# --- 2. USDT METHOD ---
@dp.callback_query(F.data.startswith("method_usdt_"))
async def process_usdt(callback: CallbackQuery):
    g_id = callback.data.split("_")[2]
    
    # Auto Generate USDT Address QR Code
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={USDT_ADDRESS}"
    
    caption = f"₮ **USDT (BEP20) Payment**\n\nAddress:\n`{USDT_ADDRESS}`\n\nCopy the exact address (Tap to copy) and send the funds. After payment, click **✅ I paid**."
    await callback.message.answer_photo(photo=qr_url, caption=caption, reply_markup=i_paid_kb(g_id, "usdt"), parse_mode="Markdown")
    await callback.answer()

# --- 3. AMAZON GIFT CARD METHOD ---
@dp.callback_query(F.data.startswith("method_amazon_"))
async def process_amazon(callback: CallbackQuery, state: FSMContext):
    g_id = callback.data.split("_")[2]
    await state.update_data(g_id=g_id)
    await state.set_state(PaymentState.waiting_for_amazon_card)
    await callback.message.answer("🎁 **Amazon Gift Card**\n\nPlease send your Amazon Gift Card Code or a Photo of the card in this chat now.", parse_mode="Markdown")
    await callback.answer()

@dp.message(StateFilter(PaymentState.waiting_for_amazon_card))
async def receive_amazon_card(message: Message, state: FSMContext):
    data = await state.get_data()
    g_id = data['g_id']
    # Save the user's message ID to forward it to admin later
    await state.update_data(amazon_msg_id=message.message_id)
    await state.set_state(PaymentState.waiting_for_amazon_confirm)
    
    await message.answer("✅ Gift card received. Click **✅ I paid** to submit it for Admin approval.", reply_markup=i_paid_kb(g_id, "amazon"), parse_mode="Markdown")

# --- 4. TELEGRAM STARS METHOD (Auto Approve) ---
@dp.callback_query(F.data.startswith("method_stars_"))
async def process_stars(callback: CallbackQuery):
    g_id = callback.data.split("_")[2]
    group = GROUPS[g_id]
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=group['name'],
        description=f"Automated access to {group['name']}",
        payload=f"stars_{g_id}_{callback.from_user.id}",
        provider_token="", # Must be empty for Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label=group['name'], amount=group['stars'])]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    # Stars payment successful! Auto-approve.
    payload = message.successful_payment.invoice_payload
    _, g_id, user_id = payload.split("_")
    
    target_chat_id = GROUPS[g_id]['chat_id']
    try:
        invite_link = await bot.create_chat_invite_link(chat_id=target_chat_id, member_limit=1)
        await message.answer(f"⭐️ **Stars Payment Successful!**\n\nHere is your unique invite link:\n👉 {invite_link.invite_link}", parse_mode="Markdown")
        
        # Notify Admin
        await bot.send_message(config.OWNER_ID, f"⭐️ **Auto-Sale!**\nUser {message.from_user.full_name} bought {GROUPS[g_id]['name']} using Telegram Stars.")
    except Exception as e:
        await message.answer("Payment successful, but error generating link. Admin has been notified.")
        await bot.send_message(config.OWNER_ID, f"Error generating link for User {user_id} after Stars payment.")

# --- I PAID BUTTON HANDLER (For UPI, USDT, Amazon) ---
@dp.callback_query(F.data.startswith("ipaid_"))
async def handle_i_paid(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    method = parts[1]
    g_id = parts[2]

    if method in ["upi", "usdt"]:
        await state.update_data(g_id=g_id, method=method)
        await state.set_state(PaymentState.waiting_for_screenshot)
        await callback.message.answer(f"📸 Please send your **{method.upper()}** payment screenshot here now.", parse_mode="Markdown")
        await callback.answer()
        
    elif method == "amazon":
        data = await state.get_data()
        msg_id = data.get("amazon_msg_id")
        
        caption = f"🚨 **Amazon Card Request**\nUser: {callback.from_user.full_name} (`{callback.from_user.id}`)\nGroup: {GROUPS[g_id]['name']}"
        await bot.send_message(chat_id=config.OWNER_ID, text=caption, parse_mode="Markdown")
        
        # Forward the exact message/photo the user sent
        await bot.forward_message(chat_id=config.OWNER_ID, from_chat_id=callback.message.chat.id, message_id=msg_id)
        await bot.send_message(chat_id=config.OWNER_ID, text="Approve or Reject?", reply_markup=admin_approval_kb(callback.from_user.id, g_id))
        
        await callback.message.answer("✅ Your Amazon Gift Card has been sent to the admin. Please wait for approval.")
        await state.clear()
        await callback.answer()

# --- SCREENSHOT HANDLER (UPI & USDT) ---
@dp.message(StateFilter(PaymentState.waiting_for_screenshot), F.photo)
async def handle_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    g_id = data['g_id']
    method = data['method']
    group = GROUPS[g_id]
    
    caption = (
        f"🚨 **New {method.upper()} Payment**\n"
        f"User: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"ID: `{message.from_user.id}`\n"
        f"Group: {group['name']}"
    )
    await bot.send_photo(
        chat_id=config.OWNER_ID, photo=message.photo[-1].file_id, 
        caption=caption, reply_markup=admin_approval_kb(message.from_user.id, g_id), parse_mode="Markdown"
    )
    await message.answer("✅ Screenshot submitted. Wait for admin approval.")
    await state.clear()

# --- ADMIN APPROVE/REJECT ---
@dp.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: CallbackQuery):
    _, user_id, g_id = callback.data.split("_")
    target_chat_id = GROUPS[g_id]['chat_id']
    try:
        link = await bot.create_chat_invite_link(chat_id=target_chat_id, member_limit=1)
        await bot.send_message(chat_id=int(user_id), text=f"✅ **Payment Approved!**\nJoin here: {link.invite_link}", parse_mode="Markdown")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("✅ Approved.")
    except:
        await callback.answer("Error! Ensure bot is Admin in group.", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: CallbackQuery):
    _, user_id, g_id = callback.data.split("_")
    await bot.send_message(chat_id=int(user_id), text="❌ **Payment Rejected!** Contact admin.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.reply("❌ Rejected.")

# --- BROADCAST SYSTEM (Owner Only) ---
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if message.from_user.id == config.OWNER_ID:
        await message.answer("Send the message (Text or Photo) you want to broadcast:")
        await state.set_state(PaymentState.broadcast_msg)

@dp.message(StateFilter(PaymentState.broadcast_msg))
async def process_broadcast(message: Message, state: FSMContext):
    await state.clear()
    if not os.path.exists("users.txt"):
        return await message.answer("No users found.")
        
    with open("users.txt", "r") as f:
        users = f.read().splitlines()
        
    sent, failed = 0, 0
    await message.answer(f"Starting broadcast to {len(users)} users...")
    
    for uid in users:
        try:
            await bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
            await asyncio.sleep(0.05) # Prevent flood wait
        except:
            failed += 1
            
    await message.answer(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
