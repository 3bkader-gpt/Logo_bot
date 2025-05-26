import logging
import os
import io
import time
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from PIL import Image

# Bot token
TOKEN = '8020071366:AAG13ndNoW0uzbDoumJuBCWoYKQs3Lqs4_o'

# الإعدادات
LOGO_FILENAME = 'logo.png'
MAX_FILE_SIZE_MB = 10
STYLE_TIMEOUT_SEC = 120  # ثوانٍ
DEFAULT_OPACITY = 0.5  # الشفافية الافتراضية
DEFAULT_SIZE = 'medium'  # الحجم الافتراضي للوجو

# حالة المستخدم في الذاكرة
user_state = {}

# إعداد السجل (Logging)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # مستوى السجل العام

# معالج للشاشة (Console Handler): يعرض INFO فقط
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# معالج للملف (File Handler): يحفظ DEBUG وما فوق
file_handler = logging.FileHandler('bot.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# إضافة المعالجات إلى Logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# تقليل لوجز المكتبات الخارجية على الشاشة والملف
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# دالة لإرجاع الواجهة الرئيسية
async def return_to_main_menu(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Set Logo', 'Reset Logo'], ['Watermark', 'Help'], ['/status', '/config size', '/config opacity']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id, text="رجعنا للواجهة الرئيسية.", reply_markup=reply_markup)

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Set Logo', 'Reset Logo'], ['Watermark', 'Help'], ['/status', '/config size', '/config opacity']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "أهلاً بيك! ده بوت بيسهل عليك تضيف لوجو على صورك بسرعة وبساطة.\n"
        "- اضغط Set Logo عشان تبعت اللوجو لأول مرة أو تغيره.\n"
        "- اضغط Watermark عشان تضيف اللوجو على صورة.\n"
        "- اضغط Reset Logo لو عايز تغير اللوجو.\n"
        "- استخدم /status تعرف إذا في لوجو محفوظ ولا لأ.\n"
        "- تقدر تتحكم في حجم اللوجو بـ /config size.\n"
        "- تقدر تتحكم في شفافية اللوجو بـ /config opacity.\n"
        "لو احتجت مساعدة اضغط على Help."
    )
    await update.message.reply_text(text, reply_markup=reply_markup)

# دالة المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **دليل المساعدة:**\n\n"
        "- **Set Logo**: إرسال اللوجو لأول مرة أو تغييره.\n"
        "- **Reset Logo**: إعادة تعيين اللوجو الحالي.\n"
        "- **Watermark**: إضافة اللوجو على صورة.\n"
        "- **/status**: التحقق من حالة اللوجو.\n"
        "- **/config size**: تغيير حجم اللوجو.\n"
        "- **/config opacity**: تغيير شفافية اللوجو.\n"
        "- **Help**: عرض هذه المساعدة.\n\n"
        "للمزيد من المساعدة، راجع الدليل أو تواصل مع الدعم."
    )

# دالة حالة اللوجو
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(LOGO_FILENAME):
        await update.message.reply_text(f"اللوجو محفوظ هنا: {os.path.abspath(LOGO_FILENAME)}")
    else:
        await update.message.reply_text("مافيش لوجو محفوظ دلوقتي. استخدم Set Logo.")

