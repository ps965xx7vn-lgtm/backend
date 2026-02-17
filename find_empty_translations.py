#!/usr/bin/env python3
"""Find empty translations in django.po"""

PO_FILE = "src/locale/ka/LC_MESSAGES/django.po"

with open(PO_FILE, encoding="utf-8") as f:
    lines = f.readlines()

print("🔍 Checking for empty translations in legal pages...\n")

in_legal = False
msgid_text = []
line_num = 0
empty_translations = []

for i, line in enumerate(lines, 1):
    # Check if we're in a legal page context
    if "refund-policy.html" in line or "terms-of-service.html" in line or "404.html" in line:
        in_legal = True
        context_line = line.strip()
        line_num = i

    if in_legal:
        if line.startswith("msgid"):
            # Start collecting msgid
            msgid_text = [line.strip()[7:-1]]  # Remove msgid " and "
        elif line.startswith('"') and not line.startswith("msgstr"):
            # Continue multiline msgid
            msgid_text.append(line.strip()[1:-1])
        elif 'msgstr ""' in line and len(msgid_text) > 0:
            # Found empty translation
            full_msgid = " ".join(msgid_text)
            if full_msgid:
                empty_translations.append(
                    {
                        "line": line_num,
                        "msgid": full_msgid[:80] + ("..." if len(full_msgid) > 80 else ""),
                        "full_msgid": " ".join(msgid_text),
                    }
                )
            in_legal = False
            msgid_text = []
        elif line.startswith("msgstr") and 'msgstr ""' not in line:
            # Has translation, reset
            in_legal = False
            msgid_text = []

print(f"Found {len(empty_translations)} empty translations:\n")
for trans in empty_translations[:20]:
    print(f"Line {trans['line']}: {trans['msgid']}")
