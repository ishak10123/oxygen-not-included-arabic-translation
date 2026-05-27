import sys
import re

# تهيئة ترميز وحدة التحكم لتجنب أخطاء UnicodeEncodeError في الويندوز
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

def search_pot(query, filepath="strings_template.pot"):
    if not query:
        print("Please enter a search query.")
        return

    print(f"SEARCHING FOR: '{query}' in the original template file...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # استخدام التعبيرات المنتظمة (Regex) للبحث عن كتل النصوص
    pattern = re.compile(
        r'(#\.[^\n]*\nmsgctxt "([^"]+)"\nmsgid "((?:[^"\\]|\\.)*)"(?:\n"((?:[^"\\]|\\.)*)")*)',
        re.MULTILINE
    )
    
    matches = pattern.findall(content)
    
    results = []
    query_lower = query.lower()
    
    for match in matches:
        full_block = match[0]
        key = match[1]
        
        # دمج الأسطر المتعددة في النص الأصلي لرؤية الجملة كاملة
        msgid_parts = [match[2]]
        try:
            remaining = full_block.split('\nmsgid "')[1].split('\nmsgstr')[0]
            msgid_clean = "".join([line.strip('"') for line in remaining.split('\n')])
        except Exception:
            msgid_clean = match[2]
        
        # البحث في المفتاح أو النص الأصلي
        if query_lower in key.lower() or query_lower in msgid_clean.lower():
            results.append((key, msgid_clean, full_block))
            
    if not results:
        print("NO MATCHES FOUND.")
    else:
        print(f"FOUND {len(results)} MATCHING KEYS:\n")
        # عرض أول 15 نتيجة لتجنب ملء الشاشة
        for i, (key, text, block) in enumerate(results[:15], 1):
            print(f"--- MATCH {i} ---")
            print(f"KEY: {key}")
            print(f"ENGLISH TEXT: {text}")
            print(f"--------------------------------------------------")
            print(block)
            print(f"==================================================\n")
            
        if len(results) > 15:
            print(f"And {len(results) - 15} more matches found. Try narrowing your query.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        query = input("Enter the English text or key name to search: ")
    else:
        query = " ".join(sys.argv[1:])
        
    search_pot(query)
    # إبقاء الشاشة مفتوحة إذا تم تشغيله بالنقر المزدوج
    input("\nPress Enter to close...")
