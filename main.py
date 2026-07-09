import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# ⚙️ GROUPS SETTINGS (Edit this from GitHub)
# ==========================================
# 'g1', 'g2' wagera short code hain.
# chat_id humesha -100 se shuru hoti hai. (Bot ko us group me Admin banana zaroori hai)
GROUPS = {
    "g1": {
        "name": "Stripchat", 
        "price": 199, 
        "chat_id": "-1004445000742", 
        "demo": "no demo ."
    },
    "g2": {
        "name": "teen Students ", 
        "price": 199, 
        "chat_id": "-1000987654321", 
        "demo": "🎬 Movies Demo\n4K Quality Movies directly in Telegram."
    }
}

# Payment Details
UPI_ID = "your_upi_id@ybl"
USDT_ADDRESS = "Txxxxxxxxxxxxxxxxxxxxxx"

# ==========================================
# 🗂 STATES FOR PAYMENT
# ==========================================
class PaymentState(StatesGroup):
    waiting_for_screenshot = State()
    selected_group_id = State()

# ==========================================
# ⌨️ BOTTOM KEYBOARDS (Reply Keyboards)
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
    kb = []
    for g_id, data in GROUPS.items():
        kb.append([KeyboardButton(text=f"📦 {data['name']} - ₹{data['price']}")])
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def demo_groups_kb():
    kb = []
    for g_id, data in GROUPS.items():
        kb.append([KeyboardButton(text=f"📁 {data['name']} Demo")])
    kb.append([KeyboardButton(text="🔙 Back to Main Menu")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Admin Approval Keyboard (Ye Inline hi rahega admin ki saholiyat ke liye)
def admin_approval_kb(user_id: int, group_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}_{group_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{user_id}_{group_id}")
        ]
    ])

# ==========================================
# 🤖 HANDLERS
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Welcome to the Premium Store! 🛍️\nPlease select an option below:", reply_markup=main_menu_kb())

@dp.message(F.text == "🔙 Back to Main Menu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Main Menu:", reply_markup=main_menu_kb())

# --- Links Handlers (Bottom Keyboard me URL direct nahi khulta, isliye reply me bhejna padta hai) ---
@dp.message(F.text == "👤 Contact Admin")
async def contact_admin(message: Message):
    await message.answer(f"Click here to message Admin:\n👉 https://t.me/{config.OWNER_USERNAME}")

@dp.message(F.text == "📢 Main Channel")
async def main_channel(message: Message):
    await message.answer(f"Join our Main Channel:\n👉 https://t.me/{config.MAIN_CHANNEL.replace('@', '')}")

# --- Demo Handlers ---
@dp.message(F.text == "📂 Demo Channels")
async def show_demo_menu(message: Message):
    await message.answer("Select a group to see its demo:", reply_markup=demo_groups_kb())

@dp.message(F.text.endswith("Demo"))
async def show_demo_content(message: Message):
    group_name = message.text.replace("📁 ", "").replace(" Demo", "")
    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            await message.answer(f"**{group_name} Demo:**\n{data['demo']}\n\nTo buy, go to 🛒 Buy Groups.", parse_mode="Markdown")
            return
    await message.answer("Demo not found.")

# --- Buy Handlers ---
@dp.message(F.text == "🛒 Buy Groups")
async def show_buy_menu(message: Message):
    await message.answer("Select a group to buy:", reply_markup=buy_groups_kb())

@dp.message(F.text.startswith("📦"))
async def process_buy_selection(message: Message, state: FSMContext):
    # Extract name from button text (e.g., "📦 VIP Trading - ₹499" -> "VIP Trading")
    text = message.text.replace("📦 ", "")
    group_name = text.split(" - ₹")[0]

    for g_id, data in GROUPS.items():
        if data["name"] == group_name:
            await state.update_data(selected_group_id=g_id)
            await state.set_state(PaymentState.waiting_for_screenshot)
            
            payment_text = (
                f"You selected: **{data['name']}**\n"
                f"Price: **₹{data['price']}**\n\n"
                f"💳 **Payment Methods:**\n"
                f"UPI ID: `{UPI_ID}`\n"
                f"USDT (TRC20): `{USDT_ADDRESS}`\n\n"
                f"👇 **Please pay the exact amount and send the PAYMENT SCREENSHOT here.**"
            )
            await message.answer(payment_text, parse_mode="Markdown")
            return

# --- Screenshot & Admin Forward Handler ---
@dp.message(StateFilter(PaymentState.waiting_for_screenshot), F.photo)
async def handle_screenshot(message: Message, state: FSMContext):
    state_data = await state.get_data()
    g_id = state_data.get("selected_group_id")
    group_data = GROUPS[g_id]
    
    # Send screenshot to Admin
    caption = (
        f"🚨 **New Payment Request**\n"
        f"User: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"User ID: `{message.from_user.id}`\n"
        f"Group: {group_data['name']}\n"
        f"Amount: ₹{group_data['price']}"
    )
    await bot.send_photo(
        chat_id=config.OWNER_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        reply_markup=admin_approval_kb(message.from_user.id, g_id),
        parse_mode="Markdown"
    )

    await message.answer("✅ Your payment screenshot has been sent to the admin. Please wait for approval.")
    await state.clear()

# --- Admin Approve / Reject Actions ---
@dp.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[1])
    g_id = parts[2]
    
    target_chat_id = GROUPS[g_id]['chat_id']
    group_name = GROUPS[g_id]['name']

    try:
        # Generate 1-Time Use Invite Link
        invite_link = await bot.create_chat_invite_link(
            chat_id=target_chat_id,
            member_limit=1,
            name=f"Buyer_{user_id}"
        )
        
        # Send Link to User
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ **Payment Approved!**\n\nHere is your unique, single-use invite link for **{group_name}**. It will expire after you join:\n\n👉 {invite_link.invite_link}",
            parse_mode="Markdown"
        )
        
        # Edit Admin's Message to show it's done
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **STATUS: APPROVED & LINK SENT**")
        await callback.answer("Approved successfully!")
    except Exception as e:
        await callback.answer(f"Error! Make sure the Bot is an Admin in the Private Channel.", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[1])
    
    await bot.send_message(
        chat_id=user_id,
        text="❌ **Payment Rejected!**\nYour screenshot could not be verified. Please contact the admin via the main menu.",
        parse_mode="Markdown"
    )
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **STATUS: REJECTED**")
    await callback.answer("Rejected.")

async def main():
    print("Bot is starting with Bottom Format...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
