#!/usr/bin/env python3
"""
Скрипт для обновления переводов в файлах django.po
Обновляет переводы для страниц сертификатов и terms of service
"""

TRANSLATIONS = {
    # Certificate verification translations
    "Верификация сертификата": {"ka": "სერტიფიკატის ვერიფიკაცია", "en": "Certificate Verification"},
    "Верификация": {"ka": "ვერიფიკაცია", "en": "Verification"},
    "Проверка подлинности сертификата": {
        "ka": "სერტიფიკატის ნამდვილობის გადამოწმება",
        "en": "Certificate Authenticity Verification",
    },
    "Убедитесь в подлинности сертификата PyLand. Введите код верификации или номер сертификата для мгновенной проверки.": {
        "ka": "დარწმუნდით PyLand-ის სერტიფიკატის ნამდვილობაში. შეიყვანეთ ვერიფიკაციის კოდი ან სერტიფიკატის ნომერი მყისიერი შემოწმებისთვის.",
        "en": "Verify the authenticity of PyLand certificate. Enter the verification code or certificate number for instant verification.",
    },
    "Введите данные для проверки": {
        "ka": "შეიყვანეთ მონაცემები შემოწმებისთვის",
        "en": "Enter data for verification",
    },
    "Код верификации или номер сертификата": {
        "ka": "ვერიფიკაციის კოდი ან სერტიფიკატის ნომერი",
        "en": "Verification code or certificate number",
    },
    "Например: 30B432450602 или CERT-20260203-A3F9": {
        "ka": "მაგალითად: 30B432450602 ან CERT-20260203-A3F9",
        "en": "For example: 30B432450602 or CERT-20260203-A3F9",
    },
    "Проверить сертификат": {"ka": "შეამოწმეთ სერტიფიკატი", "en": "Verify Certificate"},
    "Сертификат действителен": {"ka": "სერტიფიკატი მოქმედია", "en": "Certificate is Valid"},
    "Номер сертификата": {"ka": "სერტიფიკატის ნომერი", "en": "Certificate Number"},
    "Дата завершения": {"ka": "დასრულების თარიღი", "en": "Completion Date"},
    "Дата выдачи": {"ka": "გაცემის თარიღი", "en": "Issue Date"},
    "Код верификации": {"ka": "ვერიფიკაციის კოდი", "en": "Verification Code"},
    "Посмотреть полную информацию": {
        "ka": "სრული ინფორმაციის ნახვა",
        "en": "View Full Information",
    },
    "Этот сертификат был выдан официально платформой PyLand и подтверждает успешное завершение курса.": {
        "ka": "ეს სერტიფიკატი გაიცა ოფიციალურად PyLand პლატფორმის მიერ და ადასტურებს კურსის წარმატებით დასრულებას.",
        "en": "This certificate was officially issued by PyLand platform and confirms successful course completion.",
    },
    "Сертификат отозван": {"ka": "სერტიფიკატი გაუქმებულია", "en": "Certificate Revoked"},
    "Дата отзыва": {"ka": "გაუქმების თარიღი", "en": "Revocation Date"},
    "Причина": {"ka": "მიზეზი", "en": "Reason"},
    "Этот сертификат был отозван и более не является действительным.": {
        "ka": "ეს სერტიფიკატი გაუქმდა და აღარ არის მოქმედი.",
        "en": "This certificate has been revoked and is no longer valid.",
    },
    "Сертификат не найден": {"ka": "სერტიფიკატი ვერ მოიძებნა", "en": "Certificate Not Found"},
    "Сертификат с указанным кодом или номером не существует в нашей базе данных. Пожалуйста, проверьте правильность введенных данных.": {
        "ka": "სერტიფიკატი მითითებული კოდით ან ნომრით არ არსებობს ჩვენს მონაცემთა ბაზაში. გთხოვთ შეამოწმოთ შეყვანილი მონაცემების სისწორე.",
        "en": "Certificate with the specified code or number does not exist in our database. Please check the correctness of the entered data.",
    },
    "Как проверить сертификат?": {
        "ka": "როგორ შევამოწმოთ სერტიფიკატი?",
        "en": "How to verify a certificate?",
    },
    "Вы можете проверить подлинность сертификата, используя:": {
        "ka": "შეგიძლიათ შეამოწმოთ სერტიფიკატის ნამდვილობა გამოყენებით:",
        "en": "You can verify certificate authenticity using:",
    },
    "(12 символов, например: 30B432450602)": {
        "ka": "(12 სიმბოლო, მაგალითად: 30B432450602)",
        "en": "(12 characters, for example: 30B432450602)",
    },
    "(например: CERT-20260203-A3F9)": {
        "ka": "(მაგალითად: CERT-20260203-A3F9)",
        "en": "(for example: CERT-20260203-A3F9)",
    },
    "Оба значения указаны в выданном сертификате и могут быть найдены на странице детального просмотра сертификата.": {
        "ka": "ორივე მნიშვნელობა მითითებულია გაცემულ სერტიფიკატში და შეიძლება ნახოთ სერტიფიკატის დეტალური ხედვის გვერდზე.",
        "en": "Both values are indicated on the issued certificate and can be found on the certificate details page.",
    },
    "Проверьте подлинность сертификата Pyland": {
        "ka": "შეამოწმეთ Pyland სერტიფიკატის ნამდვილობა",
        "en": "Verify Pyland certificate authenticity",
    },
    "Номер сертификата или код верификации": {
        "ka": "სერტიფიკატის ნომერი ან ვერიფიკაციის კოდი",
        "en": "Certificate number or verification code",
    },
    "Например: CERT-20260126-0001 или ABC123XYZ": {
        "ka": "მაგალითად: CERT-20260126-0001 ან ABC123XYZ",
        "en": "For example: CERT-20260126-0001 or ABC123XYZ",
    },
    "Сертификат подлинный и действителен": {
        "ka": "სერტიფიკატი ავთენტურია და მოქმედია",
        "en": "Certificate is authentic and valid",
    },
    "Номер сертификата:": {"ka": "სერტიფიკატის ნომერი:", "en": "Certificate number:"},
    "Код верификации:": {"ka": "ვერიფიკაციის კოდი:", "en": "Verification code:"},
    "Студент:": {"ka": "სტუდენტი:", "en": "Student:"},
    "Курс:": {"ka": "კურსი:", "en": "Course:"},
    "Дата выдачи:": {"ka": "გაცემის თარიღი:", "en": "Issue date:"},
    "Уроков завершено:": {"ka": "დასრულებული გაკვეთილები:", "en": "Lessons completed:"},
    "Получено проверок:": {"ka": "მიღებული შემოწმებები:", "en": "Reviews received:"},
    "Итоговая оценка:": {"ka": "საბოლოო შეფასება:", "en": "Final grade:"},
    "Причина отзыва:": {"ka": "გაუქმების მიზეზი:", "en": "Revocation reason:"},
    "Этот сертификат был выдан официально платформой Pyland и подтверждает успешное завершение курса.": {
        "ka": "ეს სერტიფიკატი გაიცა ოფიციალურად Pyland პლატფორმის მიერ და ადასტურებს კურსის წარმატებით დასრულებას.",
        "en": "This certificate was officially issued by Pyland platform and confirms successful course completion.",
    },
    "Как это работает?": {"ka": "როგორ მუშაობს ეს?", "en": "How does it work?"},
    "Каждый сертификат Pyland имеет уникальный номер и код верификации. Вы можете использовать любой из них для проверки подлинности.": {
        "ka": "ყოველ Pyland სერტიფიკატს აქვს უნიკალური ნომერი და ვერიფიკაციის კოდი. შეგიძლიათ გამოიყენოთ რომელიმე მათგანი ნამდვილობის შესამოწმებლად.",
        "en": "Each Pyland certificate has a unique number and verification code. You can use either of them to verify authenticity.",
    },
    "Если у вас возникли вопросы, напишите нам: pylandschool@gmail.com": {
        "ka": "თუ თქვენ გაქვთ კითხვები, დაგვიწერეთ: pylandschool@gmail.com",
        "en": "If you have questions, write to us: pylandschool@gmail.com",
    },
    "Сертификат с указанным номером или кодом не найден в нашей базе данных. Проверьте правильность введенных данных.": {
        "ka": "სერტიფიკატი მითითებული ნომრით ან კოდით ვერ მოიძებნა ჩვენს მონაცემთა ბაზაში. შეამოწმეთ შეყვანილი მონაცემების სისწორე.",
        "en": "Certificate with the specified number or code was not found in our database. Check the correctness of the entered data.",
    },
    # Terms of service translations
    "Подтверждение регистрации и активация аккаунта": {
        "ka": "რეგისტრაციის დადასტურება და ანგარიშის აქტივაცია",
        "en": "Registration confirmation and account activation",
    },
    "Изменения в условиях использования": {
        "ka": "ცვლილებები გამოყენების პირობებში",
        "en": "Changes to Terms of Service",
    },
    "Критические обновления безопасности": {
        "ka": "უსაფრთხოების კრიტიკული განახლებები",
        "en": "Critical security updates",
    },
    "Уведомления о платежах и счетах": {
        "ka": "შეტყობინებები გადახდებისა და ინვოისების შესახებ",
        "en": "Payment and invoice notifications",
    },
}


