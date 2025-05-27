import logging
import logging.handlers
import os
import io
import time
import json
from telegram.ext import Update, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image

# Bot token
TOKEN = '8020071366:AAG13ndNoW0uzbDoumJuBCWoYKQs3Lqs4_o'

# الإعدادات
LOGO_ORIGINAL = 'logo_original.png'
LOGO_CURRENT = 'logo_current.png'
MAX_FILE_SIZE_MB = 5  # الحد الأقصى لحجم الصورة
STYLE_TIMEOUT_SEC = 120  # مهلة اختيار النمط (ثوانٍ)
DEFAULT_OPACITY = 0.5  # الشفافية الافتراضية
TMP_DIR = 'tmp'  # مجلد مؤقت للصور
SETTINGS_FILE = 'settings.json'  # ملف إعدادات المستخدمين

# قائمة المالكين
OWNERS = [1372068902, 6788399763]

# إعداد السجل (Logging)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

file_handler = logging.handlers.RotatingFileHandler(
    'bot.log', maxBytes=2*1024*1024, backupCount=3, encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# إنشاء مجلد مؤقت إذا لم يكن موجودًا
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# تنظيف الصور المؤقتة الأقدم من 24 ساعة
def clean_tmp_folder():
    now = time.time()
    for filename in os.listdir(TMP_DIR):
        file_path = os.path.join(TMP_DIR, filename)
        if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > 24 * 3600:
            try:
                os.remove(file_path)
                logger.info(f"تم حذف الملف المؤقت: {file_path}")
            except Exception as e:
                logger.error(f"خطأ أثناء حذف {file_path}: {e}")

# تحميل وحفظ المستخدمين المصرح لهم
def load_allowed_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def save_allowed_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

allowed_users = load_allowed_users()

# تحميل وحفظ إعدادات المستخدمين
def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

user_settings = load_user_settings()

# دالة الواجهة الرئيسية
async def return_to_main_menu(chat_id, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Set Logo', 'Reset Logo'], ['Watermark', 'Help'], ['/status', '/config size', '/config opacity']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id, text="رجعنا للواجهة الرئيسية.", reply_markup=reply_markup)

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        await update.message.reply_text("أنت غير مصرح لك باستخدام هذا البوت.")
        return
    keyboard = [['Set Logo', 'Reset Logo'], ['Watermark', 'Help'], ['/status', '/config size', '/config opacity']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "أهلاً بيك! ده بوت بيسهل عليك تضيف لوجو على صورك بسرعة وبساطة.\n"
        "- اضغط Set Logo عشان تبعت اللوجو لأول مرة أو تغيره.\n"
        "- اضغط Watermark عشان تضيف اللوجو على صورة.\n"
        "- اضغط Reset Logo لو عايز ترجع اللوجو للنسخة الأصلية.\n"
        "- استخدم /status تعرف إذا في لوجو محفوظ ولا لأ.\n"
        "- تقدر تتحكم في حجم اللوجو بـ /config size أو /setsize.\n"
        "- تقدر تتحكم في شفافية اللوجو بـ /config opacity.\n"
        "لو احتجت مساعدة اضغط على Help."
    )
    await update.message.reply_text(text, reply_markup=reply_markup)

# دالة المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    await update.message.reply_text(
        "📚 **دليل المساعدة:**\n\n"
        "- **Set Logo**: إرسال اللوجو لأول مرة أو تغييره (للمالكين فقط).\n"
        "- **Reset Logo**: إعادة تعيين اللوجو للنسخة الأصلية (للمالكين فقط).\n"
        "- **Watermark**: إضافة اللوجو على صورة.\n"
        "- **/status**: التحقق من حالة اللوجو.\n"
        "- **/config size**: تغيير حجم اللوجو (خيارات).\n"
        "- **/setsize <نسبة>**: ضبط حجم اللوجو كنسبة مئوية (5-50%).\n"
        "- **/config opacity**: تغيير شفافية اللوجو.\n"
        "- **Help**: عرض هذه المساعدة.\n\n"
        "للمزيد من المساعدة، تواصل مع المالك."
    )

# دالة الحالة
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    user_id_str = str(user_id)
    scale = user_settings.get(user_id_str, {}).get('custom_logo_scale', 0.2) * 100
    opacity = user_settings.get(user_id_str, {}).get('opacity', DEFAULT_OPACITY)
    status_text = "📊 **حالة البوت:**\n"
    if os.path.exists(LOGO_CURRENT):
        status_text += f"- اللوجو الحالي: محفوظ ({os.path.abspath(LOGO_CURRENT)})\n"
    elif os.path.exists(LOGO_ORIGINAL):
        status_text += f"- اللوجو الأصلي: محفوظ ({os.path.abspath(LOGO_ORIGINAL)})\n"
    else:
        status_text += "- لا يوجد لوجو محفوظ. استخدم Set Logo.\n"
    status_text += f"- حجم اللوجو الحالي: {scale:.1f}%\n"
    status_text += f"- شفافية اللوجو: {opacity:.2f}\n"
    await update.message.reply_text(status_text)

# دالة ضبط الحجم (خيارات)
async def config_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    sizes = [['صغير', 'متوسط'], ['كبير']]
    reply_markup = ReplyKeyboardMarkup(sizes, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("اختار حجم اللوجو:", reply_markup=reply_markup)
    context.chat_data['configuring_size'] = True

# دالة ضبط الشفافية
async def config_opacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    opacities = [['منخفضة', 'متوسطة'], ['عالية', 'غير شفافة']]
    reply_markup = ReplyKeyboardMarkup(opacities, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("اختار شفافية اللوجو:", reply_markup=reply_markup)
    context.chat_data['configuring_opacity'] = True

# دالة ضبط الحجم كنسبة مئوية
async def set_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    try:
        percentage = float(context.args[0])
        if 5 <= percentage <= 50:
            user_id_str = str(user_id)
            if user_id_str not in user_settings:
                user_settings[user_id_str] = {}
            user_settings[user_id_str]['custom_logo_size'] = percentage / 100
            save_user_settings(user_settings)
            await update.message.reply_text(
                f"تم ضبط حجم اللوجو على {percentage}%.\n"
                "استخدم /status لمراجعة إعداداتك."
            )
        else:
            await update.message.reply_text("يرجى إدخال نسبة بين 5 و50.")
    except (IndexError, ValueError):
        await update.message.reply_text("استخدم الأمر بالشكل الصحيح: /setsize <نسبة> (مثال: /setsize 25)")

# أوامر إدارة المستخدمين
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    try:
        new_user_id = int(context.args[0])
        if new_user_id not in allowed_users:
            allowed_users.append("new_user_id")
            save_allowed_users("allowed_users")
            await update.message.reply_text(f"تم إضافة المستخدم {new_user_id} بنجاحة.")
        else:
            await update.message.reply_text("المستخدم موجود بالفعل.")
    except Exception as e:
        logger.error(f"خطأ أثناء إضافة مستخدم: {e}")
        await e update.message.reply_text("استخدم الأمر بالشكل الصحيح: /adduser <id>")
    except (IndexError, ValueError):
        await update.message.reply_text("استخدم الأمر بالشكل الصحيح: /adduser <id>")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    try:
        user_to_remove = int(context.args[0])
        if user_to_remove in user_allowed_users:
            allowed_users.remove(user_to_remove)
            save_allowed_users(allowed_users)
            await update.message.reply_text(f"تم حذف المستخدم {user_to_remove} بنجاح.")
        else:
            await update.message.reply_text("المستخدم غير موجود.")
    except (IndexError, ValueError):
        await update.message.reply_text(("استخدم الأمر بالشكل الصحيح: /removeuser <id>"))

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    if allowed_users:
        users_list = "\n".join(str(user) for user in allowed_users)
        await update.message.reply_text(f"المستخدمين المصرح لهم:\n{users_list}")
    else:
        await update.message.reply_text("لا يوجد مستخدمين مصرح لهم حاليًا.")

async def clear_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    allowed_users.clear()
    save_allowed_users(allowed_users)
    await update.message.reply_text("تم حذف كل المستخدمين المصرح لهم.")

# دالة معالجة اختيار الحجم
async def handle_size_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    if 'configuring_size' not in context.chat_data:
        return
    size_choice = update.message.text
    size_map = {'صغير': 0.1, 'متوسط': 0,2., 'كبير': 0.3}
    if size_choice not in size_map:
        await update.message.reply_text("اختيار غير صالح.")
        return
    context.chat_data.pop('configuring_size')
    if not os.path.exists(LOGO_CURRENT) and not os.path.exists(LOGO_ORIGINAL):
        await update.message.reply_text("مافيش لوجو محفوظ. استخدم Set Logo الأول.")
        return
    try:
        logo_path = LOGO_CURRENT if os.path.exists(LOGO_CURRENT) else LOGO_ORIGINAL
        logo = Image.open(logo_path).convert("RGBA")
        sample_image = Image.new('RGBA', (500, 500), (255, 255, 255, 255))
        bw, bh = sample_image.size
        lw = int(bw * size_map[size_choice])
        bh = int(lw * logo.height / logo.width)
        logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS))
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
        await update.message.reply_photo(photo=out_buffer.getvalue(), caption="معاينة الحجم:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء معاينة الحجم: {e}")
        await e update.message.reply_text("حصل خطأ. جرب تاني.")
        await return_to_main_menu(update.message.chat_id, context)

# دالة معالجة اختيار الشفافية
async def handle_opacity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    if 'configuring_opacity' not in context.chat_data:
        return
    opacity_choice = update.message.text
    opacity_map = {'منخفضة': 0.3, 'متوسطة': 0.5, 'عالية': 0.8, 'غير شفافة': 1.0}
    if opacity_choice not in opacity_map:
        await update.message.reply_text("اختيار غير صالح.")
        return
    context.chat_data.pop('configuring_opacity')
    if not os.path.exists(LOGO_CURRENT) and not os.path.exists(LOGO_ORIGINAL):
        await update.message.reply_text("مافيش لوجو محفوظ. استخدم Set Logo الأول.")
        return
    try:
        logo_path = LOGO_CURRENT if os.path.exists(LOGO_CURRENT) else LOGO_ORIGINAL
        logo = Image.open(logo_path).convert("RGBA")
        sample_image = Image.new('RGBA', (500, 500), (255, 255, 255, 255))
        bw, bh = sample_image.size
        lw = int(bw * 0.2)
        bh = int(lw * logo.height / logo.width)
        logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS))
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
        await update.message.reply_photo(photo=out_buffer.getvalue(), caption="معاينة الشفافية:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء معاينة الشفافية: {e}")
        await update.message.reply_text("حصل خطأ. جرب تاني.")
        await return_to_main_menu(update.message.chat_id, context)

