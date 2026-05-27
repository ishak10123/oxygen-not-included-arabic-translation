import polib
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os

# تهيئة برنامج إعادة تشكيل الحروف العربية
reshaper = arabic_reshaper.ArabicReshaper(
    arabic_reshaper.config_for_true_type_font(
        "C:\\Windows\\Fonts\\arial.ttf",
        arabic_reshaper.ENABLE_ALL_LIGATURES
    )
)

def contains_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def fix_arabic_text(text):
    if not text or not contains_arabic(text):
        return text
    
    # تقسيم النص بناءً على الروابط والوسوم البرمجية لتجنب تخريبها
    parts = re.split(r'(<[^>]+>|\{[0-9]+\})', text)
    fixed_parts = []
    for part in parts:
        if (part.startswith('<') and part.endswith('>')) or (part.startswith('{') and part.endswith('}')):
            # الحفاظ على الوسم البرمجي كما هو
            fixed_parts.append(part)
        else:
            if contains_arabic(part):
                # إعادة تشكيل الحروف لربطها
                reshaped = reshaper.reshape(part)
                # عكس اتجاه النص ليظهر من اليمين إلى اليسار في محرك اللعبة
                bidi_text = get_display(reshaped)
                fixed_parts.append(bidi_text)
            else:
                fixed_parts.append(part)
                
    return "".join(fixed_parts)

# مسار ملف الترجمة المحلي (الملف النظيف المقروء دائماً)
desktop_po_path = "c:\\Users\\ishak\\Desktop\\arabic_translation.po\\strings\\strings.po"

# فتح ملف الترجمة المصدر
po = polib.pofile(desktop_po_path, encoding='utf-8')
for entry in po:
    if entry.msgstr:
        entry.msgstr = fix_arabic_text(entry.msgstr)

# تحديد مسار مودات اللعبة تلقائياً وحفظ الملف المعالج فيه مباشرة
home_dir = os.path.expanduser('~')
game_mod_dir = os.path.join(home_dir, "Documents", "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings")
game_po_path = os.path.join(game_mod_dir, "strings.po")

# إنشاء المجلدات في مسار اللعبة إذا لم تكن موجودة
os.makedirs(game_mod_dir, exist_ok=True)

# حفظ ملف الترجمة المعالج (المربوط والمعكوس) في مجلد اللعبة مباشرة
po.save(game_po_path)

print("==============================================================")
print("1. [SUCCESS] Read raw Arabic from desktop strings.po successfully!")
print("2. [SUCCESS] Shaped and reversed text for Unity compatibility.")
print(f"3. [SUCCESS] Saved processed file directly to the game mod directory:\n   {game_po_path}")
print("4. [IMPORTANT] Your desktop strings.po remains 100% clean and readable!")
print("==============================================================")

