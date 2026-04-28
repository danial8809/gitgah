import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import json
import os

# توکن ربات و آیدی کانال
TOKEN = "bot_token"
CHANNEL_ID = "@danialmohammadi8"
ADMIN_ID = 123456789
ADMIN_USERNAME = "@danial_M1"

# لیست سفید دوره‌های معتبر
VALID_COURSE_IDS = ["course1", "course2", "course3"]

# مقداردهی اولیه ربات
bot = telebot.TeleBot(TOKEN)

# فایل‌های ذخیره‌سازی
USER_DATA_FILE = "GITGAH/users.json"
COURSES_DATA_FILE = "GITGAH/courses.json"

# تابع بارگذاری دوره‌ها با مدیریت خطاها
def load_courses():
    default_courses = {
        "course1": {
            "name": "دوره ساخت ربات تلگرامی 🤖",
            "price": "690,000 تومان",
            "videos": [
                {"file_id": None, "caption": "بزودی ویدیوهای دوره برات ارسال میشن....", "order": 1}
            ]
        },
        "course2": {
            "name": "دوره طراحی سایت 👨‍💻",
            "price": "بزودی...",
            "videos": [
                {"file_id": "video3.mp4", "caption": None, "order": 1},
                {"file_id": "video4.mp4", "caption": None, "order": 2}
            ]
        },
        "course3": {
            "name": "دوره ساخت اپلیکیشن 📱",
            "price": "بزودی...",
            "videos": [
                {"file_id": "video5.mp4", "caption": None, "order": 1},
                {"file_id": "video6.mp4", "caption": None, "order": 2}
            ]
        }
    }
    try:
        if not os.path.exists(COURSES_DATA_FILE):
            print(f"فایل {COURSES_DATA_FILE} یافت نشد، استفاده از داده‌های پیش‌فرض")
            return default_courses
        with open(COURSES_DATA_FILE, "r", encoding="utf-8") as f:
            file_content = f.read()
            if not file_content.strip():
                print(f"فایل {COURSES_DATA_FILE} خالی است، استفاده از داده‌های پیش‌فرض")
                return default_courses
            try:
                courses = json.loads(file_content)
            except json.JSONDecodeError as e:
                print(f"خطا در parsing فایل courses.json: {str(e)}")
                return default_courses
            # فقط دوره‌های معتبر
            courses = {k: v for k, v in courses.items() if k in VALID_COURSE_IDS}
            for course_id in list(courses.keys()):
                if not isinstance(courses[course_id], dict):
                    print(f"ساختار نامعتبر برای دوره {course_id}: {courses[course_id]}")
                    del courses[course_id]
                    continue
                if "videos" not in courses[course_id] or not isinstance(courses[course_id]["videos"], list):
                    print(f"کلید videos برای دوره {course_id} نامعتبر است، تنظیم به لیست خالی")
                    courses[course_id]["videos"] = []
                if "name" not in courses[course_id]:
                    courses[course_id]["name"] = "دوره بدون نام"
                if "price" not in courses[course_id]:
                    courses[course_id]["price"] = "نامشخص"
                # بررسی ویدیوها
                for video in courses[course_id]["videos"][:]:
                    if not all(key in video for key in ["file_id", "caption", "order"]):
                        print(f"ساختار نامعتبر ویدیو در {course_id}: {video}")
                        courses[course_id]["videos"].remove(video)
                    elif video["file_id"] == "null":  # تبدیل "null" رشته‌ای به None
                        video["file_id"] = None
                # اصلاح orderهای تکراری
                orders = [video["order"] for video in courses[course_id]["videos"]]
                if len(orders) != len(set(orders)):
                    print(f"orderهای تکراری در {course_id}: {orders}")
                    for i, video in enumerate(courses[course_id]["videos"]):
                        video["order"] = i + 1
           
            return courses
    except Exception as e:
        print(f"خطا در بارگذاری courses.json: {str(e)}")
        return default_courses

# تعریف متغیر COURSES
try:
    COURSES = load_courses()
except Exception as e:
    print(f"خطا در مقداردهی اولیه COURSES: {str(e)}")
    COURSES = {
        "course1": {
            "name": "دوره ساخت ربات تلگرامی 🤖",
            "price": "690,000 تومان",
            "videos": []
        },
        "course2": {
            "name": "دوره طراحی سایت 👨‍💻",
            "price": "بزودی...",
            "videos": []
        },
        "course3": {
            "name": "دوره ساخت اپلیکیشن 📱",
            "price": "بزودی...",
            "videos": []
        }
    }


# ذخیره دوره‌ها
def save_courses(courses):
    try:
        os.makedirs(os.path.dirname(COURSES_DATA_FILE), exist_ok=True)
        with open(COURSES_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(courses, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"خطا در ذخیره‌سازی courses.json: {str(e)}")
        raise

# بارگذاری یا ایجاد داده‌های کاربران
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}
    else:
        users = {}
    
    if str(ADMIN_ID) not in users:
        users[str(ADMIN_ID)] = {
            "courses": [],
            "blocked": False,
            "support_message": None,
            "pending_course": None,
            "phone_number": None,
            "full_name": "ادمین",
            "profile_completed": True,
            "pending_subscription_user": None,
            "pending_receipt_message_id": None,
            "admin_state": None
        }
    
    for user_id in users:
        if "phone_number" not in users[user_id]:
            users[user_id]["phone_number"] = None
        if "full_name" not in users[user_id]:
            users[user_id]["full_name"] = None
        if "profile_completed" not in users[user_id]:
            users[user_id]["profile_completed"] = False
        if "pending_subscription_user" not in users[user_id]:
            users[user_id]["pending_subscription_user"] = None
        if "pending_receipt_message_id" not in users[user_id]:
            users[user_id]["pending_receipt_message_id"] = None
        if "admin_state" not in users[user_id]:
            users[user_id]["admin_state"] = None
    
    try:
        save_users(users)
    except Exception as e:
        print(f"خطا در ذخیره‌سازی users.json: {str(e)}")
    return users

