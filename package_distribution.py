import os
import zipfile
import re
import sys

def get_mod_version(mod_info_path):
    if os.path.exists(mod_info_path):
        try:
            with open(mod_info_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'version:\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        except Exception:
            pass
    return "1.0.0"

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_mod_dir = os.path.join(current_dir, "arabic_translation")
    install_script_path = os.path.join(current_dir, "install_mod.py")
    mod_info_path = os.path.join(source_mod_dir, "mod_info.yaml")
    
    if not os.path.exists(source_mod_dir):
        print(f"[ERROR] Source mod directory not found: {source_mod_dir}")
        sys.exit(1)
        
    if not os.path.exists(install_script_path):
        print(f"[ERROR] Install script not found: {install_script_path}")
        sys.exit(1)
        
    version = get_mod_version(mod_info_path)
    zip_filename = f"arabic_translation_release_v{version}.zip"
    zip_filepath = os.path.join(current_dir, zip_filename)
    
    print("=" * 60)
    print("Oxygen Not Included - Release Packager")
    print("=" * 60)
    print(f"Packaging mod folder: {source_mod_dir}")
    print(f"Packaging script: {install_script_path}")
    print(f"Output Release ZIP: {zip_filepath}")
    print("-" * 60)
    
    try:
        # حذف الملف المضغوط القديم إذا كان موجوداً
        if os.path.exists(zip_filepath):
            print("[INFO] Removing old zip file...")
            os.remove(zip_filepath)
            
        print("[PACKAGING] Creating zip file and adding files...")
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. إضافة سكربت التنصيب
            zipf.write(install_script_path, "install_mod.py")
            
            # 2. إضافة مجلد arabic_translation ومحتوياته بشكل تكراري
            for root, dirs, files in os.walk(source_mod_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # حساب المسار النسبي للحفاظ على بنية المجلدات بداخل الملف المضغوط
                    rel_path = os.path.relpath(file_path, current_dir)
                    zipf.write(file_path, rel_path)
                    
        print("=" * 60)
        print("[SUCCESS] Release package created successfully!")
        print(f"[SUCCESS] Zip file: {zip_filename}")
        print("=" * 60)
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to create release package: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
