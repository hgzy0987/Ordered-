import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from keep_alive import keep_alive
import tempfile

# ====== CONFIG ======
BOT_TOKEN = "7954426456:AAHJmRXrU_SQ-VyUIceOW-fCGIxIqJ5y7Lo"
ADMIN_ID = 6243881362  # আপনার numeric Telegram ID
ACCESS_KEY = "XT54JUI"
IMGBB_API = "3305fbf17e54a31c5ee46795eed61dd0"

# Conversation states
(ASK_KEY, APP_NAME, EMAIL, PHONE, BKASH, NAGAD, ROCKET, LOGO) = range(8)

user_inputs = {}
keep_alive()
logging.basicConfig(level=logging.INFO)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n\nঅ্যাপ অর্ডার করতে 🔐 Access Key দিন:"
    )
    return ASK_KEY

# Access Key
async def ask_app_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == ACCESS_KEY:
        user_inputs[update.effective_user.id] = {}
        await update.message.reply_text("✅ সঠিক Key!\n\n📱 App Name দিন:")
        return APP_NAME
    else:
        await update.message.reply_text(
            "❌ ভুল Key!\n\n"
            "দয়া করে সঠিক Key দিন অথবা SWYGEN BD এর সাথে যোগাযোগ করুন!\n"
            "📩 https://t.me/Swygen_bd"
        )
        return ASK_KEY

# App Info Steps
async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["app_name"] = update.message.text.strip()
    await update.message.reply_text("📧 যোগাযোগ Email দিন:")
    return EMAIL

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["email"] = update.message.text.strip()
    await update.message.reply_text("📞 ফোন নম্বর দিন:")
    return PHONE

async def ask_bkash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["phone"] = update.message.text.strip()
    await update.message.reply_text("📲 বিকাশ নাম্বার দিন:")
    return BKASH

async def ask_nagad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["bkash"] = update.message.text.strip()
    await update.message.reply_text("💳 নগদ নাম্বার দিন:")
    return NAGAD

async def ask_rocket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["nagad"] = update.message.text.strip()
    await update.message.reply_text("🏦 রকেট নাম্বার দিন:")
    return ROCKET

async def ask_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_inputs[update.effective_user.id]["rocket"] = update.message.text.strip()
    await update.message.reply_text("🖼️ এখন আপনার লোগো ছবিটি দিন (ছবি আপলোড করুন):")
    return LOGO

# Upload to ImgBB
def upload_to_imgbb(image_bytes):
    try:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API},
            files={"image": image_bytes},
        )
        data = response.json()
        return data['data']['url']
    except Exception as e:
        print("ImgBB Upload Error:", e)
        return None

# Receive Photo & Finish
async def receive_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not update.message.photo:
        await update.message.reply_text("⚠️ দয়া করে একটি ছবি আপলোড করুন:")
        return LOGO

    photo_file = await update.message.photo[-1].get_file()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        await photo_file.download_to_drive(tf.name)
        with open(tf.name, 'rb') as img:
            image_url = upload_to_imgbb(img)

    if not image_url:
        await update.message.reply_text("❌ ছবি আপলোড ব্যর্থ হয়েছে। আবার চেষ্টা করুন!")
        return LOGO

    data = user_inputs.get(user_id, {})
    message = f"""
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
🖼️ Logo: {image_url}
"""

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)

    # ✅ Success to user
    await update.message.reply_text(
        "✅ ধন্যবাদ!\n\nআপনার অর্ডার সফলভাবে গ্রহণ করা হয়েছে।\n\n"
        "🛠️ অ্যাপ তৈরির কাজ চলছে। ৪৮ ঘণ্টার মধ্যে SWYGEN টিম আপনার সাথে যোগাযোগ করবে।"
    )

    user_inputs.pop(user_id, None)
    return ConversationHandler.END

# CANCEL
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ প্রক্রিয়া বাতিল করা হয়েছে।")
    return ConversationHandler.END

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
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

    app.add_handler(conv)
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