def update_po_file(filepath, lang):
    """Обновляет переводы в .po файле"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    updated = 0
    for msgid, translations in TRANSLATIONS.items():
        if lang not in translations:
            continue

        msgstr = translations[lang]

        # Ищем строку msgid и следующую за ней msgstr
        import re

        # Экранируем специальные символы для регулярного выражения
        # но сохраняем пробелы и переносы строк как есть
        escaped_msgid = re.escape(msgid)

        # Паттерн 1: Простая однострочная версия
        pattern1 = r'(#[^\n]*\n)*(msgid "' + escaped_msgid + r'"\nmsgstr ")([^"]*)"'

        # Паттерн 2: Многострочная версия с пустым msgstr
        pattern2 = (
            r'(#[^\n]*\n)*(msgid ""\n"'
            + escaped_msgid.replace(" ", r'["\s]*"["\s]*')
            + r'.*?"\nmsgstr "")'
        )

        def replace_simple(match):
            # Убираем fuzzy комментарий
            return f'msgid "{msgid}"\nmsgstr "{msgstr}"'

        def replace_multiline(match):
            # Для многострочных - просто заменяем на однострочную версию
            return f'msgid "{msgid}"\nmsgstr "{msgstr}"'

        # Пробуем заменить
        new_content = re.sub(pattern1, replace_simple, content, flags=re.MULTILINE)

        if new_content != content:
            content = new_content
            updated += 1
            print(f"✓ Updated [{lang}]: {msgid[:50]}...")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return updated


if __name__ == "__main__":
    ka_file = "src/locale/ka/LC_MESSAGES/django.po"
    en_file = "src/locale/en/LC_MESSAGES/django.po"

    print("📝 Updating Georgian translations...")
    ka_updated = update_po_file(ka_file, "ka")
    print(f"✅ Updated {ka_updated} Georgian translations\n")

    print("📝 Updating English translations...")
    en_updated = update_po_file(en_file, "en")
    print(f"✅ Updated {en_updated} English translations\n")

    print("🎉 Done! Now run: poetry run python src/manage.py compilemessages")
