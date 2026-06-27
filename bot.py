from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import TOKEN
from kyc import start, button, handle_message
from admin import admin

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(
    CallbackQueryHandler(
        button,
        pattern="^(continue|dashboard|deposit|withdraw|referral|approve_.*|reject_.*|withdraw_approve_.*|withdraw_reject_.*)$"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("Bot is running...")
app.run_polling()