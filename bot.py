import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from keep_alive import keep_alive
import os

# 🔐 Configurations
ADMIN_ID = 6243881362  # ⬅️ এখানে আপনার numeric Telegram ID দিন
BOT_TOKEN = "7954426456:AAHJmRXrU_SQ-VyUIceOW-fCGIxIqJ5y7Lo"
ACCESS_KEY = "XT54JUI"

# 🔢 Steps
(ASK_KEY, APP_NAME, EMAIL, PHONE, BKASH, NAGAD, ROCKET, LOGO) = range(8)

# 🌐 Keep alive
keep_alive()

# 📦 User Data Store
user_inputs = {}

# 📋 Logging
logging.basicConfig(level=logging.INFO)

# ▶️ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 স্বাগতম {update.effective_user.first_name}!\n\n"
        f"অ্যাপ অর্ডার করতে নিচের Access Key দিন:"
    )
    return ASK_KEY

# 🔐 Access Key
async def ask_app_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text.strip()
    if key == ACCESS_KEY:
        user_inputs[update.effective_user.id] = {}
        await update.message.reply_text("✅ সঠিক Key!\n\n📱 এখন আপনার App Name দিন:")
        return APP_NAME
    else:
        await update.message.reply_text(
            "❌ ভুল Key!\n\n"
            "🔐 দয়া করে সঠিক Key দিন অথবা SWYGEN BD এর সাথে যোগাযোগ করুন!\n"
            "📩 https://t.me/Swygen_bd"
        )
        return ASK_KEY

# 📝 App Name
async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["app_name"] = update.message.text.strip()
    await update.message.reply_text("📧 এখন আপনার যোগাযোগের Email দিন:")
    return EMAIL

# 📝 Email
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["email"] = update.message.text.strip()
    await update.message.reply_text("📞 ফোন নম্বর দিন:")
    return PHONE

# 📝 Phone
async def ask_bkash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["phone"] = update.message.text.strip()
    await update.message.reply_text("📲 বিকাশ নাম্বার দিন:")
    return BKASH

# 📝 Bkash
async def ask_nagad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["bkash"] = update.message.text.strip()
    await update.message.reply_text("💳 নগদ নাম্বার দিন:")
    return NAGAD

# 📝 Nagad
async def ask_rocket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["nagad"] = update.message.text.strip()
    await update.message.reply_text("🏦 রকেট নাম্বার দিন:")
    return ROCKET

# 🖼️ Request Logo
async def ask_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["rocket"] = update.message.text.strip()
    await update.message.reply_text("🖼️ এখন আপনার App এর লোগো আপলোড করুন (একটি ছবি দিন):")
    return LOGO

# ✅ Final Logo Receive
async def receive_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.photo:
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = f"{user_id}_logo.jpg"
        await photo_file.download_to_drive(file_path)

        data = user_inputs.get(user_id, {})
        summary = f"""
📥 নতুন অ্যাপ অর্ডার:

👤 ইউজার: {update.effective_user.first_name}
🆔 ইউজারনেম: @{update.effective_user.username or 'N/A'}
🆔 ইউজার আইডি: {update.effective_user.id}

📱 App Name: {data.get("app_name")}
📧 Email: {data.get("email")}
📞 Phone: {data.get("phone")}
📲 বিকাশ: {data.get("bkash")}
💳 নগদ: {data.get("nagad")}
🏦 রকেট: {data.get("rocket")}
"""

        # ➤ Send text + logo to admin
        await context.bot.send_message(chat_id=ADMIN_ID, text=summary)
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=InputFile(file_path))

        # ➤ Confirm to user
        await update.message.reply_text(
            "✅ আপনার অর্ডার গ্রহণ করা হয়েছে!\n\n"
            "🛠️ অ্যাপ তৈরির কাজ চলছে। ৪৮ ঘণ্টার মধ্যে SWYGEN টিম আপনার সাথে যোগাযোগ করবে।\n\nধন্যবাদ!"
        )

        os.remove(file_path)
        user_inputs.pop(user_id, None)
        return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ দয়া করে একটি বৈধ ছবি দিন:")
        return LOGO

# ❌ Cancel Option
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ প্রক্রিয়া বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ▶️ Run Bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_app_name)],
            APP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_bkash)],
            BKASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_nagad)],
            NAGAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_rocket)],
            ROCKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_logo)],
            LOGO: [MessageHandler(filters.PHOTO, receive_logo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
