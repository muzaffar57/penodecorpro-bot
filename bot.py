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
        await update.get_bot().send_message(chat_id=ADMIN_ID, text=msg)

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
        await update.get_bot().send_message(
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


if name == "main":
    main()
