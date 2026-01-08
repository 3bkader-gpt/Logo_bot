# الدالة الرئيسية
async def main(local: bool = False) -> None:
    clean_tmp_folder()
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('setsize', set_size))
    app.add_handler(CommandHandler('users', users))
    app.add_handler(CommandHandler('adduser', add_user))
    app.add_handler(CommandHandler('removeuser', remove_user))
    app.add_handler(CommandHandler('clearusers', clear_users))

    # Keyboard-style handlers
    app.add_handler(MessageHandler(filters.Regex('^/config size$'), config_size))
    app.add_handler(MessageHandler(filters.Regex('^/config opacity$'), config_opacity))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Help$'), help_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^help$'), help_command))

    app.add_handler(MessageHandler(filters.Regex('Set Logo'), set_logo))
    app.add_handler(MessageHandler(filters.Regex('Reset Logo'), reset_logo))
    app.add_handler(MessageHandler(filters.Regex('Watermark'), watermark_command))

    # Photo / document handler
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.Document.IMAGE,
            receive_photo
        )
    )

    # Remaining style handlers
    app.add_handler(MessageHandler(filters.Regex('^(صغير|متوسط|كبير)$'), handle_size_choice))
    app.add_handler(MessageHandler(filters.Regex('^(منخفضة|متوسطة|عالية|غير شفافة)$'), handle_opacity_choice))
    app.add_handler(MessageHandler(filters.Regex('^(1️⃣ ركن أسفل يمين|2️⃣ منتصف اليمين|3️⃣ ركن أعلى اليسار|4️⃣ أربع أركان)$'), style_choice))
    app.add_handler(CallbackQueryHandler(handle_save))
    app.add_handler(MessageHandler(filters.ALL, block_unlisted))

    logger.info("🚗 البوت شغال!")
    if local:
        await app.run_polling(close_loop=False, stop_signals=None)
    else:
        await app.run_polling()