# ذخیره کاربران
def save_users(users):
    try:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"خطا در ذخیره‌سازی users.json: {str(e)}")
        raise

# بررسی عضویت کاربر در کانال
def check_membership(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# منوی ادمین
def admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📢 پیام همگانی"),
        KeyboardButton("📊 آمار کاربران"),
        KeyboardButton("🎬 گذاشتن ویدیو"),
        KeyboardButton("🚫 مسدود کردن کاربر"),
        KeyboardButton("💬 پیام به کاربر"),
        KeyboardButton("💳 شارژ اشتراک"),
        KeyboardButton("📽️ کل ویدیوها"),
        KeyboardButton("📋 خریداران")
    )
    return keyboard

# منوی اصلی
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("📚 کل دوره‌ها"),
        KeyboardButton("👤 حساب من"),
        KeyboardButton("🎥 دوره‌های خریداری شده"),
        KeyboardButton("📞 پشتیبانی"),
        KeyboardButton("📖 راهنما")
    )
    return keyboard

# منوی دوره‌ها
def courses_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for course_id, course in COURSES.items():
        keyboard.add(InlineKeyboardButton(f"{course['name']} - {course['price']}", callback_data=f"course_{course_id}"))
    return keyboard

# منوی انتخاب دوره
def select_course_menu(action):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for course_id, course in COURSES.items():
        keyboard.add(InlineKeyboardButton(f"{course['name']}", callback_data=f"{action}_{course_id}"))
    return keyboard

# منوی پرداخت
def payment_menu(course_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💳 درگاه پرداخت", callback_data=f"pay_online_{course_id}"),
        InlineKeyboardButton("🏦 کارت به کارت", callback_data=f"pay_card_{course_id}")
    )
    return keyboard

# منوی پشتیبانی
def support_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💬 پیام مستقیم", callback_data="support_message"),
        InlineKeyboardButton("👨‍💼 آیدی ادمین", callback_data="support_admin"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="support_back")
    )
    return keyboard

# منوی تأیید یا لغو پرداخت
def confirm_payment_menu(course_id, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ تأیید", callback_data=f"confirm_{course_id}_{user_id}"),
        InlineKeyboardButton("❌ لغو", callback_data=f"cancel_{course_id}_{user_id}")
    )
    return keyboard

# منوی دوره‌های فعال برای شارژ اشتراک
def active_courses_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for course_id, course in COURSES.items():
        if course_id not in ["course2", "course3"]:
            keyboard.add(InlineKeyboardButton(f"{course['name']}", callback_data=f"subscribe_{course_id}"))
    return keyboard

# منوی مدیریت ویدیوها
def video_management_menu(course_id, video_index):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("✏️ تغییر کپشن", callback_data=f"edit_caption_{course_id}_{video_index}"),
        InlineKeyboardButton("🔢 تغییر عدد", callback_data=f"edit_order_{course_id}_{video_index}"),
        InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_video_{course_id}_{video_index}")
    )
    return keyboard

# دستور /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users:
        users[user_id] = {
            "courses": [],
            "blocked": False,
            "support_message": None,
            "pending_course": None,
            "phone_number": None,
            "full_name": None,
            "profile_completed": False,
            "admin_state": None
        }
        save_users(users)

    if user_id == str(ADMIN_ID):
        bot.send_message(message.chat.id, "🛠️ خوش آمدید ادمین! به پنل مدیریت دسترسی دارید:", reply_markup=admin_menu())
    else:
        if not check_membership(user_id):
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID[1:]}"),
                InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_membership")
            )
            bot.send_message(message.chat.id, "لطفاً ابتدا در کانال ما عضو شوید:", reply_markup=keyboard)
        else:
            if not users[user_id]["profile_completed"]:
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard.add(KeyboardButton("📱 اشتراک‌گذاری شماره موبایل", request_contact=True))
                bot.send_message(message.chat.id, "برای ادامه، نیاز به ساخت پروفایل دارید. لطفاً شماره موبایل خود را به اشتراک بگذارید:", reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, """سلام 👋  
به **ربات گیتگاه** خوش اومدی! 🤖✨

🎓 گیتگاه یه پلتفرم حرفه‌ای برای فروش دوره‌های آموزشی با کیفیت بالا هست.  
با گیتگاه می‌تونی:

📚 دوره‌های آموزشی متنوع ببینی  
💳 راحت خرید کنی  
📥 بلافاصله به دوره‌هات دسترسی داشته باشی  
💬 سوال بپرسی و پشتیبانی بگیری

برای شروع از دکمه‌های پایین استفاده کن😍

با ما یاد بگیر، رشد کن و پیشرفت کن! 🚀  
""", reply_markup=main_menu(), parse_mode="Markdown")

