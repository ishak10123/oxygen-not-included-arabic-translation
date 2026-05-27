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

# 2. الترجمات العربية المقترحة للمرحلة الخامسة (الأجهزة والمباني الأساسية)
NEW_TRANSLATIONS = {
    # 1. المولد اليدوي (Manual Generator)
    "STRINGS.BUILDINGS.PREFABS.MANUALGENERATOR.NAME": '<link="MANUALGENERATOR">المولد اليدوي</link>',
    "STRINGS.BUILDINGS.PREFABS.MANUALGENERATOR.DESC": 'مشاهدة المستنسخين يركضون عليه أمر رائع... الطاقة الكهربائية هي مجرد مكافأة إضافية.',
    "STRINGS.BUILDINGS.PREFABS.MANUALGENERATOR.EFFECT": 'يحول الجهد اليدوي إلى <link="POWER">طاقة</link> كهربائية.',
    
    # 2. ناشر الأكسجين (Oxygen Diffuser)
    "STRINGS.BUILDINGS.PREFABS.MINERALDEOXIDIZER.NAME": '<link="MINERALDEOXIDIZER">ناشر الأكسجين</link>',
    "STRINGS.BUILDINGS.PREFABS.MINERALDEOXIDIZER.DESC": 'ناشرات الأكسجين غير فعالة، لكنها تنتج ما يكفي من الأكسجين لإبقاء المستعمرة تتنفس.',
    "STRINGS.BUILDINGS.PREFABS.MINERALDEOXIDIZER.EFFECT": 'تحول كميات كبيرة من <link="ALGAE">الطحالب</link> إلى <link="OXYGEN">أكسجين</link>.\n\nتصبح خاملة عندما تصل المنطقة إلى أقصى ضغط.',
    
    # 3. المرحاض البدائي (Outhouse)
    "STRINGS.BUILDINGS.PREFABS.OUTHOUSE.NAME": '<link="OUTHOUSE">المرحاض البدائي</link>',
    "STRINGS.BUILDINGS.PREFABS.OUTHOUSE.DESC": 'المستعمرة التي تأكل معاً، تقضي حاجتها معاً.',
    "STRINGS.BUILDINGS.PREFABS.OUTHOUSE.EFFECT": 'يمنح المستنسخين مكاناً لقضاء حاجتهم.\n\nلا يتطلب أي <link="LIQUIDPIPING">أنابيب</link>.\n\nيجب إفراغه دورياً من <link="TOXICSAND">التراب الملوث</link>.',
    
    # 4. حوض الغسيل (Wash Basin)
    "STRINGS.BUILDINGS.PREFABS.WASHBASIN.NAME": '<link="WASHBASIN">حوض الغسيل</link>',
    "STRINGS.BUILDINGS.PREFABS.WASHBASIN.DESC": 'يمكن الحد من انتشار الجراثيم من خلال بناء هذه الأحواض في الأماكن التي يتسخ فيها المستنسخون غالباً.',
    "STRINGS.BUILDINGS.PREFABS.WASHBASIN.EFFECT": 'يزيل بعض <link="DISEASE">الجراثيم</link> من المستنسخين.\n\nيستخدم المستنسخون المغطون بالجراثيم أحواض الغسيل عند المرور بها في الاتجاه المحدد.',
    
    # 5. السرير البسيط (Cot)
    "STRINGS.BUILDINGS.PREFABS.BED.NAME": '<link="BED">سرير بسيط</link>',
    "STRINGS.BUILDINGS.PREFABS.BED.DESC": 'المستنسخون الذين ليس لديهم سرير سيعانون من آلام في الظهر بسبب النوم على الأرض.',
    "STRINGS.BUILDINGS.PREFABS.BED.EFFECT": 'يمنح مستنسخاً واحداً مكاناً للنوم.\n\nسيعود المستنسخون تلقائياً إلى أسرتهم البسيطة للنوم ليلاً.',
    
    # 6. محطة الأبحاث (Research Station)
    "STRINGS.BUILDINGS.PREFABS.RESEARCHCENTER.NAME": '<link="RESEARCHCENTER">محطة الأبحاث</link>',
    "STRINGS.BUILDINGS.PREFABS.RESEARCHCENTER.DESC": 'محطات الأبحاث ضرورية لفتح جميع مستويات البحث.',
    "STRINGS.BUILDINGS.PREFABS.RESEARCHCENTER.EFFECT": 'تجري <link="RESEARCH">الأبحاث المبتدئة</link> لفتح تقنيات جديدة.\n\nتستهلك <link="DIRT">التراب</link>.'
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
