import os
import sys
import re
import json
import time
import shutil
import concurrent.futures
import polib
import arabic_reshaper
import unicodedata
from bidi.algorithm import get_display
import translators as ts

# 1. تهيئة برنامج إعادة تشكيل الحروف العربية بنفس تكوين اللعبة
reshaper = arabic_reshaper.ArabicReshaper(
    arabic_reshaper.config_for_true_type_font(
        "C:\\Windows\\Fonts\\arial.ttf",
        arabic_reshaper.ENABLE_ALL_LIGATURES
    )
)

def contains_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

# دالة ذكية لإصلاح المسافات الزائدة التي قد يضيفها محرك الترجمة داخل الوسوم والمتغيرات
def repair_translated_tags(text):
    if not text:
        return text
    text = re.sub(r'\{\s*([0-9]+)\s*\}', r'{\1}', text)
    text = re.sub(r'</\s*([a-zA-Z]+)\s*>', r'</\1>', text)
    def clean_tag(match):
        tag_content = match.group(1)
        tag_content = re.sub(r'\s*=\s*', '=', tag_content)
        tag_content = re.sub(r'=\s*"([^"]*)"', r'="\1"', tag_content)
        tag_content = tag_content.strip()
        if tag_content.startswith('/ '):
            tag_content = '/' + tag_content[2:]
        return f"<{tag_content}>"
        
    text = re.sub(r'<\s*([^>]+)\s*>', clean_tag, text)
    return text

# دالة إعادة التشكيل والعكس المتوافقة مع Unity
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

# دالة إرسال الترجمة مع فرض وقت استجابة صارم (Timeout) لمنع تعليق السكربت نهائياً
def translate_text_with_timeout(text, engine, target_lang, source_lang, timeout=8):
    # تشغيل الترجمة في مسار مستقل (Thread) لفرض وقت انتهاء صارم ومتوافق مع ويندوز
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            ts.translate_text, 
            text, 
            translator=engine, 
            from_language=source_lang, 
            to_language=target_lang
        )
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"\n[TIMEOUT] Engine '{engine}' timed out after {timeout} seconds.", flush=True)
            return None
        except Exception as e:
            # معالجة الأخطاء الشائعة مثل الحظر بصمت دون تعليق السكربت
            if "429" in str(e):
                print(f"\n[RATE LIMIT] Engine '{engine}' blocked us (429).", flush=True)
            return None

# المحرك الثلاثي الخارق والآمن للترجمة للغة العربية يدوياً بدون مفاتيح وبشكل مضاد للحظر والتعليق
def robust_translate(text, target_lang="ar", source_lang="en"):
    if not text or not text.strip():
        return text
    if contains_arabic(text):
        return text
        
    # محركات الترجمة الثلاثية (Bing هو الأقوى، ثم Google الذكي، ثم Alibaba كاحتياط)
    engines = ["bing", "google", "alibaba"]
    
    for engine in engines:
        res = translate_text_with_timeout(text, engine, target_lang, source_lang, timeout=8)
        if res and contains_arabic(res):
            return repair_translated_tags(res)
            
    return None

def safe_save_json(data, file_path):
    """حفظ ملف JSON بشكل ذري وآمن لتفادي مشاكل انقطاع الكهرباء"""
    temp_path = file_path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"\n[ERROR] Failed writing JSON to temp file: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False

    # محاولة الاستبدال الذري مع إعادة المحاولة لتجنب أقفال ويندوز المؤقتة
    for attempt in range(5):
        try:
            os.replace(temp_path, file_path)
            return True
        except PermissionError:
            time.sleep(0.2)
        except Exception as e:
            print(f"\n[ERROR] Atomic rename failed: {e}")
            break
            
    # إذا فشل الاستبدال الذري بعد المحاولات، نقوم بالحفظ العادي كملجأ أخير لمنع ضياع البيانات
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n[WARN] Atomic save failed, fell back to direct JSON save.")
        return True
    except Exception as e:
        print(f"\n[CRITICAL] Fallback JSON save also failed: {e}")
        return False