# مدیریت شماره موبایل
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or users[user_id]["blocked"]:
        bot.send_message(message.chat.id, "🚫 حساب شما غیرفعال است.")
        return

    if not check_membership(user_id) and user_id != str(ADMIN_ID):
        start(message)
        return

    if not users[user_id]["profile_completed"]:
        users[user_id]["phone_number"] = message.contact.phone_number
        save_users(users)
        bot.send_message(message.chat.id, "لطفاً نام و نام خانوادگی خود را وارد کنید:", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_full_name)
    else:
        bot.send_message(message.chat.id, "🎉 خوش آمدید!", reply_markup=main_menu())

# مدیریت نام و نام خانوادگی
def handle_full_name(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or users[user_id]["blocked"]:
        bot.send_message(message.chat.id, "🚫 حساب شما غیرفعال است.")
        return

    if not check_membership(user_id) and user_id != str(ADMIN_ID):
        start(message)
        return

    if not users[user_id]["profile_completed"]:
        users[user_id]["full_name"] = message.text.strip()
        users[user_id]["profile_completed"] = True
        save_users(users)
        bot.send_message(message.chat.id, "✅ پروفایل شما با موفقیت ساخته شد! خوش آمدید!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "🎉 خوش آمدید!", reply_markup=main_menu())

# مسدود کردن کاربر
def block_user(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    target_user_id = message.text.strip()
    users = load_users()
    if target_user_id in users:
        users[target_user_id]["blocked"] = True
        save_users(users)
        bot.send_message(message.chat.id, f"✅ کاربر {target_user_id} با موفقیت مسدود شد.", reply_markup=admin_menu())
        bot.send_message(target_user_id, '🚫 حساب شما توسط ادمین مسدود شده است. اگر فکر می‌کنید اشتباه شده، به ادمین پیام دهید: @erfanabd_admin')
    else:
        bot.send_message(message.chat.id, "❌ آیدی کاربر یافت نشد.", reply_markup=admin_menu())

# ارسال پیام به کاربر
def send_message_to_user(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    try:
        target_user_id, user_message = message.text.split(":", 1)
        target_user_id = target_user_id.strip()
        user_message = user_message.strip()
        users = load_users()
        if target_user_id in users:
            bot.send_message(target_user_id, f"📩 پیام از ادمین:\n{user_message}")
            bot.send_message(message.chat.id, f"✅ پیام به کاربر {target_user_id} ارسال شد.", reply_markup=admin_menu())
        else:
            bot.send_message(message.chat.id, "❌ آیدی کاربر یافت نشد.", reply_markup=admin_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ فرمت اشتباه! لطفاً پیام را با فرمت 'آیدی:متن پیام' وارد کنید.", reply_markup=admin_menu())

# انتخاب دوره برای شارژ اشتراک
def select_course_for_subscription(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    target_user_id = message.text.strip()
    users = load_users()
    if target_user_id in users:
        users[str(ADMIN_ID)] = users.get(str(ADMIN_ID), {
            "courses": [],
            "blocked": False,
            "support_message": None,
            "pending_course": None,
            "phone_number": None,
            "full_name": "ادمین",
            "profile_completed": True,
            "pending_subscription_user": None,
            "pending_receipt_message_id": None,
            "admin_state": None
        })
        users[str(ADMIN_ID)]["pending_subscription_user"] = target_user_id
        try:
            save_users(users)
            bot.send_message(message.chat.id, "📚 دوره‌ای را برای شارژ اشتراک انتخاب کنید:", reply_markup=active_courses_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
    else:
        bot.send_message(message.chat.id, "❌ آیدی کاربر یافت نشد.", reply_markup=admin_menu())

# افزودن اشتراک
def add_subscription(call):
    user_id = str(call.from_user.id)
    if user_id != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "🚫 دسترسی غیرمجاز!")
        return
    course_id = call.data[10:]
    if course_id not in VALID_COURSE_IDS:
        bot.send_message(call.message.chat.id, f"❌ دوره {course_id} نامعتبر است.", reply_markup=admin_menu())
        return
    users = load_users()
    target_user_id = users.get(str(ADMIN_ID), {}).get("pending_subscription_user")
    
    if not target_user_id:
        bot.send_message(call.message.chat.id, "❌ هیچ کاربری برای شارژ اشتراک انتخاب نشده است.", reply_markup=admin_menu())
        return
    if target_user_id not in users:
        bot.send_message(call.message.chat.id, f"❌ کاربر با آیدی {target_user_id} یافت نشد.", reply_markup=admin_menu())
        return
    if course_id not in COURSES:
        bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یافت نشد.", reply_markup=admin_menu())
        return
    
    if course_id not in users[target_user_id]["courses"]:
        users[target_user_id]["courses"].append(course_id)
        try:
            save_users(users)
            bot.send_message(target_user_id, f"🎉 دوره {COURSES[course_id]['name']} به حساب شما اضافه شد.")
            bot.send_message(call.message.chat.id, f"✅ اشتراک {COURSES[course_id]['name']} برای کاربر {target_user_id} فعال شد.", reply_markup=admin_menu())
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اشتراک: {str(e)}")
    else:
        bot.send_message(call.message.chat.id, f"⚠️ کاربر {target_user_id} قبلاً این دوره را دارد.", reply_markup=admin_menu())
    
    users[str(ADMIN_ID)]["pending_subscription_user"] = None
    try:
        save_users(users)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")

# افزودن ویدیو
def add_video_select_course(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    users[str(ADMIN_ID)]["admin_state"] = "add_video_select_course"
    save_users(users)
    bot.send_message(message.chat.id, "📚 دوره‌ای را برای افزودن ویدیو انتخاب کنید:", reply_markup=select_course_menu("add_video"))

def add_video_upload(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    users[str(ADMIN_ID)]["admin_state"] = "add_video_upload"
    save_users(users)
    bot.send_message(message.chat.id, "📹 ویدیو را ارسال کنید:")

def add_video_caption(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    users[str(ADMIN_ID)]["admin_state"] = "add_video_caption"
    save_users(users)
    bot.send_message(message.chat.id, "✏️ کپشن ویدیو را وارد کنید:")

def add_video_order(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    users[str(ADMIN_ID)]["admin_state"] = "add_video_order"
    save_users(users)
    bot.send_message(message.chat.id, "🔢 چندمین ویدیو این دوره باشد؟ (با عدد وارد کنید):")

# نمایش ویدیوها
def view_videos_select_course(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    users[str(ADMIN_ID)]["admin_state"] = "view_videos_select_course"
    save_users(users)
    bot.send_message(message.chat.id, "📚 دوره‌ای را برای مشاهده ویدیوها انتخاب کنید:", reply_markup=select_course_menu("view_videos"))

# مدیریت پیام‌های متنی
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or users[user_id]["blocked"]:
        bot.send_message(message.chat.id, "🚫 حساب شما غیرفعال است. اگر فکر می‌کنید اشتباه شده، به ادمین پیام دهید: @erfanabd_admin")
        return

    if not check_membership(user_id) and user_id != str(ADMIN_ID):
        start(message)
        return

    try:
        if user_id == str(ADMIN_ID):
            admin_state = users[user_id]["admin_state"]
            if admin_state == "add_video_caption":
                if len(message.text.strip()) > 1024:
                    bot.send_message(message.chat.id, "❌ کپشن نمی‌تواند بیش از 1024 کاراکتر باشد.", reply_markup=admin_menu())
                    return
                users[user_id]["admin_state"] = None
                users[user_id]["temp_video_caption"] = message.text.strip()
                save_users(users)
                add_video_order(message)
                return
            elif admin_state == "add_video_order":
                try:
                    order = int(message.text.strip())
                    if order < 1:
                        raise ValueError("عدد ترتیب باید مثبت باشد.")
                    course_id = users[user_id]["temp_course_id"]
                    if course_id not in VALID_COURSE_IDS:
                        raise ValueError(f"دوره {course_id} نامعتبر است.")
                    if course_id not in COURSES:
                        raise ValueError(f"دوره {course_id} یافت نشد.")
                    if order in [v["order"] for v in COURSES[course_id]["videos"]]:
                        max_order = max([v["order"] for v in COURSES[course_id]["videos"]], default=0)
                        order = max_order + 1
                        bot.send_message(message.chat.id, f"⚠️ عدد ترتیب {order} قبلاً استفاده شده، به {order} تغییر کرد.")
                    video = {
                        "file_id": users[user_id]["temp_video_file_id"],
                        "caption": users[user_id]["temp_video_caption"],
                        "order": order
                    }
                    COURSES[course_id]["videos"].append(video)
                    COURSES[course_id]["videos"] = sorted(COURSES[course_id]["videos"], key=lambda x: x["order"])
                    save_courses(COURSES)
                    for uid, user_data in users.items():
                        if course_id in user_data["courses"]:
                            bot.send_message(uid, f"📹 ویدیوی جدیدی به دوره {COURSES[course_id]['name']} اضافه شد!")
                    users[user_id]["admin_state"] = None
                    users[user_id]["temp_course_id"] = None
                    users[user_id]["temp_video_file_id"] = None
                    users[user_id]["temp_video_caption"] = None
                    save_users(users)
                    bot.send_message(message.chat.id, "✅ ویدیو با موفقیت اضافه شد.", reply_markup=admin_menu())
                except ValueError as e:
                    bot.send_message(message.chat.id, f"❌ خطا: {str(e)}", reply_markup=admin_menu())
                return
            elif admin_state == "edit_caption":
                course_id = users[user_id]["temp_course_id"]
                video_index = users[user_id]["temp_video_index"]
                if course_id not in VALID_COURSE_IDS or course_id not in COURSES or video_index >= len(COURSES[course_id]["videos"]):
                    bot.send_message(message.chat.id, f"❌ دوره {course_id} یا ویدیو {video_index} یافت نشد.", reply_markup=admin_menu())
                    return
                if len(message.text.strip()) > 1024:
                    bot.send_message(message.chat.id, "❌ کپشن نمی‌تواند بیش از 1024 کاراکتر باشد.", reply_markup=admin_menu())
                    return
                COURSES[course_id]["videos"][video_index]["caption"] = message.text.strip()
                save_courses(COURSES)
                users[user_id]["admin_state"] = None
                users[user_id]["temp_course_id"] = None
                users[user_id]["temp_video_index"] = None
                save_users(users)
                bot.send_message(message.chat.id, "✅ کپشن ویدیو تغییر کرد.", reply_markup=admin_menu())
                return
            elif admin_state == "edit_order":
                try:
                    order = int(message.text.strip())
                    if order < 1:
                        raise ValueError("عدد ترتیب باید مثبت باشد.")
                    course_id = users[user_id]["temp_course_id"]
                    video_index = users[user_id]["temp_video_index"]
                    if course_id not in VALID_COURSE_IDS or course_id not in COURSES or video_index >= len(COURSES[course_id]["videos"]):
                        raise ValueError(f"دوره {course_id} یا ویدیو {video_index} یافت نشد.")
                    if order in [v["order"] for v in COURSES[course_id]["videos"] if v != COURSES[course_id]["videos"][video_index]]:
                        max_order = max([v["order"] for v in COURSES[course_id]["videos"]], default=0)
                        order = max_order + 1
                        bot.send_message(message.chat.id, f"⚠️ عدد ترتیب {order} قبلاً استفاده شده، به {order} تغییر کرد.")
                    COURSES[course_id]["videos"][video_index]["order"] = order
                    COURSES[course_id]["videos"] = sorted(COURSES[course_id]["videos"], key=lambda x: x["order"])
                    save_courses(COURSES)
                    users[user_id]["admin_state"] = None
                    users[user_id]["temp_course_id"] = None
                    users[user_id]["temp_video_index"] = None
                    save_users(users)
                    bot.send_message(message.chat.id, "✅ ترتیب ویدیو تغییر کرد.", reply_markup=admin_menu())
                except ValueError as e:
                    bot.send_message(message.chat.id, f"❌ خطا: {str(e)}", reply_markup=admin_menu())
                return
            elif message.text == "📢 پیام همگانی":
                bot.send_message(message.chat.id, "📢 متن پیام همگانی را وارد کنید:")
                bot.register_next_step_handler(message, broadcast_message)
            elif message.text == "📊 آمار کاربران":
                bot.send_message(message.chat.id, f"📊 تعداد کاربران: {len(users)}")
            elif message.text == "📋 خریداران":
                buyers_found = False
                for buyer_id, buyer_data in users.items():
                    if buyer_data["courses"]:
                        courses = [COURSES.get(course_id, {"name": "دوره نامشخص"})["name"] for course_id in buyer_data["courses"]]
                        full_name = buyer_data["full_name"] or "ثبت نشده"
                        phone = buyer_data["phone_number"] or "ثبت نشده"
                        bot.send_message(
                            message.chat.id,
                            f"👤 کاربر {buyer_id}:\nنام و نام خانوادگی: {full_name}\nشماره موبایل: {phone}\nدوره‌های خریداری‌شده: {', '.join(courses)}"
                        )
                        buyers_found = True
                if not buyers_found:
                    bot.send_message(message.chat.id, "😔 هنوز هیچ کاربری دوره‌ای خریداری نکرده است.")
            elif message.text == "🚫 مسدود کردن کاربر":
                bot.send_message(message.chat.id, "🚫 آیدی کاربری که می‌خواهید مسدود کنید را وارد کنید:")
                bot.register_next_step_handler(message, block_user)
            elif message.text == "💬 پیام به کاربر":
                bot.send_message(message.chat.id, "💬 آیدی کاربر و پیام را با فرمت 'آیدی:متن پیام' وارد کنید (مثال: 123456789:سلام):")
                bot.register_next_step_handler(message, send_message_to_user)
            elif message.text == "💳 شارژ اشتراک":
                bot.send_message(message.chat.id, "💳 آیدی کاربری که می‌خواهید اشتراک او را شارژ کنید را وارد کنید:")
                bot.register_next_step_handler(message, select_course_for_subscription)
            elif message.text == "🎬 گذاشتن ویدیو":
                add_video_select_course(message)
            elif message.text == "📽️ کل ویدیوها":
                view_videos_select_course(message)
            else:
                bot.send_message(message.chat.id, "🛠️ لطفاً از منوی ادمین انتخاب کنید:", reply_markup=admin_menu())
        else:
            if message.text == "📚 کل دوره‌ها":
                bot.send_message(message.chat.id, "📚 دوره‌های موجود:", reply_markup=courses_menu())
            elif message.text == "👤 حساب من":
                courses_count = len(users[user_id]["courses"])
                status = "✅ فعال" if not users[user_id]["blocked"] else "🚫 غیرفعال"
                phone = users[user_id]["phone_number"] or "ثبت نشده"
                full_name = users[user_id]["full_name"] or "ثبت نشده"
                bot.send_message(
                    message.chat.id,
                    f"👤 حساب شما:\nنام و نام خانوادگی: {full_name}\nشماره موبایل: {phone}\nتعداد دوره‌های خریداری شده: {courses_count}\nوضعیت: {status}"
                )
            elif message.text == "🎥 دوره‌های خریداری شده":
                if not users[user_id]["courses"]:
                    bot.send_message(message.chat.id, "😔 شما هنوز دوره‌ای خریداری نکرده‌اید.")
                else:
                    keyboard = InlineKeyboardMarkup(row_width=1)
                    for course_id in users[user_id]["courses"]:
                        course_name = COURSES.get(course_id, {"name": "دوره نامشخص"})["name"]
                        keyboard.add(InlineKeyboardButton(course_name, callback_data=f"view_{course_id}"))
                    bot.send_message(message.chat.id, "🎥 دوره‌های خریداری شده:", reply_markup=keyboard)
            elif message.text == "📖 راهنما":
                bot.send_message(message.chat.id, '''📖 راهنمای استفاده از ربات گیتگاه:

با استفاده از دکمه‌های زیر می‌تونی به امکانات مختلف دسترسی پیدا کنی 👇

📚 **کل دوره‌ها**  
مشاهده لیست کامل دوره‌های آموزشی موجود در گیتگاه

👤 **حساب من**  
نمایش اطلاعات حساب، مثل تعداد دوره‌های خریداری‌شده و نام شما

🎥 **دوره‌های خریداری شده**  
لیست دوره‌هایی که قبلاً خریدی، با امکان دریافت لینک و دسترسی مجدد

📞 **پشتیبانی**  
ارسال پیام به تیم پشتیبانی گیتگاه؛ هر سوال یا مشکلی داشتی همین‌جا مطرح کن

📖 **راهنما**  
همین صفحه‌ای که الان می‌بینی 😄 شامل توضیح همه دکمه‌ها و امکانات ربات

🚀 گیتگاه همراه تو در مسیر یادگیری و پیشرفت!
''', parse_mode="Markdown")
            elif message.text == "📞 پشتیبانی":
                bot.send_message(message.chat.id, "📞 پشتیبانی:", reply_markup=support_menu())
            elif users[user_id]["support_message"] is not None:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("پاسخ", callback_data=f"reply_{user_id}"))
                bot.send_message(ADMIN_ID, f"📩 پیام از کاربر {user_id}:\n{message.text}", reply_markup=keyboard)
                bot.send_message(message.chat.id, "✅ پیام شما به ادمین ارسال شد.")
                users[user_id]["support_message"] = None
                save_users(users)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطا: {str(e)}")

# مدیریت ویدیوهای ارسالی
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id != str(ADMIN_ID) or users[user_id]["admin_state"] != "add_video_upload":
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز یا مرحله اشتباه!")
        return

    try:
        users[user_id]["temp_video_file_id"] = message.video.file_id
        save_users(users)
        add_video_caption(message)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا در ذخیره‌سازی ویدیو: {str(e)}")

# مدیریت دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = str(call.from_user.id)
    users = load_users()


    try:
        if call.data == "check_membership":
            if check_membership(user_id):
                if not users[user_id]["profile_completed"]:
                    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                    keyboard.add(KeyboardButton("📱 اشتراک‌گذاری شماره موبایل", request_contact=True))
                    bot.send_message(call.message.chat.id, "برای ادامه، نیاز به ساخت پروفایل دارید. لطفاً شماره موبایل خود را به اشتراک بگذارید:", reply_markup=keyboard)
                else:
                    bot.send_message(call.message.chat.id, "🎉 خوش آمدید!", reply_markup=main_menu())
            else:
                bot.send_message(call.message.chat.id, "❌ هنوز در کانال عضو نشده‌اید.")
        elif call.data.startswith("course_"):
            course_id = call.data[7:]
            if course_id not in VALID_COURSE_IDS:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} نامعتبر است.")
                return
            if course_id not in COURSES:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} یافت نشد.")
                return
            if course_id in ["course2", "course3"]:
                bot.answer_callback_query(call.id, "⏳ این دوره به‌زودی در دسترس خواهد بود.")
            else:
                bot.send_message(call.message.chat.id, f"💰 پرداخت برای {COURSES[course_id]['name']}:", reply_markup=payment_menu(course_id))
        elif call.data.startswith("pay_online_"):
            course_id = call.data[11:]
            if course_id not in VALID_COURSE_IDS:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} نامعتبر است.")
                return
            if course_id not in COURSES:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} یافت نشد.")
                return
            bot.answer_callback_query(call.id, "⏳ درگاه پرداخت به‌زودی فعال می‌شود.")
        elif call.data.startswith("pay_card_"):
            course_id = call.data[9:]
            if course_id not in VALID_COURSE_IDS:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} نامعتبر است.")
                return
            if course_id not in COURSES:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} یافت نشد.")
                return
            users[user_id]["pending_course"] = course_id
            try:
                save_users(users)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
                return
            bot.send_message(call.message.chat.id, f"شماره کارت:\n💳 `6104338645640596`\nبنام: عرفان عبدالهی\nمبلغ: {COURSES[course_id]['price']}\nلطفاً تصویر رسید را ارسال کنید.", parse_mode="Markdown")
        elif call.data.startswith("view_"):
            course_id = call.data[5:]
            if course_id not in VALID_COURSE_IDS:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} نامعتبر است.")
                return
            if course_id not in COURSES:
                bot.answer_callback_query(call.id, f"❌ دوره {course_id} یافت نشد.")
                return
            if user_id == str(ADMIN_ID):
                videos = sorted(COURSES[course_id]["videos"], key=lambda x: x["order"])
                if not videos:
                    bot.send_message(call.message.chat.id, "😔 هیچ ویدیویی برای این دوره ثبت نشده است.", reply_markup=admin_menu())
                else:
                    for i, video in enumerate(videos):
                        caption = f"🎥 ویدیو شماره {video['order']}: {video['caption'] or 'بدون کپشن'}"
                        if video["file_id"]:
                            bot.send_video(user_id, video["file_id"], caption=caption, reply_markup=video_management_menu(course_id, i))
                        else:
                            bot.send_message(user_id, caption, reply_markup=video_management_menu(course_id, i))
            elif course_id in users[user_id]["courses"]:
                videos = sorted(COURSES[course_id]["videos"], key=lambda x: x["order"])
                for video in videos:
                    caption = f"🎥 جلسه {video['order']}: {video['caption'] or 'بدون کپشن'}"
                    if video["file_id"]:
                        bot.send_video(user_id, video["file_id"], caption=caption)
                    else:
                        bot.send_message(user_id, caption)
                bot.send_message(user_id, "📹 ویدیوهای دیگر این دوره اگر باقیمانده باشد، بزودی برایتان اضافه می‌شود.")
            else:
                bot.answer_callback_query(call.id, "🚫 شما این دوره را خریداری نکرده‌اید.")
        elif call.data == "support_message":
            bot.send_message(call.message.chat.id, "💬 متن پیام خود را وارد کنید:")
            users[user_id]["support_message"] = True
            try:
                save_users(users)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
        elif call.data == "support_admin":
            bot.send_message(call.message.chat.id, f"👨‍💼 آیدی ادمین: {ADMIN_USERNAME}")
        elif call.data == "support_back":
            bot.send_message(call.message.chat.id, "🔙 بازگشت به منوی اصلی:", reply_markup=main_menu())
        elif call.data.startswith("confirm_"):
            course_id, target_user_id = call.data[8:].split("_")
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS:
                    bot.answer_callback_query(call.id, f"❌ دوره {course_id} نامعتبر است.")
                    return
                if course_id not in COURSES:
                    bot.answer_callback_query(call.id, f"❌ دوره {course_id} یافت نشد.")
                    return
                if target_user_id not in users:
                    bot.answer_callback_query(call.id, f"❌ کاربر {target_user_id} یافت نشد.")
                    return
                users[target_user_id]["courses"].append(course_id)
                try:
                    save_users(users)
                    bot.send_message(target_user_id, f"🎉 دوره {COURSES[course_id]['name']} به حساب شما اضافه شد.")
                    bot.send_message(call.message.chat.id, "✅ پرداخت تأیید شد.")
                    if users[target_user_id]["pending_receipt_message_id"]:
                        try:
                            bot.edit_message_reply_markup(
                                chat_id=ADMIN_ID,
                                message_id=users[target_user_id]["pending_receipt_message_id"],
                                reply_markup=None
                            )
                        except Exception as e:
                            print(f"خطا در حذف دکمه‌ها: {str(e)}")
                    users[target_user_id]["pending_receipt_message_id"] = None
                    save_users(users)
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
            else:
                bot.answer_callback_query(call.id, "🚫 دسترسی غیرمجاز!")
        elif call.data.startswith("cancel_"):
            course_id, target_user_id = call.data[8:].split("_")
            if user_id == str(ADMIN_ID):
                if target_user_id in users and users[target_user_id]["pending_receipt_message_id"]:
                    try:
                        bot.edit_message_reply_markup(
                            chat_id=ADMIN_ID,
                            message_id=users[target_user_id]["pending_receipt_message_id"],
                            reply_markup=None
                        )
                    except Exception as e:
                        print(f"خطا در حذف دکمه‌ها: {str(e)}")
                users[target_user_id]["pending_receipt_message_id"] = None
                try:
                    save_users(users)
                    bot.send_message(call.message.chat.id, "❌ پرداخت لغو شد.", reply_markup=admin_menu())
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
            else:
                bot.answer_callback_query(call.id, "🚫 دسترسی غیرمجاز!")
        elif call.data.startswith("reply_"):
            target_user_id = call.data[6:]
            users[str(ADMIN_ID)]["support_message"] = target_user_id
            try:
                save_users(users)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
            bot.send_message(call.message.chat.id, "📩 متن پاسخ خود را با فرمت 'پاسخ به پشتیبانی: متن' وارد کنید:")
        elif call.data.startswith("subscribe_"):
            add_subscription(call)
        elif call.data.startswith("add_video_"):
            course_id = call.data[10:]
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS:
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} نامعتبر است.", reply_markup=admin_menu())
                    return
                if course_id not in COURSES:
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یافت نشد.", reply_markup=admin_menu())
                    return
                users[user_id]["temp_course_id"] = course_id
                users[user_id]["admin_state"] = "add_video_upload"
                save_users(users)
                bot.send_message(call.message.chat.id, "📹 ویدیو را ارسال کنید:")
        elif call.data.startswith("view_videos_"):
            course_id = call.data[12:]
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS:
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} نامعتبر است.", reply_markup=admin_menu())
                    return
                if course_id not in COURSES:
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یافت نشد.", reply_markup=admin_menu())
                    return
                videos = sorted(COURSES[course_id]["videos"], key=lambda x: x["order"])
                if not videos:
                    bot.send_message(call.message.chat.id, "😔 هیچ ویدیویی برای این دوره ثبت نشده است.", reply_markup=admin_menu())
                else:
                    for i, video in enumerate(videos):
                        caption = f"🎥 جلسه {video['order']}: {video['caption'] or 'بدون کپشن'}"
                        if video["file_id"]:
                            bot.send_video(user_id, video["file_id"], caption=caption, reply_markup=video_management_menu(course_id, i))
                        else:
                            bot.send_message(user_id, caption, reply_markup=video_management_menu(course_id, i))
                users[user_id]["admin_state"] = None
                save_users(users)
            else:
                bot.answer_callback_query(call.id, "🚫 دسترسی غیرمجاز!")
        elif call.data.startswith("edit_caption_"):
            course_id, video_index = call.data[13:].split("_")
            video_index = int(video_index)
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS or course_id not in COURSES or video_index >= len(COURSES[course_id]["videos"]):
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یا ویدیو {video_index} یافت نشد.", reply_markup=admin_menu())
                    return
                users[user_id]["admin_state"] = "edit_caption"
                users[user_id]["temp_course_id"] = course_id
                users[user_id]["temp_video_index"] = video_index
                save_users(users)
                bot.send_message(call.message.chat.id, "✏️ متن جدید کپشن را وارد کنید:")
        elif call.data.startswith("edit_order_"):
            course_id, video_index = call.data[11:].split("_")
            video_index = int(video_index)
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS or course_id not in COURSES or video_index >= len(COURSES[course_id]["videos"]):
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یا ویدیو {video_index} یافت نشد.", reply_markup=admin_menu())
                    return
                users[user_id]["admin_state"] = "edit_order"
                users[user_id]["temp_course_id"] = course_id
                users[user_id]["temp_video_index"] = video_index
                save_users(users)
                bot.send_message(call.message.chat.id, "🔢 عدد جدید ترتیب را وارد کنید:")
        elif call.data.startswith("delete_video_"):
            course_id, video_index = call.data[13:].split("_")
            video_index = int(video_index)
            if user_id == str(ADMIN_ID):
                if course_id not in VALID_COURSE_IDS or course_id not in COURSES or video_index >= len(COURSES[course_id]["videos"]):
                    bot.send_message(call.message.chat.id, f"❌ دوره {course_id} یا ویدیو {video_index} یافت نشد.", reply_markup=admin_menu())
                    return
                COURSES[course_id]["videos"].pop(video_index)
                for i, video in enumerate(COURSES[course_id]["videos"]):
                    video["order"] = i + 1
                save_courses(COURSES)
                bot.send_message(call.message.chat.id, "🗑️ ویدیو با موفقیت حذف شد.", reply_markup=admin_menu())
        else:
            bot.answer_callback_query(call.id, f"❌ داده نامعتبر: {call.data}")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ خطا: {str(e)}")
        bot.answer_callback_query(call.id, f"❌ خطایی رخ داد: {str(e)}")

# مدیریت رسید پرداخت
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = str(message.from_user.id)
    users = load_users()
    
    if user_id not in users or "pending_course" not in users[user_id]:
        bot.send_message(message.chat.id, "❌ ابتدا یک دوره را انتخاب کنید و گزینه کارت به کارت را بزنید.")
        return
    
    course_id = users[user_id]["pending_course"]
    if course_id not in VALID_COURSE_IDS:
        bot.send_message(message.chat.id, f"❌ دوره {course_id} نامعتبر است.")
        return
    if course_id not in COURSES:
        bot.send_message(message.chat.id, f"❌ دوره {course_id} یافت نشد.")
        return
    
    try:
        course_name = COURSES[course_id]["name"]
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"رسید برای {course_name}\nبا آیدی {user_id}")
        receipt_message = bot.send_message(ADMIN_ID, f"📄 رسید پرداخت از کاربر {user_id} برای {course_name}:", 
                                         reply_markup=confirm_payment_menu(course_id, user_id))
        users[user_id]["pending_receipt_message_id"] = receipt_message.message_id
        bot.send_message(message.chat.id, "✅ رسید شما ارسال شد. منتظر تأیید ادمین باشید.")
        users[user_id]["pending_course"] = None
        try:
            save_users(users)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا در ذخیره‌سازی اطلاعات: {str(e)}")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ خطایی در ارسال رسید رخ داد. دوباره تلاش کنید.")
        bot.send_message(ADMIN_ID, f"⚠️ خطا در ارسال رسید از کاربر {user_id}: {str(e)}")

# پنل مدیریت
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        bot.send_message(message.chat.id, "🛠️ پنل مدیریت:", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز! فقط ادمین می‌تواند از این دستور استفاده کند.")

# پیام همگانی
def broadcast_message(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")
        return
    users = load_users()
    for user_id in users:
        try:
            bot.send_message(user_id, message.text)
        except:
            pass
    bot.send_message(message.chat.id, "✅ پیام همگانی ارسال شد.", reply_markup=admin_menu())

# دستور دیباگ
@bot.message_handler(commands=['debug_courses'])
def debug_courses(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        bot.send_message(message.chat.id, f"COURSES:\n{json.dumps(COURSES, indent=2, ensure_ascii=False)}")
    else:
        bot.send_message(message.chat.id, "🚫 دسترسی غیرمجاز!")

# شروع ربات
try:
    bot.polling()
except Exception as e:
    print(f"خطا در اجرای ربات: {str(e)}")