# دالة ضبط حجم اللوجو
async def config_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sizes = [['صغير', 'متوسط'], ['كبير']]
    reply_markup = ReplyKeyboardMarkup(sizes, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("اختار حجم اللوجو:", reply_markup=reply_markup)
    context.chat_data['configuring_size'] = True

# دالة ضبط شفافية اللوجو
async def config_opacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opacities = [['منخفضة', 'متوسطة'], ['عالية', 'غير شفافة']]
    reply_markup = ReplyKeyboardMarkup(opacities, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("اختار شفافية اللوجو:", reply_markup=reply_markup)
    context.chat_data['configuring_opacity'] = True

# دالة معاينة وحفظ الحجم
async def handle_size_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'configuring_size' not in context.chat_data:
        return
    
    size_choice = update.message.text
    size_map = {'صغير': 0.1, 'متوسط': 0.2, 'كبير': 0.3}
    if size_choice not in size_map:
        await update.message.reply_text("اختيار غير صالح. اختار صغير، متوسط، أو كبير.")
        return
    
    context.chat_data.pop('configuring_size')
    
    if not os.path.exists(LOGO_FILENAME):
        await update.message.reply_text("مافيش لوجو محفوظ. استخدم Set Logo الأول.")
        return
    
    try:
        logo = Image.open(LOGO_FILENAME).convert("RGBA")
        sample_image = Image.new('RGBA', (500, 500), (255, 255, 255, 255))
        bw, bh = sample_image.size
        lw = int(bw * size_map[size_choice])
        lh = int(lw * logo.height / logo.width)
        logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        
        position = (bw - lw - 10, bh - lh - 10)
        layer = Image.new('RGBA', sample_image.size, (0, 0, 0, 0))
        layer.paste(logo_resized, position, logo_resized.split()[3])
        result = Image.alpha_composite(sample_image, layer)
        
        out_buffer = io.BytesIO()
        result.convert('RGB').save(out_buffer, format='JPEG', quality=95)
        out_buffer.seek(0)
        
        keyboard = [
            [InlineKeyboardButton("حفظ", callback_data=f"save_size_{size_choice}"),
             InlineKeyboardButton("إلغاء", callback_data="cancel_size")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(photo=out_buffer.getvalue(), caption="دي معاينة اللوجو بالحجم الجديد. اختار حفظ أو إلغاء:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء معاينة الحجم: {e}")
        await update.message.reply_text("حصل خطأ أثناء معاينة الحجم. جرب تاني.")
        await return_to_main_menu(update.message.chat_id, context)

# دالة معاينة وحفظ الشفافية
async def handle_opacity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'configuring_opacity' not in context.chat_data:
        return
    
    opacity_choice = update.message.text
    opacity_map = {'منخفضة': 0.3, 'متوسطة': 0.5, 'عالية': 0.8, 'غير شفافة': 1.0}
    if opacity_choice not in opacity_map:
        await update.message.reply_text("اختيار غير صالح. اختار منخفضة، متوسطة، عالية، أو غير شفافة.")
        return
    
    context.chat_data.pop('configuring_opacity')
    
    if not os.path.exists(LOGO_FILENAME):
        await update.message.reply_text("مافيش لوجو محفوظ. استخدم Set Logo الأول.")
        return
    
    try:
        logo = Image.open(LOGO_FILENAME).convert("RGBA")
        sample_image = Image.new('RGBA', (500, 500), (255, 255, 255, 255))
        bw, bh = sample_image.size
        lw = int(bw * 0.2)
        lh = int(lw * logo.height / logo.width)
        logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        
        mask = logo_resized.split()[3].point(lambda i: i * opacity_map[opacity_choice])
        layer = Image.new('RGBA', sample_image.size, (0, 0, 0, 0))
        position = (bw - lw - 10, bh - lh - 10)
        layer.paste(logo_resized, position, mask)
        result = Image.alpha_composite(sample_image, layer)
        
        out_buffer = io.BytesIO()
        result.convert('RGB').save(out_buffer, format='JPEG', quality=95)
        out_buffer.seek(0)
        
        keyboard = [
            [InlineKeyboardButton("حفظ", callback_data=f"save_opacity_{opacity_choice}"),
             InlineKeyboardButton("إلغاء", callback_data="cancel_opacity")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(photo=out_buffer.getvalue(), caption="دي معاينة اللوجو بالشفافية الجديدة. اختار حفظ أو إلغاء:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء معاينة الشفافية: {e}")
        await update.message.reply_text("حصل خطأ أثناء معاينة الشفافية. جرب تاني.")
        await return_to_main_menu(update.message.chat_id, context)

# دالة التعامل مع أزرار الحفظ أو الإلغاء
async def handle_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    try:
        if data.startswith("save_size_"):
            size_choice = data.split("_")[2]
            size_map = {'صغير': 0.1, 'متوسط': 0.2, 'كبير': 0.3}
            logo = Image.open(LOGO_FILENAME).convert("RGBA")
            lw = int(logo.width * size_map[size_choice])
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            logo_resized.save(LOGO_FILENAME, "PNG")
            await query.edit_message_caption(caption="✅ تم حفظ اللوجو بالحجم الجديد!")
        elif data.startswith("save_opacity_"):
            opacity_choice = data.split("_")[2]
            opacity_map = {'منخفضة': 0.3, 'متوسطة': 0.5, 'عالية': 0.8, 'غير شفافة': 1.0}
            context.chat_data['opacity'] = opacity_map[opacity_choice]
            await query.edit_message_caption(caption="✅ تم حفظ الشفافية الجديدة!")
        elif data in ["cancel_size", "cancel_opacity"]:
            await query.edit_message_caption(caption="تم الإلغاء. الإعدادات لسه زي ما كانت.")
        
        await return_to_main_menu(query.message.chat_id, context)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء حفظ الإعدادات: {e}")
        await query.edit_message_caption(caption="حصل خطأ أثناء الحفظ. جرب تاني.")
        await return_to_main_menu(query.message.chat_id, context)

# دالة تعيين اللوجو
async def set_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعتلي اللوجو دلوقتي:", reply_markup=ReplyKeyboardRemove())
    context.chat_data['setting_logo'] = True

# دالة إعادة تعيين اللوجو
async def reset_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعت اللوجو الجديد:", reply_markup=ReplyKeyboardRemove())
    context.chat_data['setting_logo'] = True

# دالة طلب إرسال الصورة لإضافة اللوجو
async def watermark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعتلي الصورة اللي عايز تضيف عليها اللوجو:", reply_markup=ReplyKeyboardRemove())
    context.chat_data['waiting_for_photo'] = True

# دالة استقبال الصورة
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # التعامل مع إعداد اللوجو
    if 'setting_logo' in context.chat_data:
        if not message.photo:
            await message.reply_text("مفيش صورة في الرسالة. ابعت صورة تاني.")
            return
        try:
            photo = message.photo[-1]
            file = await photo.get_file()
            buffer = io.BytesIO()
            await file.download_to_memory(out=buffer)
            buffer.seek(0)
            logger.info("جاري التحقق من صورة اللوجو...")
            Image.open(buffer).verify()
            buffer.seek(0)
            with open(LOGO_FILENAME, 'wb') as f:
                f.write(buffer.read())
            context.chat_data.pop('setting_logo')
            await message.reply_text("✅ تم حفظ اللوجو بنجاح!")
            await return_to_main_menu(message.chat_id, context)
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ اللوجو: {str(e)}")
            await message.reply_text(f"حصل خطأ أثناء حفظ اللوجو: {str(e)}. جرب صورة تانية.")
            context.chat_data.pop('setting_logo')
            await return_to_main_menu(message.chat_id, context)
        return

    # التحقق من أن البوت ينتظر صورة
    if 'waiting_for_photo' not in context.chat_data:
        logger.debug(f"رسالة صورة وصلت، لكن البوت مش منتظر صور (chat_id: {message.chat_id}).")
        return

    if not message.photo:
        await message.reply_text("مفيش صورة في الرسالة. ابعت صورة.")
        await return_to_main_menu(message.chat_id, context)
        return

    context.chat_data.pop('waiting_for_photo')

    if not os.path.exists(LOGO_FILENAME):
        await message.reply_text("مافيش لوجو محفوظ. استخدم Set Logo الأول.")
        await return_to_main_menu(message.chat_id, context)
        return
    
    photo = message.photo[-1]
    if photo.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        logger.error(f"❌ صورة بحجم كبير جدًا: file_id={photo.file_id}, size={photo.file_size}")
        await message.reply_text(f"حجم الصورة كبير. خفّضه لأقل من {MAX_FILE_SIZE_MB} MB.")
        await return_to_main_menu(message.chat_id, context)
        return
    
    try:
        logger.info(f"تم استقبال صورة للمعالجة: file_id={photo.file_id}")
        user_state[update.effective_chat.id] = {'time': time.time(), 'photo_file_id': photo.file_id}
        styles = [['1️⃣ ركن أسفل يمين', '2️⃣ منتصف اليمين'], ['3️⃣ ركن أعلى اليسار', '4️⃣ أربع أركان']]
        await update.message.reply_text("✨ اختر نمط اللوجو:", reply_markup=ReplyKeyboardMarkup(styles, one_time_keyboard=True, resize_keyboard=True))
    except Exception as e:
        logger.error(f"❌ خطأ أثناء استقبال الصورة: {str(e)}")
        await message.reply_text(f"حدث خطأ أثناء استقبال الصورة: {str(e)}. جرب تاني.")
        await return_to_main_menu(message.chat_id, context)

# دالة اختيار النمط
async def style_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if chat_id not in user_state:
        logger.warning(f"لا توجد حالة مخزنة لـ chat_id {chat_id} في user_state.")
        await update.message.reply_text("مفيش صورة في انتظار المعالجة. ابعت صورة جديدة.")
        await return_to_main_menu(chat_id, context)
        return
    
    entry = user_state.get(chat_id)
    if time.time() - entry['time'] > STYLE_TIMEOUT_SEC:
        user_state.pop(chat_id)
        logger.info(f"انتهى وقت الاختيار لـ chat_id {chat_id}.")
        await update.message.reply_text("انتهى وقت الاختيار. ابعت صورة جديدة.")
        await return_to_main_menu(chat_id, context)
        return
    
    choice = update.message.text.strip()
    if choice not in ['1️⃣ ركن أسفل يمين', '2️⃣ منتصف اليمين', '3️⃣ ركن أعلى اليسار', '4️⃣ أربع أركان']:
        logger.warning(f"اختيار نمط غير صحيح: {choice} (chat_id: {chat_id})")
        await update.message.reply_text("اختيار غير صالح. اختار من الخيارات المتاحة.")
        return
    
    choice_map = {
        '1️⃣ ركن أسفل يمين': '1',
        '2️⃣ منتصف اليمين': '2',
        '3️⃣ ركن أعلى اليسار': '3',
        '4️⃣ أربع أركان': '4'
    }
    choice = choice_map[choice]
    
    file_id = entry['photo_file_id']
    
    try:
        logger.info("جاري تحميل اللوجو...")
        logo = Image.open(LOGO_FILENAME).convert("RGBA")
        Image.open(LOGO_FILENAME).verify()
        opacity = context.chat_data.get('opacity', DEFAULT_OPACITY)
        logger.info("تم تحميل اللوجو بنجاح.")

        logger.info(f"جاري معالجة الصورة {file_id}...")
        buffer = io.BytesIO()
        file = await context.bot.get_file(file_id)
        await file.download_to_memory(out=buffer)
        buffer.seek(0)
        
        logger.debug(f"التحقق من الصورة {file_id}...")
        Image.open(buffer).verify()
        buffer.seek(0)
        base = Image.open(buffer).convert("RGBA")
        logger.info(f"تم تحميل الصورة {file_id} بنجاح.")

        bw, bh = base.size
        logger.debug(f"حجم الصورة الأساسية: {bw}x{bh}")
        if choice == '1':
            lw = int(bw * 0.2)
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            position = (bw - lw - 10, bh - lh - 10)
        elif choice == '2':
            lw = int(bw * 0.2)
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            position = (bw - lw - 10, (bh - lh) // 2)
        elif choice == '3':
            lw = int(bw * 0.2)
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            position = (10, 10)
        else:  # choice == '4'
            lw = int(bw * 0.1)
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            positions = [(10, 10), (bw - lw - 10, 10), (10, bh - lh - 10), (bw - lw - 10, bh - lh - 10)]
        
        logger.debug(f"تطبيق الشفافية: {opacity}")
        mask = logo_resized.split()[3].point(lambda i: i * opacity)
        layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
        if choice != '4':
            layer.paste(logo_resized, position, mask)
        else:
            for pos in positions:
                layer.paste(logo_resized, pos, mask)
        result = Image.alpha_composite(base, layer)
        out_buffer = io.BytesIO()
        result.convert('RGB').save(out_buffer, format='JPEG', quality=95)
        out_buffer.seek(0)
        await context.bot.send_photo(chat_id=chat_id, photo=out_buffer, caption="✅ تم إضافة اللوجو!")
        logger.info(f"تم إرسال الصورة {file_id} المعالجة.")
        
        user_state.pop(chat_id)
        await context.bot.send_message(chat_id=chat_id, text="✅ تم معالجة الصورة بنجاح!")
        await return_to_main_menu(chat_id, context)
    
    except Exception as e:
        logger.error(f"❌ خطأ أثناء معالجة الصورة {file_id}: {str(e)}")
        await update.message.reply_text(f"حدث خطأ: {str(e)}. جرب صورة أخرى.")
        user_state.pop(chat_id, None)
        await return_to_main_menu(chat_id, context)

# دالة تنظيف المهام المنتهية
async def timeout_cleanup(context: ContextTypes.DEFAULT_TYPE):
    try:
        now = time.time()
        to_remove = [uid for uid, st in user_state.items() if now - st['time'] > STYLE_TIMEOUT_SEC]
        for uid in to_remove:
            user_state.pop(uid)
        logger.debug(f"تم تصفية {len(to_remove)} حالة منتهية.")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تنظيف user_state: {str(e)}")

# الدالة الرئيسية
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(MessageHandler(filters.Regex('^/config size$'), config_size))
    app.add_handler(MessageHandler(filters.Regex('^/config opacity$'), config_opacity))
    app.add_handler(MessageHandler(filters.Regex('^Help$'), help_command))
    app.add_handler(MessageHandler(filters.Regex('^Set Logo$'), set_logo))
    app.add_handler(MessageHandler(filters.Regex('^Reset Logo$'), reset_logo))
    app.add_handler(MessageHandler(filters.Regex('^Watermark$'), watermark_command))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.add_handler(MessageHandler(filters.Regex('^(صغير|متوسط|كبير)$'), handle_size_choice))
    app.add_handler(MessageHandler(filters.Regex('^(منخفضة|متوسطة|عالية|غير شفافة)$'), handle_opacity_choice))
    app.add_handler(MessageHandler(filters.Regex('^(1️⃣ ركن أسفل يمين|2️⃣ منتصف اليمين|3️⃣ ركن أعلى اليسار|4️⃣ أربع أركان)$'), style_choice))
    app.add_handler(CallbackQueryHandler(handle_save))
    
    app.job_queue.run_repeating(timeout_cleanup, interval=60, first=1)
    
    logger.info("🚀 البوت شغال!")
    app.run_polling()

if __name__ == '__main__':
    main()