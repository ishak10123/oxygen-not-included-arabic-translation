import polib

def main():
    po_path = r"c:\Users\ishak\Desktop\arabic_translation.po\strings\strings.po"
    po = polib.pofile(po_path, encoding='utf-8')
    
    # خريطة تعريب أسماء المستنسخين الـ 50 المعتمدة والمحسنة مع تطبيق وسم الحجم
    NAMES_MAP = {
        "ABE": "إبراهيم (أبو خليل)",
        "ADA": "هدى",
        "AMARI": "أميرة",
        "ARI": "علي",
        "ASHKAN": "أشرف",
        "BANHI": "بسمة",
        "BUBBLES": "بهيجة",
        "BURT": "بدر",
        "CAMILLE": "جميلة",
        "CATALINA": "كريمة",
        "CHIP": "شريف",
        "DEVON": "داوود",
        "EDWIREDO": "عادل",
        "ELLIE": "إلهام",
        "FRANKIE": "فريد",
        "FREYJA": "فريال",
        "GIZMO": "عزت",
        "GOSSMANN": "غسان",
        "HAROLD": "هادي",
        "HASSAN": "حسن",
        "HIGBY": "هاني",
        "JEAN": "جمال",
        "JORGE": "جورج",
        "JOSHUA": "يوسف",
        "LEIRA": "لارا",
        "LIAM": "ليث",
        "LINDSAY": "لميس",
        "MAE": "مي",
        "MARIE": "مريم",
        "MAX": "مازن",
        "MAYA": "ميساء",
        "MEEP": "مسعود",
        "MIMA": "ميادة",
        "NAILS": "نائل",
        "NIKOLA": "نادر",
        "NISBET": "نسيبة",
        "OTTO": "عطية",
        "PEI": "بهاء",
        "QUINN": "قاسم",
        "REN": "رائد",
        "ROWAN": "روان",
        "RUBY": "ربى",
        "SENA": "سناء",
        "SONYAR": "سونيا",
        "STEELA": "سلوى",
        "STEVE": "سعد",
        "STINKY": "حمدان",
        "TRAVALDO": "طارق",
        "TURNER": "تامر",
        "ULTI": "ألفت"
    }
    
    replaced_count = 0
    
    for entry in po:
        key = entry.msgctxt
        if key and key.startswith("STRINGS.DUPLICANTS.PERSONALITIES.") and key.endswith(".NAME"):
            parts = key.split('.')
            char_id = parts[-2]
            
            if char_id in NAMES_MAP:
                ar_name = NAMES_MAP[char_id]
                # تطبيق وسم الحجم 11 لتفادي الاقتصاص الرأسي في محرك اللعبة
                entry.msgstr = f"<size=11>{ar_name}</size>"
                replaced_count += 1
                
    po.save(po_path)
    print(f"Successfully applied size tags to all {replaced_count} duplicant names in strings.po!")

if __name__ == '__main__':
    main()
