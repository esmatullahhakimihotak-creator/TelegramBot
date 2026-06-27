from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_ID

async def admin(update, context):

    print("User ID =", update.effective_user.id)
    print("Admin ID =", ADMIN_ID)

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("📈 Distribute Profit", callback_data="distribute_profit")],
        [InlineKeyboardButton("🔓 Complete Expired Contracts", callback_data="complete_contracts")]
    ]

    await update.message.reply_text(
        "🛠 Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

