import asyncio
import logging
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Aapka Bot Token aur Admin ID pehle se added hai
BOT_TOKEN = "8916721054:AAFSTYY9zpAe2xm1MNdqJjLW6UNC6-mQmTQ"
ADMIN_ID = 7211171229

# Temporary memory mein keys store karne ke liye
GENERATED_KEYS = set()
USED_KEYS = set()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Forwarding Panel Menu
def get_forwarding_panel_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Set Source(s) 📥", callback_data="set_sources"),
         InlineKeyboardButton(text="Set Target 📤", callback_data="set_target")],
        [InlineKeyboardButton(text="Text Template 📝 (Premium)", callback_data="text_template")],
        [InlineKeyboardButton(text="Start Forwarding 🚀", callback_data="start_forwarding"),
         InlineKeyboardButton(text="Stop 🛑", callback_data="stop_forwarding")],
        [InlineKeyboardButton(text="🔄 Reset Config", callback_data="reset_config")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")]
    ])

# Main Menu (Admin ke liye Admin Key Panel ka button dikhega)
def get_main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="⚙️ Forwarding Panel", callback_data="forwarding_panel")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile"),
         InlineKeyboardButton(text="🤝 Referral", callback_data="referral")],
        [InlineKeyboardButton(text="📞 Support", callback_data="support")],
        [InlineKeyboardButton(text="🚪 Logout Account", callback_data="logout")]
    ]
    if is_admin:
        buttons.insert(0, [InlineKeyboardButton(text="🔑 Admin Key Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# /start command handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_admin = (message.from_user.id == ADMIN_ID)
    welcome_text = (
        "⚙️ **FORWARDING PANEL**\n"
        "Manage your automated tasks below:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(is_admin=is_admin), parse_mode="Markdown")

# Callback queries handler (Buttons ke liye)
@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    is_admin = (user_id == ADMIN_ID)
    
    if data == "forwarding_panel":
        await callback.message.edit_text(
            "⚙️ **FORWARDING PANEL**\nManage your automated tasks below:",
            reply_markup=get_forwarding_panel_menu(),
            parse_mode="Markdown"
        )
    elif data == "admin_panel":
        if not is_admin:
            await callback.answer("⚠️ Yeh section sirf Admin ke liye hai!", show_alert=True)
            return
        await callback.message.edit_text(
            "🔑 **Admin Key Generator Panel**\nYahan se aap naye subscription keys bana sakte hain:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Generate New Key", callback_data="gen_key")],
                [InlineKeyboardButton(text="📋 View All Keys", callback_data="view_keys")],
                [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
    elif data == "gen_key":
        if not is_admin:
            return
        chars = string.ascii_uppercase + string.digits
        new_key = "MF-" + "".join(random.choices(chars, k=10))
        GENERATED_KEYS.add(new_key)
        await callback.message.edit_text(
            f"✅ **Nayi Key Successfully Ban Gayi Hai!**\n\n`{new_key}`",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Admin Panel", callback_data="admin_panel")]
            ]),
            parse_mode="Markdown"
        )
    elif data == "view_keys":
        if not is_admin:
            return
        keys_list = "\n".join(f"• `{k}`" for k in GENERATED_KEYS) if GENERATED_KEYS else "Koi key nahi bani hai."
        await callback.message.edit_text(
            f"📋 **All Generated Keys:**\n\n{keys_list}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Admin Panel", callback_data="admin_panel")]
            ]),
            parse_mode="Markdown"
        )
    elif data == "set_sources":
        await callback.answer("Source channel set karne ke liye channel link bhejein.", show_alert=True)
    elif data == "set_target":
        await callback.answer("Target channel set karne ke liye channel link bhejein.", show_alert=True)
    elif data == "start_forwarding":
        await callback.answer("🚀 Forwarding shuru ho gayi hai!", show_alert=True)
    elif data == "stop_forwarding":
        await callback.answer("🛑 Forwarding rok di gayi hai!", show_alert=True)
    elif data == "reset_config":
        await callback.answer("🔄 Config reset ho gaya hai!", show_alert=True)
    elif data == "my_profile":
        await callback.message.edit_text(
            "👤 **Your Profile**\n\nStatus: Free / Trial",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
    elif data == "main_menu":
        await callback.message.edit_text("Main Menu:", reply_markup=get_main_menu(is_admin=is_admin))
    else:
        await callback.answer("Feature under development!", show_alert=True)

# Main function
async def main():
    print("Bot is running successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
