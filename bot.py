import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from keep_alive import keep_alive
import os

# 🔐 Configurations
ADMIN_ID = 6243881362  # এখানে আপনার টেলিগ্রাম ID বসান
ACCESS_KEY = "XT54JUI"
BOT_TOKEN = "7954426456:AAHJmRXrU_SQ-VyUIceOW-fCGIxIqJ5y7Lo"

# 🔢 States
ASK_KEY, ASK_DETAILS, ASK_LOGO = range(3)

# 🌐 Keep alive
keep_alive()

# 🧾 Logger
logging.basicConfig(level=logging.INFO)

# 📦 Temp storage
user_inputs = {}

# ▶️ Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"""👋 স্বাগতম {update.effective_user.first_name}!

এখানে আপনি অ্যাপ অর্ডার করতে পারবেন।

🔐 অনুগ্রহ করে Access Key দিন:"""
    )
    return ASK_KEY

# 🔐 Access Key checker
async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == ACCESS_KEY:
        await update.message.reply_text(
            "✅ সঠিক Key!\n\n"
            "🔽 এখন নিচের ফরম্যাটে তথ্য দিন:\n\n"
            "1️⃣ App Name\n"
            "2️⃣ Email\n"
            "3️⃣ Phone\n"
            "4️⃣ বিকাশ নম্বর\n"
            "5️⃣ নগদ নম্বর\n"
            "6️⃣ রকেট নম্বর"
        )
        return ASK_DETAILS
    else:
        await update.message.reply_text("❌ ভুল Key! আবার দিন:")
        return ASK_KEY

# 📥 Collect Text Info
async def get_app_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = update.message.text.strip().split("\n")
    if len(lines) < 6:
        await update.message.reply_text("⚠️ অনুগ্রহ করে App সংক্রান্ত ৬টি তথ্য দিন। আবার দিন:")
        return ASK_DETAILS

    user_inputs[update.effective_user.id] = {
        "name": lines[0],
        "email": lines[1],
        "phone": lines[2],
        "bkash": lines[3],
        "nagad": lines[4],
        "rocket": lines[5]
    }

    await update.message.reply_text("🖼️ এখন আপনার লোগো ছবি দিন (একটি ছবি আপলোড করুন)")
    return ASK_LOGO

# 📷 Receive Logo
async def get_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = f"{user_id}_logo.jpg"
        await file.download_to_drive(file_path)

        # ⬇️ Text info
        data = user_inputs.get(user_id, {})
        text = f"""📥 নতুন অ্যাপ অর্ডার:

👤 ইউজার: {update.effective_user.first_name}
🆔 ইউজারনেম: @{update.effective_user.username or 'N/A'}
🆔 ইউজার আইডি: {update.effective_user.id}

🔹 App Name: {data.get("name")}
📧 Email: {data.get("email")}
📞 Phone: {data.get("phone")}
📲 বিকাশ: {data.get("bkash")}
💳 নগদ: {data.get("nagad")}
🏦 রকেট: {data.get("rocket")}
"""

        # 📤 Send to Admin
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=InputFile(file_path))

        # ✅ User confirmation
        await update.message.reply_text(
            "✅ আপনার অ্যাপ অর্ডার গ্রহণ করা হয়েছে!\n\n"
            "🛠️ ৪৮ ঘণ্টার মধ্যে আমাদের টিম আপনার সাথে যোগাযোগ করবে।"
        )

        # ✅ Clean up
        os.remove(file_path)
        user_inputs.pop(user_id, None)
        return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ দয়া করে একটি বৈধ ছবি দিন।")
        return ASK_LOGO

# ❌ Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ প্রক্রিয়া বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ▶️ Run Bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_key)],
            ASK_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_app_info)],
            ASK_LOGO: [MessageHandler(filters.PHOTO, get_logo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
