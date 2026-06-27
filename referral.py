from database import cursor

async def referral_button(query, context):

    user_id = query.from_user.id

    cursor.execute(
        "SELECT user_id FROM users WHERE referrer=?",
        (user_id,)
    )

    level1_users = cursor.fetchall()
    level1_count = len(level1_users)

    level2_count = 0

    for user in level1_users:

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE referrer=?",
            (user[0],)
        )

        level2_count += cursor.fetchone()[0]

    total_team = level1_count + level2_count

    bot_username = (await context.bot.get_me()).username

    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    await query.message.reply_text(
        f"👥 ستاسو Referral لینک:\n\n{ref_link}\n\n"
        f"🥇 Level 1 Referrals: {level1_count}\n"
        f"🥈 Level 2 Referrals: {level2_count}\n"
        f"👨‍👩‍👧‍👦 Total Team: {total_team}"
    )