import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

KATALOG_LINKS = {
    "Rom bezaklari": "https://muzaffar57.github.io/-penodecor-katalog/katalog.html",
    "Ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/ustun.html",
    "Belbog' karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/belbog.html",
    "Yumaloq ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/yumaloq.html",
    "Kapitel va baza": "https://muzaffar57.github.io/-penodecor-katalog/kapitel.html",
    "Kalvak": "https://muzaffar57.github.io/-penodecor-katalog/kalvak.html",
    "Karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/karniz.html",
    "Shohona karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/shohona.html",
    "Termopanellar": "https://muzaffar57.github.io/-penodecor-katalog/termopanel.html",
    "Barelef gullar": "https://muzaffar57.github.io/-penodecor-katalog/barelef.html",
}

KATALOG_COUNTS = {
    "Rom bezaklari": 16,
    "Ustunlar": 13,
    "Belbog' karnizlar": 27,
    "Yumaloq ustunlar": 13,
    "Kapitel va baza": 16,
    "Kalvak": 16,
    "Karnizlar": 16,
    "Shohona karnizlar": 16,
    "Termopanellar": 16,
    "Barelef gullar": 16,
}

CHOOSING, MODEL_SELECTION, QOPLAMA, RAZMER, LOYIHA_PHOTO, FASAD_PHOTO, CUSTOM_PHOTO = range(7)

orders = {}

OLCHAM_SHABLON = (
    "📐 O'lchamlarni kiriting:\n\n"
    "Bo'yi: ___\n"
    "Qalinligi: ___\n"
    "Uzunligi (metr): ___\n"
    "Soni (dona): ___\n\n"
    "Namuna:\n"
    "Bo'yi: 20sm\n"
    "Qalinligi: 5sm\n"
    "Uzunligi (metr): 3\n"
    "Soni (dona): 10"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("Rom bezaklari"), KeyboardButton("Ustunlar")],
        [KeyboardButton("Belbog' karnizlar"), KeyboardButton("Yumaloq ustunlar")],
        [KeyboardButton("Kapitel va baza"), KeyboardButton("Kalvak")],
        [KeyboardButton("Karnizlar"), KeyboardButton("Shohona karnizlar")],
        [KeyboardButton("Termopanellar"), KeyboardButton("Barelef gullar")],
        [KeyboardButton("📐 Loyiha bo'yicha hisoblash")],
        [KeyboardButton("🏠 Fasad loyihasi tayyorlash")],
        [KeyboardButton("🏗️ Bajarilgan loyihalar")],
        [KeyboardButton("🌟 Keng qamrovlik yechim")],
        [KeyboardButton("📋 Mening buyurtmalarim")],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum, " + user.first_name + "!\n\n"
        "PenoDecorPro botiga xush kelibsiz!\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=markup
    )
    return CHOOSING


