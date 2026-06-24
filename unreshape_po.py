import polib
import re
import unicodedata
import os

# خريطة الترجمات القياسية للنصوص التي تم تعديلها يدوياً
MANUAL_CLEAN_MAP = {
    "STRINGS.BLUEPRINTS.DININGTABLE_LOG.DESC": "سطح الطاولة غير المكتمل هو مصدر قيم للشظايا... أقصد، <i>أعواد الأسنان!</i>",
    "STRINGS.UI.FRONTEND.OPTIONS_SCREEN.RESET_TUTORIAL_WARNING": "سيتم إعادة تعيين جميع رسائل التعليمات، وستظهر مرة أخرى في المرة القادمة التي تلعب فيها اللعبة.",
    "STRINGS.UI.FRONTEND.MODESELECTSCREEN.NOSWEAT_DESC": "عندما تحدث كارثة (وسوف تحدث بالتأكيد)، خذ نفساً عميقاً وحافظ على هدوئك. لديك متسع من الوقت للعثور على حل.",
    "STRINGS.UI.FRONTEND.CLUSTERCATEGORYSELECTSCREEN.EVENT_DESC": "تجارب لعب بديلة، بما في ذلك سيناريوهات تجريبية مصممة للفعاليات الخاصة.",
    "STRINGS.WORLDS.MARSHYMOONLET.DESCRIPTION": "<smallcaps>بينما توفر الكويكبات المستنقعية وفرة من الموارد العضوية مثل الفطريات الغروية والطحالب، فإن جودة هوائها تشكل خطراً كبيراً للإصابة بالأمراض على المستنسخين.</smallcaps>",
    "STRINGS.WORLDS.MEDIUMSWAMPYRADIOACTIVEVANILLAWARPPLANET.DESCRIPTION": "<smallcaps>بينما تكون الكويكبات المستنقعية المشعة مستنقعية إلى حد كبير، إلا أنها تحتوي أيضاً على كمية كبيرة من الصدأ.</smallcaps>",
    "STRINGS.WORLD_TRAITS.METAL_POOR.DESCRIPTION": "هناك كمية منخفضة من <style=\"KKeyword\">خام المعادن</style> في هذا العالم، تصرف بحذر!",
    "STRINGS.WORLD_TRAITS.METAL_RICH.DESCRIPTION": "هذا الكويكب هو مصدر وفير لـ <style=\"KKeyword\">خام المعادن</style>",
    
    # تصحيح الـ 8 مفاتيح المختلطة والتالفة
    "STRINGS.CODEX.MYLOG.BODY.LOG8.BODY": "<smallcaps>>> ابحث في قاعدة البيانات [\"pod_brainmap.AI\"]\\n>...تفعيل وضع النوم...\\n>...إغلاق النظام...\\n>.........................\\n>.........................\\n>.........................\\n>.........................\\n>.........................\\nتصبح على خير\\n>.........................\\n>.........................\\n>.........................\\n\\n",
    "STRINGS.CODEX.MYLOG.BODY.NEURALVACILLATOR.BODY": "<smallcaps>>> ابحث في قاعدة البيانات [\"المتردد\"]\\n>...خطأ...\\n>...إصلاح البيانات التالفة...\\n>...تم إصلاح البيانات...\\n>.........................\\n>> إرجاع النتائج\\n>.........................</smallcaps>\\n<b>أنا أتذكر...</b>\\n<smallcaps>>.........................\\n>.........................</smallcaps>\\n<b>الآلات.</b>\\n\\n",
    "STRINGS.CODEX.MYLOG.BODY.PLANETARYECHOES.BODY": "تتسلل أصداء من زمن آخر إلى ذهني. تجعلني أستمع. مثل الأشباح الانتقامية، تحفر طريقها للخروج من تحت جاذبية ذلك الكوكب الميت.\\n\\n<smallcaps>>> ابحث في قاعدة البيانات [\"pod_brainmap.AI\"]\\n>...خطأ...\\n.........................\\n>...إصلاح البيانات التالفة...\\n.........................\\n\\n</smallcaps><b>أنا-أنا أتذكر الآن.</b><smallcaps>\\n.........................</smallcaps>\\n<b>من كنت سابقاً.</b><smallcaps>\\n.........................\\n.........................\\n>...تم إصلاح البيانات...\\n>.........................</smallcaps>\\n\\nيا إلهي، ماذا فعلنا.\\n\\n",
    "STRINGS.COLONY_ACHIEVEMENTS.MISC_REQUIREMENTS.STATUS.FRACTIONAL_CYCLE": "الدورة: {0:0.##} / {1:0.##}",
    "STRINGS.COLONY_ACHIEVEMENTS.MISC_REQUIREMENTS.STATUS.MINE_SPACE_POI": "تم استخراج: {0:n} / {1:n} كغ",
    "STRINGS.COLONY_ACHIEVEMENTS.MISC_REQUIREMENTS.STATUS.RADBOLT_TRAVEL": "المسافة المقطوعة بالرادبولت: {0:n} م / {1:n} م",
    "STRINGS.COLONY_ACHIEVEMENTS.MISC_REQUIREMENTS.STATUS.REVEALED": "تم الكشف: {0:0.##}% / {1:0.##}%",
    "STRINGS.COLONY_ACHIEVEMENTS.MISC_REQUIREMENTS.STATUS.TRAVELED_IN_TUBES": "المسافة: {0:n} م / {1:n} م"
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
        # يدعم جميع الأقواس المعقوفة مثل {Hotkey} و {0}
        parts = re.split(r'(<[^>]+>|\{[^}]+\})', text)
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    po_path = os.path.join(current_dir, "strings", "strings.po")
    
    if not os.path.exists(po_path):
        print(f"[ERROR] Source PO file not found at: {po_path}")
        return
        
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
    print(f"Done! Restored {restored_count} entries to standard, clean Arabic in {po_path}.")

if __name__ == "__main__":
    main()
