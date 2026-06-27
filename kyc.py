from referral import referral_button
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from deposit import (
    deposit_button,
    deposit_amount,
    deposit_txid,
    approve_deposit,
    reject_deposit,
    deposit_history
)

from withdraw import (
    withdraw_button,
    withdraw_amount,
    withdraw_wallet,
    approve_withdraw,
    reject_withdraw,
    withdraw_history
)
from contract import ( contract_button, contract_amount, contract_history )
from database import cursor, conn
from config import ADMIN_ID
from datetime import datetime, timedelta

user_state = {}
user_data = {}

async def start(update, context):

    if context.args:

        print("Referral args =", context.args)

        referrer = int(context.args[0])

        user_data.setdefault(update.effective_user.id, {})

        user_data[update.effective_user.id]["referrer"] = referrer

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (update.effective_user.id,)
    )
    user = cursor.fetchone()

    if user:

        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
        ]

        await update.message.reply_text(
            "📊 تاسو مخکې ثبت شوي یاست.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    keyboard = [
        [InlineKeyboardButton("🚀 KYC پیل کړئ", callback_data="continue")]
    ]

    await update.message.reply_text(
        "🌟 حکيمي هوتک مضاربی شرکت ته ښه راغلاست",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update, context):

    query = update.callback_query
    await query.answer()

    if query.data == "continue":

        user_state[query.from_user.id] = "full_name"

        await query.message.reply_text(
            "🪪 خپل بشپړ نوم داخل کړئ."
        )

    elif query.data == "dashboard":

        keyboard = [
            [InlineKeyboardButton("💵 Deposit/واریز", callback_data="deposit")],
            [InlineKeyboardButton("💸 Withdraw/برداشت", callback_data="withdraw")],
            [InlineKeyboardButton("📜 Withdraw History", callback_data="withdraw_history")],
            [InlineKeyboardButton("📦 Contract/قرارداد", callback_data="contract")],
            [InlineKeyboardButton("📜 Contract History/قرارداد تاریخچه", callback_data="contract_history")],
            [InlineKeyboardButton("👥 Referral/دعوت", callback_data="referral")],
            [InlineKeyboardButton("📜 Deposit History/واریزتاریخچه", callback_data="deposit_history")],
            [
            InlineKeyboardButton(
            "🆘 Support",
            url="https://t.me/hakimihotakLTDsupport"
        )
    ]
]

        cursor.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (query.from_user.id,)
        )

        result = cursor.fetchone()

        balance = result[0] if result else 0

        await query.message.reply_text(
            f"📊 Dashboard\n\n💰 Balance: {balance} USDT",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "deposit":

        await deposit_button(query, user_state)

    elif query.data == "contract":

        await contract_button(
        query,
        user_state
        )

    elif query.data == "contract_history":

        await contract_history(
        query
        )   

    elif query.data == "complete_contracts":

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT user_id, amount
            FROM contracts
            WHERE end_date <= ?
            AND status='Active'
            """,
            (today,)
        )

        contracts = cursor.fetchall()

        completed = 0

        for contract in contracts:

            contract_user_id = contract[0]
            amount = contract[1]

            cursor.execute(
                """
                UPDATE users
                SET balance = balance + ?,
                    active_contract = active_contract - ?
                WHERE user_id=?
                """,
                (amount, amount, contract_user_id)
            )

            cursor.execute(
                """
                UPDATE contracts
                SET status='Completed'
                WHERE user_id=?
                AND amount=?
                AND status='Active'
                """,
                (contract_user_id, amount)
            )

            await context.bot.send_message(
                chat_id=contract_user_id,
                text=(
                    "🎉 ستاسو Contract بشپړ شو.\n\n"
                    f"💰 {amount} USDT اصل پانګه ستاسو Balance ته ستنه شوه."
                )
            )

            completed += 1

        conn.commit()

        await query.message.reply_text(
            f"✅قرارداونه بشپرشو."
        )

    elif query.data == "distribute_profit":

        import random

        cursor.execute(
            """
            SELECT user_id, active_contract
            FROM users
            WHERE active_contract > 0
            """
        )

        users = cursor.fetchall()

        total_users = 0

        for user in users:

            profit_user_id = user[0]
            active_contract = user[1]

            percent = random.uniform(0.002, 0.007)

            profit = active_contract * percent

            cursor.execute(
                """
                INSERT INTO profits (user_id, amount)
                VALUES (?, ?)
                """,
                (profit_user_id, profit)
            )

            cursor.execute(
                """
                UPDATE users
                SET balance = balance + ?
                WHERE user_id=?
                """,
                (profit, profit_user_id)
            )

            await context.bot.send_message(
                chat_id=profit_user_id,
                text=(
                    f"🎉 Daily Profit ترلاسه شو.\n\n"
                    f"💰 Profit: {profit:.2f} USDT\n"
                    f"📦 Active Contract: {active_contract} USDT"
                )
            )

            total_users += 1

        conn.commit()

        await query.message.reply_text(
            f"✅ Profit د {total_users} فعالو Contract لرونکو کاروونکو ته ووېشل شو."
        )

    elif query.data.startswith("approve_"):

        user_id = int(
        query.data.split("_")[1]
        )

        await approve_deposit(
        query,
        context,
        user_id,
        user_data
        )

    elif query.data.startswith("reject_"):

        user_id = int(
        query.data.split("_")[1]
        )

        await reject_deposit(
        query,
        context,
        user_id
        )

    elif query.data == "withdraw":

        await withdraw_button(
        query,
        user_state
        )

    elif query.data.startswith(
       "withdraw_approve_"
        ):

        user_id = int(
        query.data.split("_")[2]
        )

        await approve_withdraw(
        query,
        context,
        user_id,
        user_data
        )

    elif query.data.startswith(
        "withdraw_reject_"
        ):

        user_id = int(
        query.data.split("_")[2]
        )

        await reject_withdraw(
        query,
        context,
        user_id
        )

    elif query.data == "withdraw_history":

        await withdraw_history(query)

    elif query.data == "referral":

        await referral_button(
        query,
        context
        )

    elif query.data == "contract":

        user_state[query.from_user.id] = "contract_amount"

        await query.message.reply_text(
        "📦 د Contract اندازه داخل کړئ.\n\n"
        "⚠️ لږ تر لږه 20 USDT"
        )

    elif query.data == "deposit_history":

        await deposit_history(
        query
        )

    elif query.data == "profit":

        cursor.execute(
            "SELECT total_deposit FROM users WHERE user_id=?",
            (query.from_user.id,)
        )

        result = cursor.fetchone()

        total_deposit = result[0] if result and result[0] else 0

        if total_deposit >= 5000:
            percent = 0.7

        elif total_deposit >= 1000:
            percent = 0.4

        elif total_deposit >= 100:
            percent = 0.2

        else:
            percent = 0

        daily_profit = total_deposit * (percent / 100)

        await query.message.reply_text(
            f"📈 Daily Profit Information\n\n"
            f"💰 Total Deposit: {total_deposit} USDT\n"
            f"📊 Profit Rate: {percent}%\n"
            f"💵 Daily Profit: {daily_profit:.2f} USDT"
        )

async def handle_message(update, context):

    user_id = update.effective_user.id

    print("Current state =", user_state.get(user_id))

    if user_state.get(user_id) == "full_name":

        user_data.setdefault(user_id, {})

        user_data[user_id]["full_name"] = update.message.text        

        user_state[user_id] = "country"

        await update.message.reply_text(
            "🌍 مهرباني وکړئ خپل هېواد داخل کړئ."
        )

    elif user_state.get(user_id) == "country":

        print("country step reached")

        user_data[user_id]["country"] = update.message.text

        print("Referrer =", user_data[user_id].get("referrer"))

        cursor.execute(
        """
        INSERT OR REPLACE INTO users
        (user_id, full_name, country, referrer)
        VALUES (?, ?, ?, ?)
        """,
        (
        user_id,
        user_data[user_id]["full_name"],
        user_data[user_id]["country"],
        user_data[user_id].get("referrer")
        )
        )
        conn.commit()
        print("User saved successfully")
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
        ]

        await update.message.reply_text(
            "✅ KYC Database ته ذخیره شو",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif user_state.get(user_id) == "deposit_amount":

        print("calling deposit_amount")

        await deposit_amount(
        update,
        user_state,
        user_data
        )

    elif user_state.get(user_id) == "waiting_after_address":

        user_state[user_id] = "deposit_txid"

        await update.message.reply_text(
        "🆔 مهرباني وکړئ TXID داخل کړئ."
        )

    elif user_state.get(user_id) == "deposit_txid":

        await deposit_txid(
        update,
        context,
        user_state,
        user_data
        )

    elif user_state.get(user_id) == "withdraw_amount":

        await withdraw_amount(
        update,
        user_state,
        user_data
        )

    elif user_state.get(user_id) == "contract_amount":

        await contract_amount(
        update,
        user_state
        )

    elif user_state.get(user_id) == "withdraw_wallet":

        await withdraw_wallet(
        update,
        context,
        user_data
        )