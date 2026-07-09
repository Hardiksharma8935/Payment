import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config

# Logging setup
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📂 Demo Channels", callback_data="demo")
    builder.button(text="🛒 Buy Groups", callback_data="buy")
    builder.button(text="👤 Contact Admin", url=f"https://t.me/{config.OWNER_USERNAME}")
    builder.button(text="📢 Main Channel", url=f"https://t.me/{config.MAIN_CHANNEL.replace('@', '')}")
    builder.adjust(2) # 2-column layout
    return builder.as_markup()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Welcome to the Premium Store! 🛍️\nPlease select an option below:",
        reply_markup=main_menu_kb()
    )

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
