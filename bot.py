import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

SHEET_IDS = {
    "rom": "10AvifJVAE_nWml3U0IEDQU4h2-vsOBZt3MRZII7SYRM",
    "ustun": "18wKIn4C20qkTMfQ5F2V20TJ-VptBK7HCF3dp9-PWGlg",
    "karniz": "13y4wsnY8BwoOiQRFNzrqeZFvY1oxhJcZh0Cd-JGkDAs",
    "belbog": "1gj7bPGtK2Cws9_yvwao1aTLnt7E-dQeb5xmWQx2yNoU",
}

def get_gspread_client():
    import base64
    creds_b64 = os.environ.get("GOOGLE_CREDENTIALS_B64")
    creds_json_str = os.environ.get("GOOGLE_CREDENTIALS")
    logger.info("GOOGLE_CREDENTIALS_B64 exists: " + str(bool(creds_b64)))
    logger.info("GOOGLE_CREDENTIALS exists: " + str(bool(creds_json_str)))
    if creds_b64:
        creds_json_str = base64.b64decode(creds_b64).decode("utf-8")
    creds_dict = json.loads(creds_json_str)
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def parse_narx(narx_str):
    if not narx_str:
        return None
    cleaned = narx_str.replace(" ", "").replace(",", "").replace(".", "").replace("\xa0", "")
    try:
        return int(cleaned)
    except:
        return None

def get_narx(sheet_key, model, razmer, tur=None):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SHEET_IDS[sheet_key])
        ws = sh.get_worksheet(0)
        data = ws.get_all_values()

        for row in data:
            if len(row) < 3:
                continue
            row_model = row[0].strip()
            if not row_model.startswith("MODEL"):
                continue

            if sheet_key == "rom":
                if len(row) < 4:
                    continue
                row_tur = row[1].strip()
                row_razmer = row[2].strip()
                row_narx = row[3].strip()
                if row_model == model and tur and tur in row_tur and razmer in row_razmer:
                    return parse_narx(row_narx)
            else:
                row_razmer = row[1].strip()
                row_narx = row[2].strip()
                if row_model == model and razmer in row_razmer:
                    return parse_narx(row_narx)
    except Exception as e:
        logger.error("Narx olishda xato: " + str(e))
    return None

def format_narx(narx):
    return "{:,}".format(narx).replace(",", " ") + " so'm"

KATALOG_LINKS = {
    "Rom bezaklari": "https://muzaffar57.github.io/-penodecor-katalog/katalog.html",
    "Ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/ustun.html",
    "Belbog' karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/belbog.html",
    "Yumaloq ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/yumaloq.html",
    "Kapitel va baza": "https://muzaffar57.github.io/-penodecor-katalog/kapitel.html",
    "Kalvak": "https://muzaffar57.github.io/-penodecor-katalog/kalvak.html",
    "Karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/karniz.html",
    "Shohona karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/shohona.html",
    "Barelef gullar": "https://muzaffar57.github.io/-penodecor-katalog/barelef.html",
}

KATALOG_COUNTS = {
    "Rom bezaklari": 16,
    "Ustunlar": 13,
    "Belbog' karnizlar": 27,
    "Yumaloq ustunlar": 12,
    "Kapitel va baza": 16,
    "Kalvak": 9,
    "Karnizlar": 26,
    "Shohona karnizlar": 12,
    "Barelef gullar": 7,
}

USTUN_RAZMERLAR = ["25sm", "30sm", "35sm", "40sm", "45sm", "50sm"]
KARNIZ_RAZMERLAR = ["Kichik (17sm)", "Ortacha (20sm)", "Katta (25sm)", "25sm dan katta"]

OLCHAM_SHABLONLAR = {
    "Rom bezaklari": "Nechta rom va nechta eshik bor?\nMasalan: 8 ta rom, 4 ta eshik",
    "Ustunlar": "Qancha metr kerak?\nMasalan: 12 metr",
    "Belbog' karnizlar": "Qancha metr kerak?\nMasalan: 25 metr",
    "Karnizlar": "Qancha metr kerak?\nMasalan: 30 metr",
    "Shohona karnizlar": "Bo'yi necha sm va qancha metr kerak?\nMasalan: Bo'yi 50sm, 20 metr",
    "Yumaloq ustunlar": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 30sm, 4 dona",
    "Kapitel va baza": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 40sm, 4 dona",
    "Barelef gullar": "O'lchamlarni kiriting:\nUzunligi: ___\nBo'yi: ___\nSoni: ___",
    "Kalvak": "O'lchamlarni kiriting:\nUzunligi: ___\nEni: ___\nQalinligi: ___\nSoni: ___",
}

CHOOSING, MODEL_SELECTION, QOPLAMA, RAZMER_TANLOV, ROM_TUR, OLCHAM, LOYIHA_PHOTO, FASAD_PHOTO, CUSTOM_PHOTO = range(9)

