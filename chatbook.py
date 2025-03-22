import telebot
import random
import threading
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = "7806071446:AAFukCv3jKDCM8cQKnk0UevHzGjCl5QD13E"
CHANNEL_USERNAME = "chatbook29"  # ✅ Channel Username

bot = telebot.TeleBot(API_TOKEN)

queue = {"Male": [], "Female": [], "Any": []}
chats = {}
user_gender = {}
reported_users = {}


# ✅ Check If User Has Joined the Channel (Using Bot Admin Permissions)
def is_user_in_channel(user_id):
    try:
        chat_member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False


# ✅ Fake Online Users Count (Random Number for Engagement)
def get_fake_online_count():
    return random.randint(30000, 70000)


# ✅ Start Command (With Channel Join Verification)
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        bot.send_message(
            user_id,
            f"⚠️ *You must join our channel to use this bot!* Then just type /start and u easily use this bot! \n👉 [Join Here](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown"
        )
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔍 Find Chat"), KeyboardButton("📝 Set Gender"))
    keyboard.add(KeyboardButton("❌ End Chat"))

    bot.send_message(
        user_id,
        f"🔥 Welcome to *ChatBookBot!* 🎉\n\n"
        f"🔹 *{get_fake_online_count()} users* are chatting right now!\n"
        f"💬 Meet new people & chat anonymously.\n\n"
        f"✅ *Commands:*\n"
        f"🔹 /setgender Male/Female - Set your gender\n"
        f"🔹 /find Male/Female/Any - Find a specific gender\n"
        f"🔹 /exitgender - Leave chat if gender mismatch\n"
        f"🔹 /next - Find a new partner\n"
        f"🔹 /report - Report bad user\n"
        f"🔹 /end - Disconnect chat\n\n"
        f"⚠️ *Rules:*\n"
        f"❌ No spamming\n"
        f"❌ No abuse\n"
        f"❌ Be respectful!\n\n"
        f"💡 Stay safe & enjoy chatting!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ✅ Set Gender Command
@bot.message_handler(commands=['setgender'])
def set_gender(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        bot.send_message(
            user_id,
            f"⚠️ You must join our channel first!\n👉 [Join Here](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown"
        )
        return

    gender = message.text.split(" ")[1].capitalize() if len(message.text.split()) > 1 else None

    if gender not in ["Male", "Female"]:
        bot.send_message(user_id, "⚠️ Invalid command! Use: `/setgender Male` or `/setgender Female`")
        return

    user_gender[user_id] = gender
    bot.send_message(user_id, f"✅ Gender set to *{gender}*! You can now search for specific genders.")


# ✅ Find Partner (With Gender-Based Matching Fix)
@bot.message_handler(commands=['find'])
def find_chat(message):
    user_id = message.chat.id

    if not is_user_in_channel(user_id):
        bot.send_message(
            user_id,
            f"⚠️ You must join our channel first!\n👉 [Join Here](https://t.me/{CHANNEL_USERNAME})",
            parse_mode="Markdown"
        )
        return

    if user_id in chats:
        bot.send_message(user_id, "⚠️ You are already in a chat!")
        return

    preference = message.text.split(" ")[1].capitalize() if len(message.text.split()) > 1 else "Any"

    queue[preference].append(user_id)
    bot.send_message(user_id, f"🔍 Searching for a {preference} partner... ({get_fake_online_count()} online)")

    for pref in [preference, "Any"]:
        while queue[pref]:
            partner_id = queue[pref].pop(0)
            if partner_id != user_id:
                chats[user_id] = partner_id
                chats[partner_id] = user_id

                bot.send_message(user_id, f"✅ Partner found! **Gender: {user_gender.get(partner_id, 'Unknown')}**")
                bot.send_message(partner_id, f"✅ Partner found! **Gender: {user_gender.get(user_id, 'Unknown')}**")

                threading.Thread(target=auto_disconnect_timer, args=(user_id, partner_id)).start()
                return


# ✅ Exit Chat If Gender Mismatch
@bot.message_handler(commands=['exitgender'])
def exit_gender_chat(message):
    user_id = message.chat.id
    if user_id in chats:
        partner_id = chats[user_id]
        bot.send_message(user_id, "⚠️ You left the chat due to gender mismatch.")
        bot.send_message(partner_id, "⚠️ Your partner left due to gender mismatch.")
        disconnect_users(user_id, partner_id)
    else:
        bot.send_message(user_id, "⚠️ You're not in a chat!")


# ✅ Auto-Disconnect Timer (3 mins inactivity)
def auto_disconnect_timer(user1, user2):
    time.sleep(180)
    if user1 in chats and chats[user1] == user2:
        bot.send_message(user1, "⏳ 3 minutes up! Chat ended. Type /find to search again.")
        bot.send_message(user2, "⏳ 3 minutes up! Chat ended. Type /find to search again.")
        disconnect_users(user1, user2)


# ✅ Disconnect Users
def disconnect_users(user1, user2):
    if user1 in chats:
        del chats[user1]
    if user2 in chats:
        del chats[user2]
    bot.send_message(user1, "🔄 Want a new chat? Type /find")
    bot.send_message(user2, "🔄 Want a new chat? Type /find")


# ✅ Instant Reconnect Feature
@bot.message_handler(commands=['next'])
def instant_reconnect(message):
    user_id = message.chat.id
    if user_id in chats:
        disconnect_users(user_id, chats[user_id])
    find_chat(message)


# ✅ Start the Bot
bot.polling()