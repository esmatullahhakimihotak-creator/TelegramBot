from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import cursor, conn
from config import ADMIN_ID

async def withdraw_button(
    query,
    user_state
):

    user_state[
        query.from_user.id
    ] = "withdraw_amount"

    await query.message.reply_text(
        "💸 مهرباني وکړئ د Withdraw اندازه داخل کړئ."
    )

async def withdraw_amount(
    update,
    user_state,
    user_data
):

    user_id = update.effective_user.id

    amount = float(update.message.text)

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    balance = result[0] if result else 0

    if amount > balance:

        await update.message.reply_text(
            f"❌ ستاسو Balance {balance} USDT دی."
        )
        return

    commission = amount * 0.10
    payable_amount = amount - commission

    user_data.setdefault(user_id, {})

    user_data[user_id]["withdraw_amount"] = amount
    user_data[user_id]["commission"] = commission
    user_data[user_id]["payable_amount"] = payable_amount

    user_state[user_id] = "withdraw_wallet"

    await update.message.reply_text(
        f"💸 Withdraw Amount: {amount} USDT\n"
        f"💰 Commission (10%): {commission:.2f} USDT\n"
        f"✅ Final Amount: {payable_amount:.2f} USDT\n\n"
        f"🏦 مهرباني وکړئ د USDT BEP20 Wallet Address داخل کړئ."
    )

async def withdraw_wallet(
    update,
    context,
    user_data
):

    user_id = update.effective_user.id

    wallet = update.message.text

    user_data[user_id]["wallet"] = wallet

    amount = user_data[user_id]["withdraw_amount"]

    cursor.execute(
    """
    INSERT INTO withdrawals
    (user_id, amount, wallet, status)
    VALUES (?, ?, ?, ?)
    """,
    (
        user_id,
        amount,
        wallet,
        "Pending"
        )
    )

    conn.commit()

    commission = user_data[user_id]["commission"]
    payable_amount = user_data[user_id]["payable_amount"]

    await update.message.reply_text(
        "✅ ستاسو Withdraw غوښتنه اډمین ته واستول شوه.\n"
        "⏳ د تایید انتظار وکړئ."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💸 نوی Withdraw Request\n\n"
            f"👤 User ID: {user_id}\n"
            f"💵 Requested Amount: {amount} USDT\n"
            f"💰 Commission (10%): {commission:.2f} USDT\n"
            f"✅ Payable Amount: {payable_amount:.2f} USDT\n"
            f"🏦 Wallet: {wallet}"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=f"withdraw_approve_{user_id}"
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"withdraw_reject_{user_id}"
                )
            ]
        ])
    )

async def approve_withdraw(
    query,
    context,
    user_id,
    user_data
):

    amount = float(
        user_data[user_id]["withdraw_amount"]
    )

    cursor.execute(
        """
        UPDATE users
        SET balance = balance - ?
        WHERE user_id=?
        """,
        (
            amount,
            user_id
        )
    )

    conn.commit()

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "✅ ستاسو Withdraw د اډمین لخوا تایید شو."
        )
    )

    await query.message.reply_text(
        "✅ Withdraw Approved"
    )

async def reject_withdraw(
    query,
    context,
    user_id
):

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ ستاسو Withdraw د اډمین لخوا رد شو."
    )

    await query.message.reply_text(
        "❌ Withdraw Rejected"
    )

async def withdraw_history(query):

    cursor.execute(
        """
        SELECT amount, wallet, status
        FROM withdrawals
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (query.from_user.id,)
    )

    withdrawals = cursor.fetchall()

    if not withdrawals:

        await query.message.reply_text(
            "📜 Withdraw History نشته."
        )

    else:

        text = "📜 Withdraw History\n\n"

        for wd in withdrawals:

            text += (
                f"💵 Amount: {wd[0]} USDT\n"
                f"🏦 Wallet: {wd[1]}\n"
                f"📌 Status: {wd[2]}\n\n"
            )

        await query.message.reply_text(text)