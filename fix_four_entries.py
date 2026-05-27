import polib

FIX_MAP = {
    "STRINGS.UI.IMMIGRANTSCREEN.REJECTALL": "رفض الكل",
    "STRINGS.UI.FRONTEND.CUSTOMGAMESETTINGSSCREEN.SETTINGS.CALORIE_BURN.LEVELS.EASY.TOOLTIP": "يحرق المستنسخون السعرات الحرارية ببطء ويكتفون بوجبات أقل",
    "STRINGS.UI.FRONTEND.CUSTOMGAMESETTINGSSCREEN.SETTINGS.MORALE.LEVELS.HARD.NAME": "متطلب قليلاً",
    "STRINGS.UI.FRONTEND.CUSTOMGAMESETTINGSSCREEN.SETTINGS.RADIATION.LEVELS.EASIEST.NAME": "مضاد للقنابل"
}

def main():
    po_path = r"C:\Users\ishak\Desktop\arabic_translation.po\strings\strings.po"
    po = polib.pofile(po_path, encoding='utf-8')
    
    fixed_count = 0
    for entry in po:
        key = entry.msgctxt
        if key in FIX_MAP:
            entry.msgstr = FIX_MAP[key]
            fixed_count += 1
            print(f"FIXED [{key}] -> {FIX_MAP[key]}")
            
    po.save(po_path)
    print(f"Successfully fixed {fixed_count} entries!")

if __name__ == "__main__":
    main()