def safe_save_po(po_obj, file_path):
    """حفظ ملف PO بشكل ذري وآمن لتفادي مشاكل انقطاع الكهرباء"""
    temp_path = file_path + ".tmp"
    try:
        po_obj.save(temp_path)
        # إجبار نظام التشغيل على حفظ التغييرات المؤقتة على القرص
        if os.path.exists(temp_path):
            with open(temp_path, "a") as f:
                f.flush()
                os.fsync(f.fileno())
    except Exception as e:
        print(f"\n[ERROR] Failed writing PO to temp file: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False

    # محاولة الاستبدال الذري مع إعادة المحاولة لتجنب أقفال ويندوز المؤقتة
    for attempt in range(5):
        try:
            os.replace(temp_path, file_path)
            return True
        except PermissionError:
            time.sleep(0.2)
        except Exception as e:
            print(f"\n[ERROR] Atomic rename failed: {e}")
            break
            
    # ملجأ أخير
    try:
        po_obj.save(file_path)
        print(f"\n[WARN] Atomic save failed, fell back to direct PO save.")
        return True
    except Exception as e:
        print(f"\n[CRITICAL] Fallback PO save also failed: {e}")
        return False

def main():
    if sys.platform.startswith('win'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

    workspace_dir = r"c:\Users\ishak\Desktop\arabic_translation.po"
    desktop_po_path = os.path.join(workspace_dir, "strings", "strings.po")
    template_pot_path = os.path.join(workspace_dir, "strings_template.pot")
    cache_path = os.path.join(workspace_dir, "translation_cache.json")
    
    print("=" * 60)
    print("🤖 Oxygen Not Included 100% Arabic Translation Tool (ANTI-HANG)")
    print("=" * 60)
    
    # 1. تحميل الذاكرة المؤقتة (Cache)
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as cf:
                cache = json.load(cf)
            print(f"[CACHE] Loaded {len(cache)} cached translations.")
        except Exception as ce:
            print(f"[CACHE WARNING] Could not load cache: {ce}. Starting fresh cache.")
            
    # 2. تحميل ملف قالب اللعبة الأصلي
    print("[POT] Loading strings_template.pot... (This might take a few seconds)")
    try:
        template = polib.pofile(template_pot_path, encoding='utf-8')
        print(f"[POT] Loaded {len(template)} total strings from template.")
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to load POT template: {e}")
        return

    # 3. تحميل ملف الترجمة الحالي
    print("[PO] Loading desktop strings.po...")
    po_existed = os.path.exists(desktop_po_path)
    if po_existed:
        try:
            po = polib.pofile(desktop_po_path, encoding='utf-8')
            print(f"[PO] Loaded existing strings.po with {len(po)} entries.")
        except Exception as e:
            print(f"[PO WARNING] Failed to load strings.po: {e}. Creating a new one.")
            po = polib.POFile()
            po.metadata = {
                'Language': 'ar',
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit'
            }
    else:
        po = polib.POFile()
        po.metadata = {
            'Language': 'ar',
            'Content-Type': 'text/plain; charset=UTF-8',
            'Content-Transfer-Encoding': '8bit'
        }

    # 4. حماية التعريبات اليدوية السابقة
    manual_translations = {}
    for entry in po:
        if entry.msgctxt and entry.msgstr:
            manual_translations[entry.msgctxt] = entry.msgstr
            
    print(f"[PROTECT] Protected {len(manual_translations)} manual/existing translations.")

    existing_po_entries = {entry.msgctxt: entry for entry in po if entry.msgctxt}

    # 5. تجميع المدخلات المتبقية التي تحتاج إلى ترجمة
    translation_queue = []
    for entry in template:
        if not entry.msgctxt:
            continue
        if entry.msgctxt in manual_translations:
            continue
        original_text = entry.msgid
        if not original_text or not original_text.strip():
            continue
        translation_queue.append(entry)

    total_to_translate = len(translation_queue)
    print(f"[QUEUE] Found {total_to_translate} entries to translate out of {len(template)} total strings.")
    
    limit = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=")[1])
                print(f"[DRY-RUN] Limit set to {limit} translations.")
            except ValueError:
                pass

    if total_to_translate == 0:
        print("[SUCCESS] All strings are already translated! Saving final outputs...")
    else:
        print("[TRANSLATE] Starting triple-engine translation loop. Anti-Hang Enabled.")
        print("Press Ctrl+C at any time to safely stop and save progress.")
        print("-" * 60)
        
        translated_count = 0
        unsaved_live_translations = 0
        unsaved_cached_translations = 0
        
        try:
            for idx, entry in enumerate(translation_queue, 1):
                if limit and translated_count >= limit:
                    print(f"\n[DRY-RUN] Reached dry-run limit of {limit} translations. Stopping.")
                    break
                    
                key = entry.msgctxt
                english_text = entry.msgid
                
                arabic_trans = None
                
                # أ. التحقق من الكاش أولاً
                if english_text in cache:
                    arabic_trans = cache[english_text]
                    unsaved_cached_translations += 1
                elif not re.search(r'[a-zA-Z]', english_text):
                    # إذا كان النص لا يحتوي على أي حروف إنجليزية (مثل رموز أو أرقام فقط مثل "{0}"), فلا يحتاج لترجمة
                    arabic_trans = english_text
                    cache[english_text] = arabic_trans
                    unsaved_live_translations += 1
                else:
                    # ب. الترجمة عبر المحرك الثلاثي الذكي
                    # حلقة متكررة مع حد أقصى للمحاولات لمنع التعليق اللانهائي
                    attempt = 1
                    sleep_time = 15.0
                    max_attempts = 3
                    while not arabic_trans and attempt <= max_attempts:
                        arabic_trans = robust_translate(english_text)
                        if arabic_trans:
                            break
                        else:
                            print(f"\n[BLOCK] All 3 engines blocked or timed out. Attempt {attempt}/{max_attempts}. Waiting {sleep_time}s for: '{english_text[:20]}...'")
                            time.sleep(sleep_time)
                            attempt += 1
                            sleep_time = min(sleep_time + 15.0, 90.0)
                    
                    if not arabic_trans:
                        print(f"\n[SKIP] Could not translate '{english_text[:20]}' after {max_attempts} attempts. Skipping to prevent permanent hang.")
                        continue  # تخطي هذا العنصر في هذه الدورة دون التسبب في تعليق السكربت
                        
                    # حفظ في الكاش
                    cache[english_text] = arabic_trans
                    unsaved_live_translations += 1
                    
                    # تأخير زمني خفيف لعدم إجهاد الشبكة (0.5 ثانية)
                    time.sleep(0.5)
                
                # ج. التشكيل والعكس لـ Unity
                processed_arabic = fix_arabic_text(arabic_trans)
                
                # د. حفظ الترجمة في ملف PO
                if key in existing_po_entries:
                    existing_po_entries[key].msgstr = processed_arabic
                else:
                    new_entry = polib.POEntry(msgid=english_text, msgstr=processed_arabic, msgctxt=key)
                    po.append(new_entry)
                    existing_po_entries[key] = new_entry
                
                translated_count += 1
                
                # هـ. طباعة التقدم
                progress_pct = (idx / total_to_translate) * 100
                sys.stdout.write(f"\rProgress: {progress_pct:.2f}% ({idx}/{total_to_translate}) | Translated: {translated_count}")
                sys.stdout.flush()
                
                # و. حفظ ذري وآمن بذكاء لتفادي إرهاق الهارد ديسك وتجنب التلف:
                # 1. إذا كانت هناك ترجمة حية جديدة (مهمة وبطيئة): نحفظ فوراً
                # 2. إذا كانت الترجمات من الكاش: نحفظ على دفعات كل 50 ترجمة لتسريع السكربت 1000%
                if unsaved_live_translations > 0 or unsaved_cached_translations >= 50:
                    safe_save_json(cache, cache_path)
                    safe_save_po(po, desktop_po_path)
                    unsaved_live_translations = 0
                    unsaved_cached_translations = 0
                    
        except KeyboardInterrupt:
            print("\n\n[PAUSED] Translation paused by user (Ctrl+C). Saving progress...")
        
        # حفظ نهائي للكاش
        with open(cache_path, "w", encoding="utf-8") as cf:
            json.dump(cache, cf, ensure_ascii=False, indent=4)
        print(f"\n[CACHE] Successfully saved translation cache of {len(cache)} strings.")

    # 7. حفظ ملف PO النهائي على سطح المكتب
    print("[PO] Saving final strings.po to desktop...")
    po.save(desktop_po_path)
    print(f"[PO] Successfully saved strings.po ({len(po)} total entries).")
    
    # 8. نسخ الملف المعالج مباشرة إلى مجلد مودات اللعبة
    home_dir = os.path.expanduser('~')
    game_mod_dir = os.path.join(home_dir, "Documents", "Klei", "OxygenNotIncluded", "mods", "local", "arabic_translation", "strings")
    game_po_path = os.path.join(game_mod_dir, "strings.po")
    
    try:
        os.makedirs(game_mod_dir, exist_ok=True)
        shutil.copy(desktop_po_path, game_po_path)
        print("=" * 60)
        print("[SUCCESS] All done!")
        print(f"[SUCCESS] Saved to desktop: {desktop_po_path}")
        print(f"[SUCCESS] Copied to game mod directory: {game_po_path}")
        print("=" * 60)
    except Exception as mod_err:
        print(f"[ERROR] Could not copy PO file to game mod folder: {mod_err}")

if __name__ == "__main__":
    main()
