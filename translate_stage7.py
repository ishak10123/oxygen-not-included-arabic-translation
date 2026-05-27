import polib
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os
import shutil

# 1. تهيئة برنامج إعادة تشكيل الحروف العربية بنفس تكوين اللعبة
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
    parts = re.split(r'(<[^>]+>|\{[0-9]+\}|\n)', text)
    fixed_parts = []
    for part in parts:
        if part == '\n':
            fixed_parts.append('\n')
        elif (part.startswith('<') and part.endswith('>')) or (part.startswith('{') and part.endswith('}')):
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

# 2. الترجمات العربية المقترحة للمرحلة السابعة (سمات المستنسخين)
NEW_TRANSLATIONS = {
    # 1. حساسية (Allergies)
    "STRINGS.DUPLICANTS.TRAITS.ALLERGIES.NAME": 'حساسية',
    "STRINGS.DUPLICANTS.TRAITS.ALLERGIES.DESC": 'سيعطس هذا المستنسخ بشكل لا يمكن السيطرة عليه عند تعرضه لحبوب اللقاح الموجودة في <link="POLLENGERMS">عطر الأزهار</link>',
    "STRINGS.DUPLICANTS.TRAITS.ALLERGIES.SHORT_DESC": 'تفاعل حساسية تجاه <b><link="POLLENGERMS">عطر الأزهار</link></b>',
    
    # 2. فقر الدم (Anemic)
    "STRINGS.DUPLICANTS.TRAITS.ANEMIC.NAME": 'مصاب بفقر الدم',
    "STRINGS.DUPLICANTS.TRAITS.ANEMIC.DESC": 'يواجه هذا المستنسخ صعوبة في مواكبة الآخرين'
}

def main():
    desktop_po_path = r"c:\Users\ishak\Desktop\arabic_translation.po\strings\strings.po"
    template_pot_path = r"c:\Users\ishak\Desktop\arabic_translation.po\strings_template.pot"
    
    print("Loading original template strings_template.pot...")
    template = polib.pofile(template_pot_path, encoding='utf-8')
    
    # بناء قاموس للحصول على النص الإنجليزي الأصلي من المفتاح msgctxt
    template_map = {}
    for entry in template:
        if entry.msgctxt:
            template_map[entry.msgctxt] = entry.msgid
            
    print("Loading desktop strings.po...")
    po = polib.pofile(desktop_po_path, encoding='utf-8')
    
    # بناء خريطة للمفاتيح الموجودة بالفعل لتحديثها بدلاً من تكرارها
    existing_entries = {entry.msgctxt: entry for entry in po if entry.msgctxt}
    
    added_count = 0
    updated_count = 0
    
    for key, arabic_text in NEW_TRANSLATIONS.items():
        if key not in template_map:
            print(f"[WARNING] Key '{key}' not found in template. Skipping.")
            continue
            
        original_msgid = template_map[key]
        processed_arabic = fix_arabic_text(arabic_text)
        
        if key in existing_entries:
            # تحديث ترجمة موجودة بالفعل
            entry = existing_entries[key]
            entry.msgstr = processed_arabic
            updated_count += 1
        else:
            # إنشاء مدخل جديد تماماً
            new_entry = polib.POEntry(
                msgid=original_msgid,
                msgstr=processed_arabic,
                msgctxt=key
            )
            po.append(new_entry)
            added_count += 1
            
    # حفظ التغييرات على سطح المكتب
    po.save(desktop_po_path)
    print(f"Successfully processed {len(NEW_TRANSLATIONS)} items:")
    print(f"- Added: {added_count} new entries")
    print(f"- Updated: {updated_count} existing entries")
    print(f"Saved to: {desktop_po_path}")
    
    # نسخ الملف المعالج مباشرة إلى مجلد مودات اللعبة
    home_dir = os.path.expanduser('~')
    game_mod_dir = os.path.join(home_dir, "Documents", "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings")
    game_po_path = os.path.join(game_mod_dir, "strings.po")
    
    os.makedirs(game_mod_dir, exist_ok=True)
    shutil.copy(desktop_po_path, game_po_path)
    print(f"Copied final processed file to game mod directory:\n {game_po_path}")

if __name__ == "__main__":
    main()
