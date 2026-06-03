import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
CATEGORIES = {
    "Nalichnik": "Nalichnik turlari",
    "Ustun": "Ustun turlari",
    "Rom": "Rom turlari",
    "Korniz": "Korniz turlari",
    "Boshqa": "Boshqa elementlar",
}

CHOOSING, RAZMER, CUSTOM_PHOTO = range(3)

orders = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = []
    for cat in CATEGORIES.keys():
        keyboard.append([KeyboardButton(cat)])
    keyboard.append([KeyboardButton("Mening buyurtmalarim")])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum, " + user.first_name + "!\n\n"
        "PenoDecorPro botiga xush kelibsiz!\n"
        "Quyidagi kategoriyalardan birini tanlang:",
        reply_markup=markup
    )
    return CHOOSING
  async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    if text == "Mening buyurtmalarim":
        uid = user.id
        if uid in orders and orders[uid]:
            msg = "Sizning buyurtmalaringiz:\n\n"
            for i, o in enumerate(orders[uid], 1):
                msg += str(i) + ". " + o["category"] + "\n"
                msg += "   O'lcham: " + o["razmer"] + "\n\n"
        else:
            msg = "Hozircha buyurtma yo'q."
        await update.message.reply_text(msg)
        return CHOOSING
    if text in CATEGORIES:
        context.user_data["category"] = text
        keyboard = [
            [InlineKeyboardButton("O'z rasmimni yuboraman", callback_data="custom_photo")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text + " kategoriyasini tanladingiz.\n\n"
            "Namuna rasmingizni yuboring yoki tugmani bosing:",
            reply_markup=markup
        )
        return CUSTOM_PHOTO
    await update.message.reply_text("Iltimos, menyudan tanlang.")
    return CHOOSING
    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "custom_photo":
        await query.message.reply_text("Rasmingizni yuboring:")
        return CUSTOM_PHOTO
    return CHOOSING


async def custom_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        context.user_data["photo_id"] = photo.file_id
        await update.message.reply_text(
            "Rasmingiz qabul qilindi!\n\n"
            "Endi o'lchamlarni kiriting:\n"
            "Masalan: Eni 50sm, Boyi 120sm, Qalinligi 3sm"
        )
        if ADMIN_ID:
            cat = context.user_data.get("category", "Noma'lum")
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption="Yangi namuna!\nMijoz: " + user.first_name + "\nID: " + str(user.id) + "\nKategoriya: " + cat
            )
        return RAZMER
    await update.message.reply_text("Iltimos, rasm yuboring.")
    return CUSTOM_PHOTO
  async def razmer_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    razmer = update.message.text
    category = context.user_data.get("category", "Noma'lum")
    if user.id not in orders:
        orders[user.id] = []
    orders[user.id].append({
        "category": category,
        "razmer": razmer
    })
    await update.message.reply_text(
        "Buyurtmangiz qabul qilindi!\n\n"
        "Kategoriya: " + category + "\n"
        "O'lcham: " + razmer + "\n\n"
        "Tez orada narxni hisoblab, sizga yuboramiz. Rahmat!"
    )
    if ADMIN_ID:
        msg = (
            "YANGI BUYURTMA!\n\n"
            "Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
            "ID: " + str(user.id) + "\n"
            "Kategoriya: " + category + "\n"
            "O'lcham: " + razmer
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return CHOOSING
    async def send_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Ishlatish: /narx [mijoz_id] [narx va xabar]")
        return
    try:
        client_id = int(args[0])
        price_text = " ".join(args[1:])
        await context.bot.send_message(
            chat_id=client_id,
            text="Sizning buyurtmangiz narxi:\n\n" + price_text
        )
        await update.message.reply_text("Narx mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text("Xato: " + str(e))


def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen)],
            CUSTOM_PHOTO: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.PHOTO, custom_photo_received),
            ],
            RAZMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, razmer_received)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", send_price))
    app.run_polling()


if __name__ == "__main__":
    main()
