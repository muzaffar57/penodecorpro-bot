if ADMIN_ID:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption=f"📸 Yangi namuna rasmi!\n👤 {user.first_name} ({user.id})"
            )
        return RAZMER
    else:
        await update.message.reply_text("Iltimos, rasm yuboring.")
        return CUSTOM_PHOTO

async def razmer_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    razmer = update.message.text
    category = context.user_data.get("category", "Noma'lum")
    variant = context.user_data.get("variant", "Noma'lum")

    if user.id not in orders:
        orders[user.id] = []
    orders[user.id].append({
        "category": category,
        "variant": variant,
        "razmer": razmer
    })

    await update.message.reply_text(
        f"✅ Buyurtmangiz qabul qilindi!\n\n"
        f"📦 Tur: {category}\n"
        f"🎨 Variant: {variant}\n"
        f"📐 O'lcham: {razmer}\n\n"
        "Tez orada narxni hisoblab, sizga yuboramiz. Rahmat! 🙏"
    )

    if ADMIN_ID:
        msg = (
            f"🆕 *Yangi buyurtma!*\n\n"
            f"👤 Mijoz: {user.first_name} {user.last_name or ''}\n"
            f"🆔 ID: {user.id}\n"
            f"📦 Tur: {category}\n"
            f"🎨 Variant: {variant}\n"
            f"📐 O'lcham: {razmer}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")

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
            text=f"💰 *Sizning buyurtmangiz narxi:*\n\n{price_text}\n\nBuyurtmani tasdiqlash uchun adminga yozing.",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Narx mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen)],
            VIEWING: [CallbackQueryHandler(button_handler)],
            RAZMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, razmer_received)],
            CUSTOM_PHOTO: [MessageHandler(filters.PHOTO, custom_photo_received)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", send_price))
    app.run_polling()

if name == "main":
    main()
