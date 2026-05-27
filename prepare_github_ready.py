import os
import shutil

def main():
    repo_root = r"c:\Users\ishak\Desktop\arabic_translation.po"
    compiled_dir = os.path.join(repo_root, "arabic_translation_compiled")
    
    # 1. إنشاء المجلد الجاهز للتحميل المباشر
    os.makedirs(compiled_dir, exist_ok=True)
    os.makedirs(os.path.join(compiled_dir, "strings"), exist_ok=True)
    
    # 2. نسخ الملفات التعريفية وصورة الغلاف
    shutil.copy2(os.path.join(repo_root, "mod_info.yaml"), os.path.join(compiled_dir, "mod_info.yaml"))
    shutil.copy2(os.path.join(repo_root, "preview.png"), os.path.join(compiled_dir, "preview.png"))
    
    # 3. نسخ ملف الترجمة المترابط والمعكوس الجاهز للعب فوراً
    # سنقوم بجلب النسخة المعالجة والمربوطة من مجلد المود المحلي للعبة مباشرة
    home_dir = os.path.expanduser('~')
    game_po_path = os.path.join(home_dir, "Documents", "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings", "strings.po")
    
    dest_po_path = os.path.join(compiled_dir, "strings", "strings.po")
    
    if os.path.exists(game_po_path):
        shutil.copy2(game_po_path, dest_po_path)
        print("[SUCCESS] Copied compiled shaped strings.po to GitHub ready folder!")
    else:
        print("[WARNING] Could not find the compiled strings.po in game mod folder.")
        return
        
    # 4. كتابة دليل استخدام سريع ومبسط للاعبين داخل المجلد الجاهز باللغتين العربية والإنجليزية
    readme_content = """# 🎮 كيفية تركيب التعريب الجاهز يدوياً | How to Install the Arabic Mod Manually

مرحباً بك! هذا المجلد يحتوي على نسخة المود **المهيأة والمربوطة الجاهزة للعب فوراً** دون الحاجة لتشغيل أي سكربتات.

## 🇸🇦 طريقة التركيب بالعربية:
1. قم بتحميل هذا المجلد بالكامل باسم `arabic_translation_compiled`.
2. انسخ المجلد والملفات التي بداخله.
3. توجه إلى مسار مودات اللعبة في جهازك (غالباً في المستندات):
   `Documents\\Klei\\OxygenNotIncluded\\mods\\local\\`
4. قم بإنشاء مجلد جديد باسم `arabic_translation` (إذا لم يكن موجوداً).
5. الصق الملفات الثلاثة (`mod_info.yaml` و `preview.png` ومجلد `strings`) بداخل مجلد `arabic_translation`.
6. افتح اللعبة، اذهب إلى قائمة **Mods**، وقم بتفعيل المود واستمتع باللعب!

---

## 🇬🇧 How to Install in English:
1. Download this entire folder `arabic_translation_compiled`.
2. Go to your local Oxygen Not Included mods folder (usually in Documents):
   `Documents\\Klei\\OxygenNotIncluded\\mods\\local\\`
3. Create a new folder named `arabic_translation` (if it doesn't exist).
4. Paste the three files (`mod_info.yaml`, `preview.png`, and the `strings` folder) inside `arabic_translation`.
5. Open the game, go to **Mods**, enable it, and enjoy!
"""
    
    with open(os.path.join(compiled_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
        
    print("[SUCCESS] Created ready-made mod bundle and instruction README inside the repository!")

if __name__ == '__main__':
    main()
