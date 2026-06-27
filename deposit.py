from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import cursor, conn
from config import ADMIN_ID

async def deposit_button(query, user_state):

    user_state[query.from_user.id] = "deposit_amount"

    await query.message.reply_text(
        "💵 مهرباني وکړئ د Deposit اندازه داخل کړئ."
    )

async def deposit_amount(update, user_state, user_data):

    print("deposit_amount reached")

    user_id = update.effective_user.id

    user_data.setdefault(user_id, {})

    user_data[user_id]["deposit_amount"] = update.message.text

    user_state[user_id] = "waiting_after_address"

    print("sending address...")

    await update.message.reply_text(
        "🔗 د USDT (BEP20):\n\n"
        "0x600b1986562d2a8fab887677559340154221d373\n\n"
        "✅ پیسې ولېږئ او بیا هر پیغام واستوئ."
    )

    print("address sent")

async def deposit_txid(update, context, user_state, user_data):

    user_id = update.effective_user.id

    user_data[user_id]["txid"] = update.message.text

    cursor.execute(
        """
        INSERT INTO deposits
        (user_id, amount, txid, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            float(user_data[user_id]["deposit_amount"]),
            user_data[user_id]["txid"],
            "Pending"
        )
    )

    conn.commit()

    await update.message.reply_text(
        "✅ ستاسو Deposit درخواست اډمین ته واستول شو.\n"
        "⏳ د تایید انتظار وکړئ."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💰 نوی Deposit\n\n"
            f"👤 User ID: {user_id}\n"
            f"💵 Amount: {user_data[user_id]['deposit_amount']}\n"
            f"🆔 TXID: {user_data[user_id]['txid']}"
        ),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Approve",
                    callback_data=f"approve_{user_id}"
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ])
    )

async def approve_deposit(
    query,
    context,
    user_id,
    user_data
):

    amount = user_data[user_id]["deposit_amount"]

    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id=?",
        (float(amount), user_id)
    )

    cursor.execute(
        "UPDATE users SET total_deposit = total_deposit + ? WHERE user_id=?",
        (float(amount), user_id)
    )

    cursor.execute(
        "SELECT referrer FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result and result[0]:

        level1_id = result[0]
        level1_bonus = float(amount) * 0.03

        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?",
            (level1_bonus, level1_id)
        )

        await context.bot.send_message(
            chat_id=level1_id,
            text=(
                f"🎉 تاسو "
                f"{level1_bonus} USDT "
                f"Level 1 Referral Bonus ترلاسه کړ."
            )
        )

        cursor.execute(
            "SELECT referrer FROM users WHERE user_id=?",
            (level1_id,)
        )

        level2 = cursor.fetchone()

        if level2 and level2[0]:

            level2_id = level2[0]
            level2_bonus = float(amount) * 0.02

            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id=?",
                (level2_bonus, level2_id)
            )

            await context.bot.send_message(
                chat_id=level2_id,
                text=(
                    f"🎉 تاسو "
                    f"{level2_bonus} USDT "
                    f"Level 2 Referral Bonus ترلاسه کړ."
                )
            )

    conn.commit()

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ ستاسو Deposit د اډمین لخوا تایید شو."
    )

    await query.message.reply_text(
        "✅ Deposit Approved"
    )

async def reject_deposit(
    query,
    context,
    user_id
):

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ ستاسو Deposit رد شو."
    )

    await query.message.reply_text(
        "❌ Deposit Rejected"
    )

async def deposit_history(
    query
):

    cursor.execute(
        """
        SELECT amount, txid, status
        FROM deposits
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (query.from_user.id,)
    )

    deposits = cursor.fetchall()

    if not deposits:

        await query.message.reply_text(
            "📜 Deposit History نشته."
        )

    else:

        text = "📜 Deposit History\n\n"

        for dep in deposits:

            text += (
                f"💵 Amount: {dep[0]}\n"
                f"🆔 TXID: {dep[1]}\n"
                f"📌 Status: {dep[2]}\n\n"
            )

        await query.message.reply_text(
            text
        )