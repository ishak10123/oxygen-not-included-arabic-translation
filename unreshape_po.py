import polib
import re
import unicodedata

# خريطة الترجمات القياسية للنصوص التي تم تعديلها يدوياً
MANUAL_CLEAN_MAP = {
    "STRINGS.BLUEPRINTS.DININGTABLE_LOG.DESC": "سطح الطاولة غير المكتمل هو مصدر قيم للشظايا... أقصد، <i>أعواد الأسنان!</i>",
    "STRINGS.UI.FRONTEND.OPTIONS_SCREEN.RESET_TUTORIAL_WARNING": "سيتم إعادة تعيين جميع رسائل التعليمات، وستظهر مرة أخرى في المرة القادمة التي تلعب فيها اللعبة.",
    "STRINGS.UI.FRONTEND.MODESELECTSCREEN.NOSWEAT_DESC": "عندما تحدث كارثة (وسوف تحدث بالتأكيد)، خذ نفساً عميقاً وحافظ على هدوئك. لديك متسع من الوقت للعثور على حل.",
    "STRINGS.UI.FRONTEND.CLUSTERCATEGORYSELECTSCREEN.EVENT_DESC": "تجارب لعب بديلة، بما في ذلك سيناريوهات تجريبية مصممة للفعاليات الخاصة.",
    "STRINGS.WORLDS.MARSHYMOONLET.DESCRIPTION": "<smallcaps>بينما توفر الكويكبات المستنقعية وفرة من الموارد العضوية مثل الفطريات الغروية والطحالب، فإن جودة هوائها تشكل خطراً كبيراً للإصابة بالأمراض على المستنسخين.</smallcaps>",
    "STRINGS.WORLDS.MEDIUMSWAMPYRADIOACTIVEVANILLAWARPPLANET.DESCRIPTION": "<smallcaps>بينما تكون الكويكبات المستنقعية المشعة مستنقعية إلى حد كبير، إلا أنها تحتوي أيضاً على كمية كبيرة من الصدأ.</smallcaps>",
    "STRINGS.WORLD_TRAITS.METAL_POOR.DESCRIPTION": "هناك كمية منخفضة من <style=\"KKeyword\">خام المعادن</style> في هذا العالم، تصرف بحذر!",
    "STRINGS.WORLD_TRAITS.METAL_RICH.DESCRIPTION": "هذا الكويكب هو مصدر وفير لـ <style=\"KKeyword\">خام المعادن</style>"
}

def contains_presentation_forms(text):
    for char in text:
        cp = ord(char)
        if (0xFB50 <= cp <= 0xFDFF) or (0xFE70 <= cp <= 0xFEFF):
            return True
    return False

def restore_string(text):
    if not text:
        return text
        
    # تفكيك الحروف وإعادتها لترميزها القياسي (U+0600 - U+06FF)
    normalized = unicodedata.normalize('NFKC', text)
    
    # إذا كانت النصوص تحتوي على الحروف المتصلة (Presentation Forms) فهذا يعني أنها كانت مقلوبة ويجب عكسها لتصحيح الترتيب
    if contains_presentation_forms(text):
        parts = re.split(r'(<[^>]+>|\{[0-9]+\})', text)
        fixed_parts = []
        for part in parts:
            if (part.startswith('<') and part.endswith('>')) or (part.startswith('{') and part.endswith('}')):
                fixed_parts.append(part)
            else:
                norm_part = unicodedata.normalize('NFKC', part)
                fixed_parts.append(norm_part[::-1])
        return "".join(fixed_parts)
        
    return normalized

def main():
    po_path = r"C:\Users\ishak\Desktop\arabic_translation.po\strings\strings.po"
    po = polib.pofile(po_path, encoding='utf-8')
    
    restored_count = 0
    for entry in po:
        if entry.msgstr:
            key = entry.msgctxt
            if key in MANUAL_CLEAN_MAP:
                entry.msgstr = MANUAL_CLEAN_MAP[key]
                restored_count += 1
            elif contains_presentation_forms(entry.msgstr):
                entry.msgstr = restore_string(entry.msgstr)
                restored_count += 1
            else:
                # التأكد من تنظيف أي حروف عرض متبقية
                entry.msgstr = unicodedata.normalize('NFKC', entry.msgstr)
                
    po.save(po_path)
    print(f"Done! Restored {restored_count} entries to standard, clean Arabic in your desktop strings.po file.")

if __name__ == "__main__":
    main()
