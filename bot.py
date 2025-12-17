import os
import telebot
from telebot import types

# ================== الإعدادات (من Environment Variables) ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")
OWNER_NAME = os.getenv("OWNER_NAME", "عبد الملك")

if not BOT_TOKEN or not BOT_PASSWORD:
    raise ValueError("❌ BOT_TOKEN أو BOT_PASSWORD غير موجود في Environment Variables")

bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)

# ================== تخزين حالة المستخدم ==================
users = {}

# ================== المواد ==================
SUBJECTS = [
    "Arabic",
    "Biology",
    "Chemistry",
    "English",
    "Islamic Studies",
    "Math",
    "Physics",
    "Social Studies"
]

# ================== لوحات الأزرار ==================
def kb_start():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("▶️ Start")
    return kb

def kb_subjects():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(SUBJECTS), 2):
        kb.row(*SUBJECTS[i:i+2])
    kb.add("🔙 الرجوع للبداية")
    return kb

def kb_sections():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("✏️ حل", "📊 تقرير")
    kb.add("🔄 تغيير المادة")
    kb.add("🔙 الرجوع للبداية")
    return kb

# ================== أدوات مساعدة ==================
def reset_user(user_id):
    users[user_id] = {
        "state": "WAIT_START",
        "login": "",
        "subject": "",
        "lessons": ""
    }

# ================== بدء المحادثة ==================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    reset_user(user_id)

    bot.send_message(
        message.chat.id,
        f"""👋 مرحبًا بك في *بوت ألفا*

أهلاً بك يا {OWNER_NAME} ✔️  
تم تصميم هذا البوت لتسهيل تنفيذ الطلبات الدراسية  
وتنظيم العمل على المواد والدروس بطريقة واضحة ومباشرة.

⬅️ اضغط *Start* للمتابعة""",
        parse_mode="Markdown",
        reply_markup=kb_start()
    )

# ================== المعالج الرئيسي ==================
@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in users:
        reset_user(user_id)

    state = users[user_id]["state"]

    # ===== الرجوع للبداية =====
    if text == "🔙 الرجوع للبداية":
        reset_user(user_id)
        bot.send_message(
            message.chat.id,
            "🔁 تم الرجوع للبداية\n⬅️ اضغط Start للمتابعة",
            reply_markup=kb_start()
        )
        return

    # ===== Start =====
    if state == "WAIT_START":
        if text == "▶️ Start":
            users[user_id]["state"] = "WAIT_PASSWORD"
            bot.send_message(
                message.chat.id,
                "🔐 أدخل كلمة المرور:",
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ اضغط Start للمتابعة",
                reply_markup=kb_start()
            )
        return

    # ===== كلمة المرور =====
    if state == "WAIT_PASSWORD":
        if text == BOT_PASSWORD:
            users[user_id]["state"] = "WELCOME"
            bot.send_message(
                message.chat.id,
                f"""✔️ تم التحقق بنجاح

👋 مرحبًا بك في *بوت ألفا* يا {OWNER_NAME}

✍️ أرسل الآن اليوزر والباسورد:""",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ كلمة المرور غير صحيحة"
            )
        return

    # ===== اليوزر والباس =====
    if state == "WELCOME":
        users[user_id]["login"] = text
        users[user_id]["state"] = "WAIT_SUBJECT"
        bot.send_message(
            message.chat.id,
            "✔️ تم حفظ البيانات\n📚 اختر المادة:",
            reply_markup=kb_subjects()
        )
        return

    # ===== اختيار المادة =====
    if state == "WAIT_SUBJECT":
        if text in SUBJECTS:
            users[user_id]["subject"] = text
            users[user_id]["state"] = "WAIT_SECTION"
            bot.send_message(
                message.chat.id,
                f"✔️ المادة المختارة: *{text}*\nاختر القسم:",
                parse_mode="Markdown",
                reply_markup=kb_sections()
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ اختر مادة من القائمة فقط",
                reply_markup=kb_subjects()
            )
        return

    # ===== تغيير المادة =====
    if text == "🔄 تغيير المادة":
        users[user_id]["state"] = "WAIT_SUBJECT"
        bot.send_message(
            message.chat.id,
            "📚 اختر مادة جديدة:",
            reply_markup=kb_subjects()
        )
        return

    # ===== الأقسام =====
    if state == "WAIT_SECTION":
        if text == "📊 تقرير":
            bot.send_message(
                message.chat.id,
                f"""📊 *قسم التقرير*
✔️ المادة: {users[user_id]['subject']}
✔️ سيتم توليد برومت التقرير بناءً على بياناتك""",
                parse_mode="Markdown",
                reply_markup=kb_sections()
            )

        elif text == "✏️ حل":
            users[user_id]["state"] = "WAIT_LESSONS"
            bot.send_message(
                message.chat.id,
                "✏️ أدخل أرقام الدروس المطلوبة (مثال: 1,2,5):"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ اختر من الأزرار فقط",
                reply_markup=kb_sections()
            )
        return

    # ===== إدخال الدروس =====
    if state == "WAIT_LESSONS":
        users[user_id]["lessons"] = text
        users[user_id]["state"] = "WAIT_SECTION"
        bot.send_message(
            message.chat.id,
            f"""✔️ تم استلام الدروس

📘 المادة: {users[user_id]['subject']}
📚 الدروس: {text}

🧠 *البرومت جاهز الآن للنسخ*
⬅️ يمكنك اختيار قسم آخر أو تغيير المادة""",
            parse_mode="Markdown",
            reply_markup=kb_sections()
        )
        return

# ================== تشغيل البوت ==================
print("✅ بوت ألفا يعمل بثبات")
bot.infinity_polling(skip_pending=True)
