import re

with open('django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим все блоки msgid/msgstr
pattern = r'(msgid\s+"[^"]*"(?:\n"[^"]*")*)\s*\n(msgstr\s+""(?:\n"[^"]*")+)'
matches = re.finditer(pattern, content, re.MULTILINE)

english_translations = []

for match in matches:
    msgid = match.group(1)
    msgstr = match.group(2)
    
    # Проверяем, содержит ли msgstr английский текст (начинается с заглавной латинской буквы)
    msgstr_lines = msgstr.split('\n')[1:]  # Пропускаем первую строку 'msgstr ""'
    
    for line in msgstr_lines:
        line = line.strip()
        if line.startswith('"') and len(line) > 2:
            text = line[1:-1] if line.endswith('"') else line[1:]
            # Проверяем, начинается ли с английской заглавной буквы
            if text and re.match(r'^[A-Z]', text) and not re.match(r'^[А-ЯЁ]', text):
                # Извлекаем msgid текст
                msgid_text = re.findall(r'"([^"]*)"', msgid)
                msgid_str = ' '.join(msgid_text)[:100]
                
                msgstr_text = re.findall(r'"([^"]*)"', msgstr)
                msgstr_str = ' '.join(msgstr_text)[:100]
                
                english_translations.append({
                    'msgid': msgid_str,
                    'msgstr': msgstr_str,
                    'full_msgid': msgid,
                    'full_msgstr': msgstr
                })
                break

print(f"Найдено {len(english_translations)} английских переводов\n")

# Показываем первые 20
for i, trans in enumerate(english_translations[:20], 1):
    print(f"{i}. ID: {trans['msgid'][:80]}")
    print(f"   EN: {trans['msgstr'][:80]}")
    print()
