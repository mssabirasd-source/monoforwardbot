import asyncio
import logging
import random
import string
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8916721054:AAFSTYY9zpAe2xm1MNdqJjLW6UNC6-mQmTQ"
ADMIN_ID = 7211171229

# In-memory database for keys and configuration
GENERATED_KEYS = set()
USED_KEYS = set()
PREMIUM_USERS = set()

bot_config = {
    "source": None,  # e.g., @source_channel or -100xxxxxxxxxx
    "target": None,  # e.g., @target_channel or -100xxxxxxxxxx
    "active": False
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class BotStates(StatesGroup):
    waiting_source = State()
    waiting_target = State()
    waiting_key = State()

def main_menu_kb(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="⚙️ Forwarding Panel", callback_data="fw_panel")],
        [InlineKeyboardButton(text="🔑 Redeem Key", callback_data="redeem_key"),
         InlineKeyboardButton(text="👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton(text="📞 Support", callback_data="support")]
    ]
    if is_admin:
        buttons.insert(0, [InlineKeyboardButton(text="🔑 Admin Key Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    is_admin = (message.from_user.id == ADMIN_ID)
    text = (
        "🤖 **MONO FORWARD BOT**\n\n"
        "Welcome! Yeh bot aapke channels ke beech posts ko instant forward karta hai.\n"
        "Neeche diye gaye buttons se management karein:"
    )
    await message.answer(text, reply_markup=main_menu_kb(is_admin), parse_mode="Markdown")

@dp.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = (callback.from_user.id == ADMIN_ID)
    await callback.message.edit_text("🤖 **Main Menu:**", reply_markup=main_menu_kb(is_admin), parse_mode="Markdown")

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⚠️ Yeh sirf admin ke liye hai!", show_alert=True)
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Generate New Key", callback_data="gen_key")],
        [InlineKeyboardButton(text="📋 View All Keys", callback_data="view_keys")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text("🔑 **Admin Key Generator Panel**", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "gen_key")
async def generate_key(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    chars = string.ascii_uppercase + string.digits
    new_key = "MF-" + "".join(random.choices(chars, k=12))
    while new_key in GENERATED_KEYS:
        new_key = "MF-" + "".join(random.choices(chars, k=12))
    
    GENERATED_KEYS.add(new_key)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Generate Another", callback_data="gen_key")],
        [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(f"✅ **New Key Generated:**\n\n`{new_key}`", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "view_keys")
async def view_keys(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    keys_text = "\n".join(f"• `{k}` {'(Used)' if k in USED_KEYS else '(Active)'}" for k in GENERATED_KEYS) if GENERATED_KEYS else "Koi key nahi bani hai."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")]
    ])
    await callback.message.edit_text(f"📋 **All Keys:**\n\n{keys_text}", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "fw_panel")
async def forwarding_panel(callback: types.CallbackQuery):
    status = "🟢 Active" if bot_config["active"] else "🔴 Stopped"
    src = bot_config["source"] or "Not Set"
    tgt = bot_config["target"] or "Not Set"
    
    text = (
        f"⚙️ **FORWARDING CONFIGURATION**\n\n"
        f"• Status: {status}\n"
        f"• Source: `{src}`\n"
        f"• Target: `{tgt}`"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Set Source Channel", callback_data="set_src"),
         InlineKeyboardButton(text="📤 Set Target Channel", callback_data="set_tgt")],
        [InlineKeyboardButton(text="🚀 Start Forwarding", callback_data="start_fw"),
         InlineKeyboardButton(text="🛑 Stop Forwarding", callback_data="stop_fw")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "set_src")
async def set_source_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📥 Apne Source Channel ka username (jaise `@source_channel`) ya ID bhejein:")
    await state.set_state(BotStates.waiting_source)

@dp.message(BotStates.waiting_source)
async def save_source(message: types.Message, state: FSMContext):
    bot_config["source"] = message.text.strip()
    await message.answer(f"✅ Source Channel successfully set to: `{bot_config['source']}`", parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data == "set_tgt")
async def set_target_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📤 Apne Target Channel ka username (jaise `@target_channel`) ya ID bhejein:")
    await state.set_state(BotStates.waiting_target)

@dp.message(BotStates.waiting_target)
async def save_target(message: types.Message, state: FSMContext):
    bot_config["target"] = message.text.strip()
    await message.answer(f"✅ Target Channel successfully set to: `{bot_config['target']}`", parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data == "start_fw")
async def start_forwarding(callback: types.CallbackQuery):
    if not bot_config["source"] or not bot_config["target"]:
        await callback.answer("⚠️ Pehle Source aur Target channel set karein!", show_alert=True)
        return
    bot_config["active"] = True
    await callback.answer("🚀 Auto-Forwarding shuru ho gayi hai!", show_alert=True)
    await forwarding_panel(callback)

@dp.callback_query(F.data == "stop_fw")
async def stop_forwarding(callback: types.CallbackQuery):
    bot_config["active"] = False
    await callback.answer("🛑 Auto-Forwarding rok di gayi hai!", show_alert=True)
    await forwarding_panel(callback)

@dp.callback_query(F.data == "redeem_key")
async def redeem_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔑 Apni subscription key yahan type karke bhejein:")
    await state.set_state(BotStates.waiting_key)

@dp.message(BotStates.waiting_key)
async def process_redeem(message: types.Message, state: FSMContext):
    key = message.text.strip()
    if key in GENERATED_KEYS and key not in USED_KEYS:
        USED_KEYS.add(key)
        PREMIUM_USERS.add(message.from_user.id)
        await message.answer("🎉 **Congratulation!** Aapki key successfully redeem ho gayi hai aur aapka premium access activate ho gaya hai.")
    elif key in USED_KEYS:
        await message.answer("❌ Yeh key pehle hi use ki ja chuki hai!")
    else:
        await message.answer("❌ Invalid key! Kripya sahi key enter karein.")
    await state.clear()

@dp.callback_query(F.data == "profile")
async def profile_page(callback: types.CallbackQuery):
    status = "👑 Premium Member" if callback.from_user.id in PREMIUM_USERS or callback.from_user.id == ADMIN_ID else "🆓 Free User"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]])
    await callback.message.edit_text(f"👤 **Your Profile**\n\nStatus: {status}", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "support")
async def support_page(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]])
    await callback.message.edit_text("📞 Kisi bhi samasya ke liye admin se sampark karein.", reply_markup=kb, parse_mode="Markdown")

# Instant Auto-Forward Listener for Channel Posts
@dp.channel_post()
async def auto_forward_channel_posts(message: types.Message):
    if not bot_config["active"]:
        return
    
    src = bot_config["source"]
    tgt = bot_config["target"]
    
    # Check if message is from the configured source channel
    if src and (str(message.chat.id) == str(src) or message.chat.username == src.replace("@", "")):
        if tgt:
            try:
                await message.forward(chat_id=tgt)
            except Exception as e:
                logging.error(f"Forwarding Error: {e}")

# Web server for Render port requirement
async def handle_web(request):
    return web.Response(text="Bot is running smoothly 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    print("Bot and Web Server started successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
