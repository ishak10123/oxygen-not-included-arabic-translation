import polib
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os
import json
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
    parts = re.split(r'(<[^>]+>|\{[0-9]+\}|\n)', text)
    fixed_parts = []
    for part in parts:
        if part == '\n':
            fixed_parts.append('\n')
        elif (part.startswith('<') and part.endswith('>')) or (part.startswith('{') and part.endswith('}')):
            fixed_parts.append(part)
        else:
            if contains_arabic(part):
                reshaped = reshaper.reshape(part)
                bidi_text = get_display(reshaped)
                fixed_parts.append(bidi_text)
            else:
                fixed_parts.append(part)
    return "".join(fixed_parts)

NEW_TRANSLATIONS = {
    "STRINGS.UI.SCHEDULESCREEN.SCHEDULE_EDITOR": "محرر الجدول",
    "STRINGS.UI.SCHEDULESCREEN.SCHEDULE_NAME_DEFAULT": "الجدول القياسي الافتراضي",
    "STRINGS.UI.SCHEDULESCREEN.ALARM_BUTTON": "تنبيهات الورديات",
    "STRINGS.UI.SCHEDULEGROUPS.HYGENE.NAME": "وقت الاستحمام",
    "STRINGS.UI.SCHEDULEGROUPS.WORKTIME.NAME": "العمل",
    "STRINGS.UI.SCHEDULEGROUPS.RECREATION.NAME": "وقت الاستجمام",
    "STRINGS.UI.SCHEDULEGROUPS.SLEEP.NAME": "وقت النوم",
    "STRINGS.UI.SCHEDULESCREEN.ADD_SCHEDULE": "إضافة جدول جديد",
    "STRINGS.UI.SCHEDULESCREEN.DELETE_SCHEDULE": "حذف الجدول",
    "STRINGS.UI.SCHEDULESCREEN.SCHEDULE_NAME_NEW": "جدول جديد"
}

def safe_save_json(data, file_path):
    temp_path = file_path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def safe_save_po(po_obj, file_path):
    temp_path = file_path + ".tmp"
    try:
        po_obj.save(temp_path)
        os.replace(temp_path, file_path)
        return True
    except Exception as e:
        print(f"Error saving PO: {e}")
        return False

def main():
    workspace_dir = r"c:\Users\ishak\Desktop\arabic_translation.po"
    desktop_po_path = os.path.join(workspace_dir, "strings", "strings.po")
    template_pot_path = os.path.join(workspace_dir, "strings_template.pot")
    cache_path = os.path.join(workspace_dir, "translation_cache.json")
    
    print("Loading strings_template.pot... (this might take a few seconds)")
    template = polib.pofile(template_pot_path, encoding='utf-8')
    template_map = {entry.msgctxt: entry.msgid for entry in template if entry.msgctxt}
    
    print("Loading strings.po...")
    po = polib.pofile(desktop_po_path, encoding='utf-8')
    existing_entries = {entry.msgctxt: entry for entry in po if entry.msgctxt}
    
    # تحميل الكاش
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
            
    added_count = 0
    updated_count = 0
    
    for key, arabic_text in NEW_TRANSLATIONS.items():
        if key not in template_map:
            print(f"[WARN] Key '{key}' not found in template. Skipping.")
            continue
            
        original_msgid = template_map[key]
        processed_arabic = fix_arabic_text(arabic_text)
        
        # إضافة للكاش
        cache[original_msgid] = arabic_text
        
        if key in existing_entries:
            entry = existing_entries[key]
            entry.msgstr = processed_arabic
            updated_count += 1
        else:
            new_entry = polib.POEntry(msgid=original_msgid, msgstr=processed_arabic, msgctxt=key)
            po.append(new_entry)
            existing_entries[key] = new_entry
            added_count += 1
            
    # حفظ ذري
    safe_save_json(cache, cache_path)
    safe_save_po(po, desktop_po_path)
    
    print(f"Successfully processed {len(NEW_TRANSLATIONS)} items:")
    print(f"- Added: {added_count} new entries")
    print(f"- Updated: {updated_count} existing entries")
    
    # نسخ إلى مجلد المودات
    home_dir = os.path.expanduser('~')
    game_mod_dir = os.path.join(home_dir, "Documents", "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings")
    game_po_path = os.path.join(game_mod_dir, "strings.po")
    
    try:
        os.makedirs(game_mod_dir, exist_ok=True)
        shutil.copy(desktop_po_path, game_po_path)
        print(f"[SUCCESS] Copied to game mod folder: {game_po_path}")
    except Exception as mod_err:
        print(f"[ERROR] Could not copy: {mod_err}")

if __name__ == "__main__":
    main()