orders = {}
savat = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("Rom bezaklari"), KeyboardButton("Ustunlar")],
        [KeyboardButton("Belbog' karnizlar"), KeyboardButton("Yumaloq ustunlar")],
        [KeyboardButton("Kapitel va baza"), KeyboardButton("Kalvak")],
        [KeyboardButton("Karnizlar"), KeyboardButton("Shohona karnizlar")],
        [KeyboardButton("Barelef gullar")],
        [KeyboardButton("📐 Loyiha bo'yicha hisoblash")],
        [KeyboardButton("🏠 Fasad loyihasi tayyorlash")],
        [KeyboardButton("🏗️ Bajarilgan loyihalar")],
        [KeyboardButton("🌟 Keng qamrovlik yechim")],
        [KeyboardButton("🛒 Savatim"), KeyboardButton("📋 Buyurtmalarim")],
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
    uid = user.id

    if text == "📋 Buyurtmalarim":
        if uid in orders and orders[uid]:
            msg = "Sizning buyurtmalaringiz:\n\n"
            for i, o in enumerate(orders[uid], 1):
                msg += str(i) + ". " + o["category"] + " — " + o.get("model", "") + "\n"
                msg += "   O'lcham: " + o.get("olcham", "") + "\n\n"
        else:
            msg = "Hozircha buyurtma yo'q."
        await update.message.reply_text(msg)
        return CHOOSING

    if text == "🛒 Savatim":
        if uid in savat and savat[uid]:
            msg = "🛒 Savatingiz:\n\n"
            for i, s in enumerate(savat[uid], 1):
                msg += str(i) + ". " + s["category"] + " — " + s.get("model", "") + "\n"
                msg += "   " + s.get("olcham", "") + "\n"
                msg += "   Qoplama: " + s.get("qoplama", "") + "\n\n"
            keyboard = [
                [InlineKeyboardButton("✅ Buyurtma berish", callback_data="buyurtma_ber")],
                [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
            ]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Savat bo'sh. Mahsulot tanlang!")
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
            "🏗️ Bajarilgan loyihalarni ko'rish:\n\n"
            "https://muzaffar57.github.io/-penodecor-katalog/loyihalar.html"
        )
        return CHOOSING

    if text == "🌟 Keng qamrovlik yechim":
        await update.message.reply_text(
            "🌟 Keng qamrovlik yechim:\n\n"
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

        await update.message.reply_text(
            text + " katalogi:\n\n"
            "Katalogni ko'rish: " + link + "\n\n"
            "Yoqtirgan modelingizni tanlang:",
            reply_markup=InlineKeyboardMarkup(model_buttons)
        )
        return MODEL_SELECTION

    await update.message.reply_text("Iltimos, menyudan tanlang.")
    return CHOOSING


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    category = context.user_data.get("category", "")

    if query.data.startswith("model_"):
        model = "MODEL-" + query.data.replace("model_", "")
        context.user_data["model"] = model

        if category == "Rom bezaklari":
            keyboard = [
                [InlineKeyboardButton("🪟 Rom bezak", callback_data="romtur_rom")],
                [InlineKeyboardButton("🚪 Eshik bezak", callback_data="romtur_eshik")],
            ]
            await query.message.reply_text(
                model + " tanlandingiz!\n\nQaysi tur kerak?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ROM_TUR

        if category in ["Karnizlar", "Belbog' karnizlar"]:
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r)] for r in KARNIZ_RAZMERLAR]
            await query.message.reply_text(
                model + " tanlandingiz!\n\nRazmer tanlang:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return RAZMER_TANLOV

        if category == "Ustunlar":
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r)] for r in USTUN_RAZMERLAR]
            await query.message.reply_text(
                model + " tanlandingiz!\n\nRazmer tanlang:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return RAZMER_TANLOV

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await query.message.reply_text(
            model + " tanlandingiz!\n\nQoplama tortilsinmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return QOPLAMA

    if query.data.startswith("romtur_"):
        tur = "Rom bezak" if query.data == "romtur_rom" else "Eshik bezak"
        context.user_data["rom_tur"] = tur
        keyboard = [
            [InlineKeyboardButton("Katta razmer", callback_data="razmer_Katta_razmer")],
            [InlineKeyboardButton("Kichik razmer", callback_data="razmer_Kichik_razmer")],
        ]
        await query.message.reply_text(
            tur + " tanlandi!\n\nRazmer tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return RAZMER_TANLOV

    if query.data.startswith("razmer_"):
        razmer = query.data.replace("razmer_", "").replace("_", " ")
        context.user_data["razmer"] = razmer

        if razmer == "25sm dan katta":
            await query.message.reply_text(
                "Katta razmer uchun bizga murojaat qiling:\n\n"
                "📞 Telefon orqali yoki admin bilan bog'laning."
            )
            return CHOOSING

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await query.message.reply_text(
            "Razmer: " + razmer + "\n\nQoplama tortilsinmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return QOPLAMA

    if query.data in ["qoplama_ha", "qoplama_yoq"]:
        context.user_data["qoplama"] = "Ha" if query.data == "qoplama_ha" else "Yo'q"
        category = context.user_data.get("category", "")
        shablon = OLCHAM_SHABLONLAR.get(category, "O'lchamlarni kiriting:")
        await query.message.reply_text("📐 " + shablon)
        return OLCHAM

    if query.data == "custom_photo":
        await query.message.reply_text("Namuna rasmingizni yuboring:")
        return CUSTOM_PHOTO

    if query.data == "buyurtma_ber":
        user = query.from_user
        if uid in savat and savat[uid]:
            msg = "🆕 YANGI BUYURTMA!\n\n"
            msg += "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
            msg += "🆔 ID: " + str(uid) + "\n\n"
            msg += "🛒 Buyurtma tarkibi:\n\n"
            for i, s in enumerate(savat[uid], 1):
                msg += str(i) + ". " + s["category"] + " — " + s.get("model", "") + "\n"
                if s.get("rom_tur"):
                    msg += "   Tur: " + s["rom_tur"] + "\n"
                if s.get("razmer"):
                    msg += "   Razmer: " + s["razmer"] + "\n"
                msg += "   Qoplama: " + s.get("qoplama", "") + "\n"
                msg += "   O'lcham: " + s.get("olcham", "") + "\n\n"

            if ADMIN_ID:
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

            if uid not in orders:
                orders[uid] = []
            orders[uid].extend(savat[uid])
            savat[uid] = []

            await query.message.reply_text(
                "✅ Buyurtmangiz qabul qilindi!\n\n"
                "Tez orada narxni hisoblab, sizga yuboramiz. Rahmat! 🙏"
            )
        return CHOOSING

    if query.data == "savat_tozala":
        savat[uid] = []
        await query.message.reply_text("🗑 Savat tozalandi!")
        return CHOOSING

    return CHOOSING


async def olcham_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    olcham = update.message.text
    category = context.user_data.get("category", "Noma'lum")
    model = context.user_data.get("model", "Noma'lum")
    qoplama = context.user_data.get("qoplama", "Yo'q")
    razmer = context.user_data.get("razmer", "")
    rom_tur = context.user_data.get("rom_tur", "")

    narx_xabar = ""
    sheet_key = None

    if category == "Rom bezaklari":
        sheet_key = "rom"
    elif category == "Ustunlar":
        sheet_key = "ustun"
    elif category == "Karnizlar":
        sheet_key = "karniz"
    elif category == "Belbog' karnizlar":
        sheet_key = "belbog"

    if sheet_key:
        narx = get_narx(sheet_key, model, razmer, rom_tur if sheet_key == "rom" else None)
        if narx:
            if qoplama == "Yo'q":
                narx = narx // 2
            narx_xabar = "\n💰 1 dona/metr narxi: " + format_narx(narx)

    item = {
        "category": category,
        "model": model,
        "rom_tur": rom_tur,
        "qoplama": qoplama,
        "razmer": razmer,
        "olcham": olcham,
    }

    if uid not in savat:
        savat[uid] = []
    savat[uid].append(item)

    keyboard = [
        [InlineKeyboardButton("🛒 Savatni ko'rish va buyurtma berish", callback_data="buyurtma_ber")],
        [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
    ]

    msg = "✅ Savatga qo'shildi!\n\n"
    msg += "📦 " + category + "\n"
    if rom_tur:
        msg += "🚪 Tur: " + rom_tur + "\n"
    msg += "🎨 Model: " + model + "\n"
    if razmer:
        msg += "📏 Razmer: " + razmer + "\n"
    msg += "🖌 Qoplama: " + qoplama + "\n"
    msg += "📐 O'lcham: " + olcham
    msg += narx_xabar

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
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
                caption="📐 LOYIHA BO'YICHA HISOBLASH!\n\n"
                "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
                "🆔 ID: " + str(user.id)
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
                caption="🏠 FASAD LOYIHASI!\n\n"
                "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
                "🆔 ID: " + str(user.id) + "\n"
                "📝 Izoh: " + caption
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
                caption="📷 Yangi namuna rasmi!\n👤 " + user.first_name + "\n🆔 " + str(user.id) + "\n📦 " + cat
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
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen),
                CallbackQueryHandler(button_handler),
            ],
            MODEL_SELECTION: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.PHOTO, custom_photo_received),
            ],
            ROM_TUR: [CallbackQueryHandler(button_handler)],
            RAZMER_TANLOV: [CallbackQueryHandler(button_handler)],
            QOPLAMA: [CallbackQueryHandler(button_handler)],
            OLCHAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, olcham_received)],
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
