import polib
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os
import sys

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
    
    # تقسيم النص بناءً على الروابط والوسوم البرمجية لتجنب تخريبها (يدعم جميع الأقواس المعقوفة مثل {Hotkey} و {0})
    parts = re.split(r'(<[^>]+>|\{[^}]+\})', text)
    fixed_parts = []
    for part in parts:
        if ((part.startswith('<') and part.endswith('>')) or (part.startswith('{') and part.endswith('}'))) and not contains_arabic(part):
            # الحفاظ على الوسم البرمجي كما هو (فقط إذا كان لا يحتوي على لغة عربية بداخله)
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

def get_windows_documents_path():
    """الاستعلام عن مسار مجلد المستندات الفعلي والنشط من سجل نظام ويندوز لدعم المجلدات الموجهة أو OneDrive"""
    import sys
    if sys.platform.startswith('win'):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                personal_path, _ = winreg.QueryValueEx(key, "Personal")
            return os.path.expandvars(personal_path)
        except Exception as e:
            print(f"[WARN] Failed to query registry for Documents folder: {e}. Falling back to default.")
    return os.path.join(os.path.expanduser('~'), "Documents")

# 1. تحديد المسارات النسبية داخل المشروع
current_dir = os.path.dirname(os.path.abspath(__file__))
clean_po_path = os.path.join(current_dir, "strings", "strings.po")
workspace_compiled_dir = os.path.join(current_dir, "arabic_translation", "strings")
workspace_compiled_po_path = os.path.join(workspace_compiled_dir, "strings.po")

if not os.path.exists(clean_po_path):
    print(f"[ERROR] Source clean PO file not found at: {clean_po_path}")
    sys.exit(1)

# 2. فتح ملف الترجمة المصدر النظيف
po = polib.pofile(clean_po_path, encoding='utf-8')

# 3. معالجة النصوص (الربط والعكس)
for entry in po:
    if entry.msgstr:
        entry.msgstr = fix_arabic_text(entry.msgstr)

# 4. حفظ النسخة المعالجة في مجلد المشروع لـ GitHub
os.makedirs(workspace_compiled_dir, exist_ok=True)
po.save(workspace_compiled_po_path)

# 5. تحديد مسار مودات اللعبة تلقائياً وحفظ الملف المعالج فيه مباشرة
documents_dir = get_windows_documents_path()
game_mod_dir = os.path.join(documents_dir, "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings")
game_po_path = os.path.join(game_mod_dir, "strings.po")

# إنشاء المجلدات في مسار اللعبة إذا لم تكن موجودة
os.makedirs(game_mod_dir, exist_ok=True)

# حفظ ملف الترجمة المعالج (المربوط والمعكوس) في مجلد اللعبة مباشرة
po.save(game_po_path)

print("==============================================================")
print("1. [SUCCESS] Read clean Arabic from project strings.po successfully!")
print("2. [SUCCESS] Shaped and reversed text for Unity compatibility.")
print(f"3. [SUCCESS] Saved processed file to workspace mod: {workspace_compiled_po_path}")
print(f"4. [SUCCESS] Saved processed file directly to the game mod directory:\n   {game_po_path}")
print("5. [IMPORTANT] Your source strings/strings.po remains 100% clean and readable!")
print("==============================================================")

