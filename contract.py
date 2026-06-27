from database import cursor, conn
from datetime import datetime, timedelta

async def contract_button(query, user_state):

    user_id = query.from_user.id

    cursor.execute(
        "SELECT active_contract FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    active_contract = result[0] if result else 0

    user_state[user_id] = "contract_amount"

    await query.message.reply_text(
        f"📈 فعاله Contract: {active_contract} USDT\n\n"
        f"📦 د Contract اندازه داخل کړئ.\n"
        f"⚠️ لږ تر لږه 20 USDT"
    )

async def contract_amount(
    update,
    user_state
):

    user_id = update.effective_user.id

    amount = float(update.message.text)

    if amount < 20:

        await update.message.reply_text(
            "❌ لږ تر لږه Contract باید 20 USDT وي."
        )
        return

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    print("USER DATA =", user)

    if not user:
        await update.message.reply_text(
            "❌ ستاسو معلومات په Database کې ونه موندل شول."
        )
        return

    balance = float(user[4])
    active_contract = float(user[7])
    if balance < amount:
        await update.message.reply_text(
            f"❌ ستاسو Balance {balance} USDT دی.\n"
            "کافي نه دی."
        )
        return

    old_active_contract = active_contract
    new_active_contract = old_active_contract + amount

    cursor.execute(
        """
        UPDATE users
        SET balance = balance - ?,
            active_contract = active_contract + ?
        WHERE user_id=?
        """,
        (amount, amount, user_id)
    )

    start_date = datetime.now()
    end_date = start_date + timedelta(days=365)

    cursor.execute(
        """
        INSERT INTO contracts
        (user_id, amount, start_date, end_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            amount,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            "Active"
        )
    )

    conn.commit()

    await update.message.reply_text(
        f"✅ Contract فعال شو.\n\n"
        f"💰 نوې پانګه: {amount} USDT\n"
        f"📈 پخوانۍ فعاله پانګه: {old_active_contract} USDT\n"
        f"📊 ټوله فعاله پانګه: {new_active_contract} USDT"
    )

async def contract_history(query):

    cursor.execute(
        """
        SELECT amount, start_date, end_date, status
        FROM contracts
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (query.from_user.id,)
    )

    contracts = cursor.fetchall()

    if not contracts:

        await query.message.reply_text(
            "📜 تر اوسه Contract History نشته."
        )

    else:

        text = "📜 Contract History\n\n"

        for contract in contracts:

            text += (
                f"💰 Amount: {contract[0]} USDT\n"
                f"📅 Start: {contract[1]}\n"
                f"⏳ End: {contract[2]}\n"
                f"📌 Status: {contract[3]}\n\n"
            )

        await query.message.reply_text(text)