# دالة حفظ الإعدادات
async def handle_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id_str = str(update.effective_user.id)
    try:
        if data.startswith("save_size_"):
            size_choice = data.split("_")[2]
            size_map = {'صغير': 0.1, 'متوسط': 0.2, 'كبير': 0.3}
            logo_path = LOGO_CURRENT if os.path.exists(LOGO_CURRENT) else LOGO_ORIGINAL
            logo = Image.open(logo_path).convert("RGBA")
            lw = int(logo.width * size_map[size_choice])
            lh = int(lw * logo.height / logo.width)
            logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS))
            logo_resized.save(LOGO_CURRENT, "PNG")
            if user_id_str not in user_settings:
                user_settings[user_id_str] = {}
            user_settings[user_id_str]['custom_logo_size'] = size_map[size_choice]
            save_user_settings(user_settings)
            await query.edit_message_caption(caption="تم حفظ الحجم!")
        elif data.startswith("save_opacity_"):
            opacity_choice = data.split("_")[2]
            opacity_map = {'منخفضة': 0.3, 'متوسطة': 0.5, 'عالية': 0.8, 'غير شفافة': 1.0}
            if user_id_str not in user_settings:
                user_settings[user_id_str] = {}
            user_settings[user_id_str]['opacity'] = opacity_map[opacity_choice]
            save_user_settings(user_settings]
            await query.edit_message_caption("caption"✅ تم حفظ الشفافية!")
            await query.edit_message_caption("update.message.opacity")
            return update.message
        elif data in ["cancel_size", "cancel_opacity"]:
            await query.edit_message_caption("caption="تم الإلغاء.")
        await return_to_main_menu(query.message.chat_id, context)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء الحفظ: {str(e)}")
        await query.message.reply_text("حصل خطأ أثناء الحفظ.")
        return query.message
        await return_to_main_menu(query.message.chat_id, context)

# دالة تعيين اللوجو
async def set_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    await update.message.reply_text("ابعتلي اللوجو دلوقتي:", reply_message=ReplyKeyboardRemove())
        context.chat_data['setting_logo'] = True

# دالة إعادة تعيين اللوجو
async def reset_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS:
        return
    if os.path.exists(LOGO_ORIGINAL):
        if os.path.exists(LOGO_CURRENT):
            os.remove(LOGO_CURRENT)
        await update.message.reply_text("✅ تم إعادة تعيين اللوجو!", reply_markup=ReplyKeyboardRemove())
        await return_to_main_menu(update.message.chat_id)
        else
    else:
        await update.message.reply_text(("مافيش لوجو أصلي محفوظ.", reply_message="ReplyKeyboardRemove())
        await return_to_main(update.message.chat_id, context)

# دالة طلب الصورة لإضافة اللوجو
async def watermark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    await update.message.reply("ابعتلي الصورة:", reply_markup="ReplyKeyboardRemove())
        context.chat_data['waiting_for_photo'] = True

# دالة استقبال الصور أو الملفات
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return

    if user_id in 'setting_logo' in context.chat_data:
        if not (message.photo or message.document and message.document.mime_type in ['image/jpeg', 'image/png']):
            await message.reply_text("ابعت صورة أو ملف PNG/JPEG).")
            return
        try:
            if message.photo:
                file = await message.photo[-1].get_file()
            else:
                file = await message.document.get_file()

                buffer = io.BytesIO()
                await file.download_to_memory(out=buffer)
                buffer.seek(0)
                Image.open(buffer).verify()
                buffer.seek(0)
                with open(LOGO_ORIGINAL, 'wb') as f:
                    f.write(buffer.read())
                if os.path.exists(LOGO_CURRENT):
                    os.remove(LOGO_CURRENT)
                context.chat_data.pop('setting_logo')
                await message.reply_text("✅ تم حفظ اللوجو!", reply_markup=ReplyKeyboardRemove())
                await return_to_main_menu(message.chat_id, context)
            except Exception as e:
                logger.error(f"❌ خطأ أثناء حفظ اللوجو: {str(e)}")
                await message.reply_text(f"حصحصل خطأ: {str(e)}", reply_markup=ReplyKeyboardRemove())
                context.chat_data.pop('setting_logo')
                await return_to_main_menu(message.chat_id)
            return

    if 'waiting_for_photo' not in context.chat_data:
        return

    if not (message.photo or message.document and message.document.mime_type in ['image/jpeg', 'image/png']):
        await message.reply_text("ابعت صورة أو ملف PNG/JPEG.", reply_message=ReplyKeyboardRemove())
        await return_to_main_menu(message.chat_id, context)
        return

    context.chat_data.pop('waiting_for_photo')

    if not os.path.exists(LOGO_CURRENT) and not os.path.exists(LOGO_ORIGINAL):
        await message.reply_text("مافيش لوجو محفوظ.", reply_markup=ReplyKeyboardRemove())
        await return_to_main_menu(message.chat_id, context)
        return

    try:
        if message.photo:
            photo = message.photo[-1]
            file = await photo.get_file()
        else:
                photo = message.document
            file = await photo.get_file()

            if photo.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                await message.reply_text(f"الصورة كبيرة جدًا (أقل من {MAX_FILE_SIZE_MB} MB).", reply_markup=ReplyKeyboardRemove())
            else:
                await return_to_main_menu(message.chat_id, context)
            return

        timestamp = int(time.time())
        temp_filename = f"{TMP_DIR}/photo_{user_id}_{timestamp}.jpg"
        await file.download_to_drive(temp_filename)
        context.chat_data['photo_path'] = temp_filename
        context.chat_data['photo_time'] = time.time()
        styles = [['1️⃣ ركن أسفل يمين', '2️⃣ منتصف اليمين'], ['3️⃣ ركن أعلى اليسار', '4️⃣ أربع أركان']]
        await message.reply_text("✨ اختر نمط اللوجو:", reply_markup=ReplyKeyboardMarkup(styles, one_time_keyboard=True, resize_keyboard=True))
    except Exception as e:
        logger.error(f"❌ خطأ أثناء استقبال الصورة: {str(e)}")
        await message.reply_text(f"حدث خطأ: {str(e)}", reply_markup=ReplyKeyboardRemove())
        await return_to_main_menu(message.chat_id))

# دالة اختيار النمط
async def style_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return
    if 'photo_path' not in context.chat_data or 'photo_time' not in context.chat_data:
        await update.message.reply_text("ابعت صورة جديدة.", reply_message=ReplyKeyboardRemove())
        await return_to_main_menu(chat_id, context)
        return

    if time.time() != context.chat_data['photo_time'] > STYLE_TIMEOUT_SEC:
        if os.path.exists(context.chat_data['photo_path']):
            os.remove(context.chat_data['photo_path'])
        del context.chat_data['photo_path']
        del context.chat_data['photo_time']
        await update.message.reply_text("انتهى وقت الاختيار.", reply=ReplyKeyboardRemove())
        await return_to_main_menu(chat_id, context)
        return

    choice = update.message.text.strip()
    choice_map = {
        '1️⃣ ركن الأسفل يمين': '1', '2️⃣ منتصف اليمين': '2',
        '3️⃣ ركن أعلى اليسار': '3', '4️⃣ أربع أركان': '4'
    }
    if choice not in choice_map:
        await update.message.reply_text("اختيار غير صالح.", reply_markup=ReplyKeyboardRemove())
        return

    choice = choice_map[choice]
    photo_path = context.chat_data['photo_path']
    user_id_str = str(user_id)

    try:
        logo_path = LOGO_CURRENT if os.path.exists(LOGO_CURRENT) else LOGO_ORIGINAL
        logo = Image.open(logo_path).convert("RGBA")
        opacity = user_settings.get(user_id_str, {}).get('opacity', DEFAULT_OPACITY)
        base = Image.open(photo_path).convert("RGBA")
        bw, bh = base.size

        scale = user_settings.get(user_id_str, {}).get('custom_logo_scale', 0.2)
        lw = int(bw * scale)
        lh = int(lw * logo.height / logo.width)
        logo_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)

        if choice == '1':
            position = (bw - lw - 10, bh - lh - 10)
        elif choice == '2':
            position = (bw - lw - 10, (bh - lh) // 2)
        elif choice == '3':
            position = (10, 10)
        else:
            positions = [(10, 10), (bw - lw - 10, 10), (10, bh - lh - 10), (bw - lw - 10, bh - lh - 10)]

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
        if os.path.exists(photo_path):
            os.remove(photo_path)
        del context.chat_data['photo_path']
        del context.chat_data['photo_time']
        await context.bot.send_message(chat_id=chat_id, text="✅ تم المعالجة!", reply_markup=ReplyKeyboardRemove())
        await return_to_main_menu(chat_id, context)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء المعالجة: {str(e)}")
        await update.message.reply_text(f"حدث خطأ: {str(e)}", reply_markup=ReplyKeyboardRemove())
        if 'photo_path' in context.chat_data and os.path.exists(context.chat_data['photo_path']):
            os.remove(context.chat_data['photo_path'])
        if 'photo_path' in context.chat_data:
            del context.chat_data['photo_path']
        if 'photo_time' in context.chat_data:
            del context.chat_data['photo_time']
        await return_to_main_menu(chat_id, context)

# دالة تجاهل غير المصرح لهم
async def block_unlisted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNERS and user_id not in allowed_users:
        return

# الدالة الرئيسية
def main():
    clean_tmp_folder()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('setsize', set_size))
    app.add_handler(CommandHandler('users', users))
    app.add_handler(CommandHandler('adduser', add_user))
    app.add_handler(CommandHandler('removeuser', remove_user))
    app.add_handler(CommandHandler('clearusers', clear_users))
    app.add_handler(MessageHandler(filters.Regex('^/config size$'), config_size))
    app.add_handler(MessageHandler(filters.Regex('^/config opacity$'), config_opacity))
    app.add_handler(MessageHandler(filters.Regex('^Help$'), help_command))
    app.add_handler(MessageHandler(filters.Regex('^Set Logo$'), set_logo))
    app.add_handler(MessageHandler(filters.Regex('^Reset Logo$'), reset_logo))
    app.add_handler(MessageHandler(filters.Regex('^Watermark$'), watermark_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document(content_types=['image/jpeg', 'image/png']), receive_photo))
    app.add_handler(MessageHandler(filters.Regex('^(صغير|متوسط|كبير)$'), handle_size_choice))
    app.add_handler(MessageHandler(filters.Regex('^(منخفضة|متوسطة|عالية|غير شفافة)$'), handle_opacity_choice))
    app.add_handler(MessageHandler(filters.Regex('^(1️⃣ ركن أسفل يمين|2️⃣ منتصف اليمين|3️⃣ ركن أعلى اليسار|4️⃣ أربع أركان)$'), style_choice))
    app.add_handler(CallbackQueryHandler(handle_save))
    app.add_handler(MessageHandler(filters.ALL, block_unlisted))
    logger.info("🚀 البوت شغال!")
    app.run_polling()

if __name__ == '__main__':
    main()
