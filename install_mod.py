import os
import shutil
import sys

def get_windows_documents_path():
    """الاستعلام عن مسار مجلد المستندات الفعلي والنشط من سجل نظام ويندوز لدعم المجلدات الموجهة أو OneDrive"""
    if sys.platform.startswith('win'):
        try:
            import winreg
            # فتح مفتاح سجل النظام الخاص بمجلدات شل للمستخدم
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                # القيمة "Personal" تحتوي على مسار مجلد المستندات
                personal_path, _ = winreg.QueryValueEx(key, "Personal")
            # فك المتغيرات البيئية مثل %USERPROFILE% إن وجدت
            return os.path.expandvars(personal_path)
        except Exception as e:
            print(f"[WARN] Failed to query registry for Documents folder: {e}. Falling back to default.")
    
    # ملجأ احتياطي في حال فشل الاستعلام أو تشغيله على نظام غير ويندوز
    return os.path.join(os.path.expanduser('~'), "Documents")

def main():
    # 1. تحديد مسار مجلد المود في المشروع الحالي
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_mod_dir = os.path.join(current_dir, "arabic_translation")
    
    if not os.path.exists(source_mod_dir):
        print(f"[ERROR] Source mod directory not found: {source_mod_dir}")
        print("Please make sure the 'arabic_translation' folder exists in the project root.")
        sys.exit(1)
        
    # 2. تحديد مسار المستندات الفعلي للعبة
    documents_dir = get_windows_documents_path()
    target_local_dir = os.path.join(documents_dir, "Klei", "OxygenNotIncluded", "mods", "local")
    target_mod_dir = os.path.join(target_local_dir, "arabic_translation")
    
    print("=" * 60)
    print("Oxygen Not Included - Arabic Translation Installer")
    print("=" * 60)
    print(f"Source: {source_mod_dir}")
    print(f"Destination: {target_mod_dir}")
    print("-" * 60)
    
    try:
        # إنشاء مجلد local إذا لم يكن موجوداً
        os.makedirs(target_local_dir, exist_ok=True)
        
        # إذا كان المجلد القديم موجوداً، نقوم بحذفه أولاً لضمان تثبيت نظيف
        if os.path.exists(target_mod_dir):
            print("[INFO] Removing old version of the mod from game directory...")
            shutil.rmtree(target_mod_dir)
            
        # نسخ المجلد بالكامل
        print("[INSTALL] Copying translation files to local mods...")
        shutil.copytree(source_mod_dir, target_mod_dir)
        
        print("=" * 60)
        print("[SUCCESS] Mod installed successfully!")
        print("[SUCCESS] You can now open the game, go to 'Mods', and enable 'Arabic Translation'.")
        print("=" * 60)
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to install mod: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