async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "📋 Mening buyurtmalarim":
        uid = user.id
        if uid in orders and orders[uid]:
            msg = "Sizning buyurtmalaringiz:\n\n"
            for i, o in enumerate(orders[uid], 1):
                msg += str(i) + ". " + o["category"] + "\n"
                msg += "   Model: " + o.get("model", "Noma'lum") + "\n"
                msg += "   Qoplama: " + o.get("qoplama", "Yo'q") + "\n"
                msg += "   O'lcham: " + o.get("razmer", "Noma'lum") + "\n\n"
        else:
            msg = "Hozircha buyurtma yo'q."
        await update.message.reply_text(msg)
        return CHOOSING

    if text == "📐 Loyiha bo'yicha hisoblash":
        context.user_data["category"] = text
        await update.message.reply_text(
            "📐 Loyiha bo'yicha hisoblash\n\n"
            "Loyihangiz rasmini yuboring — biz ko'rib chiqib narx hisoblaymiz."
        )
        return LOYIHA_PHOTO

    if text == "🏠 Fasad loyihasi tayyorlash":
        context.user_data["category"] = text
        await update.message.reply_text(
            "🏠 Fasad loyihasi tayyorlash\n\n"
            "Uyingizning fasad rasmini yuboring va yoqtirgan modellarni yozing.\n"
            "Biz kompyuter grafika yordamida loyiha tayyorlab yuboramiz!"
        )
        return FASAD_PHOTO

    if text == "🏗️ Bajarilgan loyihalar":
        await update.message.reply_text(
            "🏗️ Bajarilgan loyihalarni ko'rish uchun:\n\n"
            "https://muzaffar57.github.io/-penodecor-katalog/loyihalar.html"
        )
        return CHOOSING

    if text == "🌟 Keng qamrovlik yechim":
        await update.message.reply_text(
            "🌟 Keng qamrovlik yechim\n\n"
            "Tayyor dizayn paketlari va detallar to'plamlari:\n\n"
            "https://muzaffar57.github.io/-penodecor-katalog/yechim.html"
        )
        return CHOOSING

    if text in KATALOG_LINKS:
        context.user_data["category"] = text
        count = KATALOG_COUNTS.get(text, 16)
        link = KATALOG_LINKS[text]

        row = []
        model_buttons = []
        for i in range(1, count + 1):
            row.append(InlineKeyboardButton("MODEL-" + str(i).zfill(2), callback_data="model_" + str(i).zfill(2)))
            if len(row) == 4:
                model_buttons.append(row)
                row = []
        if row:
            model_buttons.append(row)
        model_buttons.append([InlineKeyboardButton("📷 O'z rasmimni yuboraman", callback_data="custom_photo")])

        markup = InlineKeyboardMarkup(model_buttons)
        await update.message.reply_text(
            text + " katalogi:\n\n"
            "Katalogni ko'rish: " + link + "\n\n"
            "Yoqtirgan modelingizni tanlang:",
            reply_markup=markup
        )
        return MODEL_SELECTION

    await update.message.reply_text("Iltimos, menyudan tanlang.")
    return CHOOSING


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("model_"):
        model = "MODEL-" + query.data.replace("model_", "")
        context.user_data["model"] = model
        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await query.message.reply_text(
            "Siz " + model + " ni tanladingiz!\n\n"
            "Qoplama tortilsinmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return QOPLAMA

    if query.data == "custom_photo":
        await query.message.reply_text("Namuna rasmingizni yuboring:")
        return CUSTOM_PHOTO

    if query.data == "qoplama_ha":
        context.user_data["qoplama"] = "Ha (x2 narx)"
        await query.message.reply_text(OLCHAM_SHABLON)
        return RAZMER

    if query.data == "qoplama_yoq":
        context.user_data["qoplama"] = "Yo'q"
        await query.message.reply_text(OLCHAM_SHABLON)
        return RAZMER

    return CHOOSING


async def razmer_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    razmer = update.message.text
    category = context.user_data.get("category", "Noma'lum")
    model = context.user_data.get("model", "Noma'lum")
    qoplama = context.user_data.get("qoplama", "Yo'q")

    if user.id not in orders:
        orders[user.id] = []
    orders[user.id].append({
        "category": category,
        "model": model,
        "razmer": razmer,
        "qoplama": qoplama
    })

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "Bo'lim: " + category + "\n"
        "Model: " + model + "\n"
        "Qoplama: " + qoplama + "\n"
        "O'lcham:\n" + razmer + "\n\n"
        "Tez orada narxni hisoblab, sizga yuboramiz. Rahmat! 🙏"
    )

    if ADMIN_ID:
        msg = (
            "🆕 YANGI BUYURTMA!\n\n"
            "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
            "🆔 ID: " + str(user.id) + "\n"
            "📦 Bo'lim: " + category + "\n"
            "🎨 Model: " + model + "\n"
            "🖌 Qoplama: " + qoplama + "\n"
            "📐 O'lcham:\n" + razmer
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    return CHOOSING


async def loyiha_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        await update.message.reply_text(
            "✅ Loyihangiz qabul qilindi!\n\n"
            "Mutaxassislarimiz ko'rib chiqib, tez orada narx yuboramiz. Rahmat! 🙏"
        )
        if ADMIN_ID:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption=(
                    "📐 LOYIHA BO'YICHA HISOBLASH!\n\n"
                    "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
                    "🆔 ID: " + str(user.id)
                )
            )
        return CHOOSING
    await update.message.reply_text("Iltimos, rasm yuboring.")
    return LOYIHA_PHOTO


async def fasad_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    caption = update.message.caption or ""
    if photo:
        await update.message.reply_text(
            "✅ Fasad rasmingiz qabul qilindi!\n\n"
            "Dizaynerlarimiz loyiha tayyorlab, tez orada yuboramiz. Rahmat! 🙏"
        )
        if ADMIN_ID:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption=(
                    "🏠 FASAD LOYIHASI TAYYORLASH!\n\n"
                    "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
                    "🆔 ID: " + str(user.id) + "\n"
                    "📝 Izoh: " + caption
                )
            )
        return CHOOSING
    await update.message.reply_text("Iltimos, fasad rasmini yuboring.")
    return FASAD_PHOTO


async def custom_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        context.user_data["model"] = "Mijoz namunasi"
        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await update.message.reply_text(
            "Rasmingiz qabul qilindi!\n\nQoplama tortilsinmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        if ADMIN_ID:
            cat = context.user_data.get("category", "Noma'lum")
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption="📷 Yangi namuna rasmi!\n👤 Mijoz: " + user.first_name + "\n🆔 ID: " + str(user.id) + "\n📦 Bo'lim: " + cat
            )
        return QOPLAMA
    await update.message.reply_text("Iltimos, rasm yuboring.")
    return CUSTOM_PHOTO


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
            text="💰 Sizning buyurtmangiz narxi:\n\n" + price_text
        )
        await update.message.reply_text("✅ Narx mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text("Xato: " + str(e))


def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen)],
            MODEL_SELECTION: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.PHOTO, custom_photo_received),
            ],
            QOPLAMA: [CallbackQueryHandler(button_handler)],
            RAZMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, razmer_received)],
            LOYIHA_PHOTO: [MessageHandler(filters.PHOTO, loyiha_photo_received)],
            FASAD_PHOTO: [
                MessageHandler(filters.PHOTO, fasad_photo_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, fasad_photo_received),
            ],
            CUSTOM_PHOTO: [MessageHandler(filters.PHOTO, custom_photo_received)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", send_price))
    app.run_polling()


if __name__ == "__main__":
    main()
