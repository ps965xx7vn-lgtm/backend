"""
Management команда для создания полных тестовых данных для проверки функционала.

Создает:
- Пользователей всех ролей (студенты, менторы, проверяющие, менеджеры)
- Курсы с уроками и шагами
- Записи студентов на курсы и прогресс
- Отправленные задания (submissions)
- Отзывы (reviews) от проверяющих
- Сертификаты для завершенных курсов
- Feedback для менеджеров
- System logs

Использование:
    poetry run python src/manage.py populate_test_data
    poetry run python src/manage.py populate_test_data --students 20 --courses 5
    poetry run python src/manage.py populate_test_data --clear  # Очистить перед созданием
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from authentication.models import Manager, Reviewer, Role, Student
from blog.models import Article, Category as BlogCategory
from certificates.models import Certificate
from courses.models import Course, Lesson, Step
from managers.models import Feedback, SystemLog
from reviewers.models import LessonSubmission, Review, StudentImprovement

User = get_user_model()
fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Создает полные тестовые данные для проверки всего функционала платформы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--students",
            type=int,
            default=15,
            help="Количество студентов для создания (по умолчанию: 15)",
        )
        parser.add_argument(
            "--reviewers",
            type=int,
            default=3,
            help="Количество проверяющих для создания (по умолчанию: 3)",
        )
        parser.add_argument(
            "--mentors",
            type=int,
            default=2,
            help="Количество менторов для создания (по умолчанию: 2)",
        )
        parser.add_argument(
            "--managers",
            type=int,
            default=2,
            help="Количество менеджеров для создания (по умолчанию: 2)",
        )
        parser.add_argument(
            "--courses",
            type=int,
            default=5,
            help="Количество курсов для создания (по умолчанию: 5)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие тестовые данные перед созданием",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(
            self.style.HTTP_INFO(
                "  СОЗДАНИЕ ПОЛНЫХ ТЕСТОВЫХ ДАННЫХ ДЛЯ PYLAND PLATFORM"
            )
        )
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write("")

        if options["clear"]:
            self._clear_test_data()

        with transaction.atomic():
            # 1. Создаем роли
            self.stdout.write(self.style.HTTP_INFO("📋 ШАГ 1/10: Создание ролей"))
            roles = self._create_roles()

            # 2. Создаем пользователей всех типов
            self.stdout.write(self.style.HTTP_INFO("\n👥 ШАГ 2/10: Создание пользователей"))
            users_data = self._create_users(options, roles)

            # 3. Создаем курсы
            self.stdout.write(self.style.HTTP_INFO("\n📚 ШАГ 3/10: Создание курсов"))
            courses = self._create_courses(options["courses"])

            # 4. Создаем записи студентов на курсы
            self.stdout.write(self.style.HTTP_INFO("\n📝 ШАГ 4/10: Запись студентов на курсы"))
            self._enroll_students(users_data["students"], courses)

            # 5. Создаем прогресс студентов
            self.stdout.write(self.style.HTTP_INFO("\n📊 ШАГ 5/10: Создание прогресса студентов"))
            submissions = self._create_progress(users_data["students"], courses)

            # 6. Создаем отзывы от проверяющих
            self.stdout.write(self.style.HTTP_INFO("\n✅ ШАГ 6/10: Создание отзывов проверяющих"))
            self._create_reviews(submissions, users_data["reviewers"])

            # 7. Создаем сертификаты
            self.stdout.write(self.style.HTTP_INFO("\n🎓 ШАГ 7/10: Создание сертификатов"))
            certificates = self._create_certificates(users_data["students"], courses)

            # 8. Создаем feedback для менеджеров
            self.stdout.write(self.style.HTTP_INFO("\n💬 ШАГ 8/10: Создание обращений (Feedback)"))
            self._create_feedback(users_data["managers"])

            # 9. Создаем system logs
            self.stdout.write(self.style.HTTP_INFO("\n📄 ШАГ 9/10: Создание системных логов"))
            self._create_system_logs(users_data)

            # 10. Статистика
            self.stdout.write(self.style.HTTP_INFO("\n📈 ШАГ 10/10: Статистика"))
            self._print_statistics(users_data, courses, submissions, certificates)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Все тестовые данные успешно созданы!"))
        self.stdout.write("")
        self._print_test_accounts(users_data)

    def _clear_test_data(self):
        """Очистка тестовых данных"""
        self.stdout.write(self.style.WARNING("⚠️  Очистка существующих тестовых данных..."))

        # Удаляем пользователей (кроме суперпользователя)
        test_users = User.objects.filter(email__contains="test").exclude(is_superuser=True)
        deleted_count = test_users.count()
        test_users.delete()

        # Удаляем тестовые курсы
        Course.objects.filter(name__icontains="тест").delete()

        # Удаляем feedback
        Feedback.objects.filter(email__contains="test").delete()

        # Удаляем старые логи
        SystemLog.objects.filter(created_at__lt=timezone.now() - timedelta(days=7)).delete()

        self.stdout.write(self.style.SUCCESS(f"✓ Удалено {deleted_count} тестовых пользователей"))
        self.stdout.write("")

    def _create_roles(self):
        """Создание всех ролей"""
        roles = {}

        role_data = [
            ("student", "Студент", "Студент платформы, проходит курсы"),
            ("mentor", "Ментор", "Ментор и куратор студентов"),
            ("reviewer", "Проверяющий", "Проверяет работы студентов"),
            ("manager", "Менеджер", "Управляет платформой и контентом"),
        ]

        for name, display_name, description in role_data:
            role, created = Role.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            roles[name] = role
            status = "создана" if created else "уже существует"
            self.stdout.write(f"  • Роль '{display_name}': {status}")

        return roles

    def _create_users(self, options, roles):
        """Создание пользователей всех типов"""
        users_data = {
            "students": [],
            "reviewers": [],
            "mentors": [],
            "managers": [],
        }

        # Создаем студентов
        self.stdout.write(f"\n  Создание {options['students']} студентов...")
        for i in range(options["students"]):
            email = f"student{i+1}@test.com"
            user = self._create_user(
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=roles["student"],
            )
            users_data["students"].append(user)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Создано {len(users_data['students'])} студентов"))

        # Создаем проверяющих
        self.stdout.write(f"\n  Создание {options['reviewers']} проверяющих...")
        for i in range(options["reviewers"]):
            email = f"reviewer{i+1}@test.com"
            user = self._create_user(
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=roles["reviewer"],
            )
            users_data["reviewers"].append(user)
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {len(users_data['reviewers'])} проверяющих")
        )

        # Создаем менторов
        self.stdout.write(f"\n  Создание {options['mentors']} менторов...")
        for i in range(options["mentors"]):
            email = f"mentor{i+1}@test.com"
            user = self._create_user(
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=roles["mentor"],
            )
            users_data["mentors"].append(user)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Создано {len(users_data['mentors'])} менторов"))

        # Создаем менеджеров
        self.stdout.write(f"\n  Создание {options['managers']} менеджеров...")
        for i in range(options["managers"]):
            email = f"manager{i+1}@test.com"
            user = self._create_user(
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=roles["manager"],
                is_staff=True,
            )
            users_data["managers"].append(user)
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {len(users_data['managers'])} менеджеров")
        )

        return users_data

    def _create_user(self, email, first_name, last_name, role, is_staff=False):
        """Создание одного пользователя с профилем"""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "is_staff": is_staff,
            },
        )

        if created:
            user.set_password("test123")
            user.save()

        # Устанавливаем роль
        user.role = role
        user.save()

        # Создаем профиль в зависимости от роли
        if role.name == "student":
            Student.objects.get_or_create(
                user=user,
                defaults={
                    "bio": fake.text(max_nb_chars=200),
                    "phone": fake.phone_number(),
                    "is_active": True,
                },
            )
        elif role.name == "reviewer":
            Reviewer.objects.get_or_create(
                user=user,
                defaults={
                    "bio": f"Опытный проверяющий с экспертизой в {fake.job()}",
                    "is_active": True,
                },
            )
        elif role.name == "manager":
            Manager.objects.get_or_create(user=user, defaults={"is_active": True})

        return user

    def _create_courses(self, count):
        """Создание курсов с уроками и шагами"""
        courses = []

        course_templates = [
            {
                "title": "Python для начинающих",
                "description": "Изучите основы программирования на Python",
                "category": "python",
            },
            {
                "title": "Django Web Development",
                "description": "Создание веб-приложений на Django",
                "category": "web",
            },
            {
                "title": "JavaScript и React",
                "description": "Современная фронтенд-разработка",
                "category": "javascript",
            },
            {
                "title": "Data Science с Python",
                "description": "Анализ данных и машинное обучение",
                "category": "data-science",
            },
            {
                "title": "Git и GitHub",
                "description": "Система контроля версий для разработчиков",
                "category": "other",
            },
        ]

        for i in range(min(count, len(course_templates))):
            template = course_templates[i]

            course, created = Course.objects.get_or_create(
                name=template["title"],
                defaults={
                    "description": template["description"],
                    "category": template["category"],
                    "status": "active",
                    "price": Decimal(random.choice([0, 1990, 2990, 4990])),
                    "rating": Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                    "is_featured": random.choice([True, False]),
                },
            )

            if created:
                # Создаем уроки
                for lesson_num in range(1, random.randint(4, 7)):
                    lesson_name = f"Урок {lesson_num}: {fake.sentence(nb_words=4)}"
                    lesson_slug = f"{course.slug}-lesson-{lesson_num}"
                    
                    lesson = Lesson.objects.create(
                        course=course,
                        name=lesson_name,
                        slug=lesson_slug,
                        short_description=fake.text(max_nb_chars=200),
                        lesson_number=lesson_num,
                    )

                    # Создаем шаги
                    for step_num in range(1, random.randint(3, 6)):
                        Step.objects.create(
                            lesson=lesson,
                            name=f"Шаг {step_num}: {fake.sentence(nb_words=3)}",
                            description=fake.text(max_nb_chars=500),
                            step_number=step_num,
                        )

            courses.append(course)
            self.stdout.write(f"  • Курс '{course.name}': {'создан' if created else 'существует'}")

        return courses

    def _enroll_students(self, students, courses):
        """Запись студентов на курсы"""
        enrollments_created = 0

        for student in students:
            student_profile = student.student
            # Каждый студент записывается на 1-3 курса
            num_courses = random.randint(1, min(3, len(courses)))
            selected_courses = random.sample(courses, num_courses)

            for course in selected_courses:
                if course not in student_profile.courses.all():
                    student_profile.courses.add(course)
                    enrollments_created += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Создано {enrollments_created} записей на курсы"))

    def _create_progress(self, students, courses):
        """Создание прогресса студентов и submissions"""
        from reviewers.models import StepProgress
        
        submissions = []
        submissions_created = 0
        steps_completed = 0

        for student in students:
            student_profile = student.student
            enrolled_courses = student_profile.courses.all()

            for course in enrolled_courses:
                lessons = course.lessons.all()

                # Проходим случайное количество уроков (от 20% до 80%)
                lessons_to_complete = max(1, int(lessons.count() * random.uniform(0.2, 0.8)))

                for lesson in lessons[:lessons_to_complete]:
                    steps = lesson.steps.all()
                    
                    # Случайное количество выполненных шагов (от 50% до 100%)
                    steps_to_complete = max(1, int(steps.count() * random.uniform(0.5, 1.0)))
                    
                    # Создаём прогресс по шагам
                    for step in steps[:steps_to_complete]:
                        progress, created = StepProgress.objects.get_or_create(
                            profile=student_profile,
                            step=step,
                            defaults={
                                "is_completed": True,
                                "completed_at": timezone.now() - timedelta(days=random.randint(1, 30)),
                            },
                        )
                        if created:
                            steps_completed += 1
                    
                    # Если выполнено больше 70% шагов урока, создаём submission
                    completion_rate = steps_to_complete / steps.count() if steps.count() > 0 else 0
                    if completion_rate >= 0.7:
                        # 80% вероятность что студент отправил задание
                        if random.random() < 0.8:
                            submission, created = LessonSubmission.objects.get_or_create(
                                student=student.student,
                                lesson=lesson,
                                defaults={
                                    "lesson_url": f"https://github.com/student/lesson-{lesson.id}/pull/{random.randint(1, 999)}",
                                    "status": "pending",  # Только pending, чтобы избежать срабатывания сигналов
                                    "submitted_at": timezone.now() - timedelta(days=random.randint(1, 25)),
                                },
                            )
                            if created:
                                submissions.append(submission)
                                submissions_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {steps_completed} выполненных шагов")
        )
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {submissions_created} отправленных заданий")
        )
        return submissions

    def _create_reviews(self, submissions, reviewers):
        """Создание отзывов от проверяющих"""
        from reviewers.models import StepProgress
        
        reviews_created = 0
        improvements_created = 0

        # Проверяем только submissions со статусом pending
        for submission in submissions:
            if submission.status == "pending":
                # 60% вероятность что работа проверена
                if random.random() < 0.6 and reviewers:
                    reviewer = random.choice(reviewers)
                    
                    # Выбираем новый статус
                    new_status = random.choice(["approved", "changes_requested"])

                    review, created = Review.objects.get_or_create(
                        lesson_submission=submission,
                        reviewer=reviewer.reviewer,
                        defaults={
                            "status": "approved" if new_status == "approved" else "needs_work",
                            "comments": fake.text(max_nb_chars=200),
                            "time_spent": random.randint(10, 60),
                            "reviewed_at": timezone.now()
                            - timedelta(days=random.randint(0, 20)),
                        },
                    )

                    if created:
                        reviews_created += 1
                        
                        # Обновляем статус submission
                        submission.status = new_status
                        submission.reviewed_at = timezone.now() - timedelta(days=random.randint(0, 15))
                        
                        # Добавляем комментарий ментора если требуются доработки
                        if new_status == "changes_requested":
                            submission.mentor_comment = fake.text(max_nb_chars=150)
                        
                        submission.save()
                        
                        # ВАЖНО: Если работа одобрена, убеждаемся что ВСЕ шаги урока выполнены
                        if new_status == "approved":
                            lesson_steps = submission.lesson.steps.all()
                            for step in lesson_steps:
                                StepProgress.objects.get_or_create(
                                    profile=submission.student,
                                    step=step,
                                    defaults={
                                        "is_completed": True,
                                        "completed_at": submission.submitted_at,
                                    },
                                )

                        # Если требуются доработки, создаем улучшения
                        if new_status == "changes_requested":
                            num_improvements = random.randint(1, 3)
                            for i in range(num_improvements):
                                StudentImprovement.objects.create(
                                    lesson_submission=submission,
                                    review=review,
                                    improvement_number=i + 1,
                                    title=fake.sentence(nb_words=4),
                                    improvement_text=fake.text(max_nb_chars=100),
                                    priority=random.choice(["low", "medium", "high"]),
                                    is_completed=random.choice([True, False]),
                                )
                                improvements_created += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Создано {reviews_created} отзывов"))
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {improvements_created} рекомендаций по улучшению")
        )

    def _create_certificates(self, students, courses):
        """Создание сертификатов для завершенных курсов"""
        from reviewers.models import LessonSubmission, StepProgress
        from certificates.utils import generate_certificate_pdf

        certificates = []
        certificates_created = 0

        for student in students:
            student_profile = student.student
            enrolled_courses = student_profile.courses.filter(status="active")

            for course in enrolled_courses:
                # Проверить прогресс курса - сертификат только если 100%
                progress_data = course.get_progress_for_profile(student_profile)
                completion_percentage = progress_data.get("completion_percentage", 0) if isinstance(progress_data, dict) else progress_data
                
                # Сертификат только если курс завершен на 100% ИЛИ для тестирования с 20% вероятностью
                should_create_cert = completion_percentage >= 100 or (completion_percentage >= 50 and random.random() < 0.2)
                
                if should_create_cert:
                    # Проверить, нет ли уже сертификата
                    existing = Certificate.objects.filter(
                        student=student_profile, course=course
                    ).first()

                    if not existing:
                        completion_date = (
                            timezone.now() - timedelta(days=random.randint(1, 60))
                        ).date()

                        # Собрать статистику вручную
                        total_lessons = course.lessons.count()

                        # Подсчет завершенных уроков
                        completed_lessons = 0
                        for lesson in course.lessons.all():
                            # Считаем урок завершенным если есть шаги с is_completed=True
                            completed_steps_count = StepProgress.objects.filter(
                                profile=student_profile,
                                step__lesson=lesson,
                                is_completed=True,
                            ).count()
                            total_steps_count = lesson.steps.count()
                            if (
                                total_steps_count > 0
                                and completed_steps_count == total_steps_count
                            ):
                                completed_lessons += 1

                        # Подсчет заданий
                        submissions = LessonSubmission.objects.filter(
                            student=student_profile, lesson__course=course
                        )
                        assignments_submitted = submissions.count()
                        assignments_approved = submissions.filter(status="approved").count()
                        reviews_received = submissions.exclude(status="pending").count()

                        # Подсчет времени (примерная оценка)
                        steps_completed = StepProgress.objects.filter(
                            profile=student_profile,
                            step__lesson__course=course,
                            is_completed=True,
                        ).count()
                        total_time_spent = round((steps_completed * 15) / 60, 2)  # В часах

                        # Итоговая оценка (случайная от 60 до 100)
                        final_grade = random.randint(60, 100) if completed_lessons > 0 else None

                        try:
                            # Создать сертификат напрямую с заполненными данными
                            certificate = Certificate.objects.create(
                                student=student_profile,
                                course=course,
                                completion_date=completion_date,
                                lessons_completed=completed_lessons,
                                total_lessons=total_lessons,
                                assignments_submitted=assignments_submitted,
                                assignments_approved=assignments_approved,
                                reviews_received=reviews_received,
                                total_time_spent=total_time_spent,
                                final_grade=final_grade,
                            )
                            
                            # Генерировать PDF автоматически
                            try:
                                generate_certificate_pdf(certificate)
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"    ✓ Сертификат {certificate.certificate_number} + PDF для "
                                        f"{student.email} по курсу '{course.name}' "
                                        f"({completed_lessons}/{total_lessons} уроков, {int(completion_percentage)}% прогресс)"
                                    )
                                )
                            except ImportError:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    ⚠ Сертификат {certificate.certificate_number} создан, но PDF не сгенерирован (ReportLab не установлен)"
                                    )
                                )
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    ⚠ Сертификат {certificate.certificate_number} создан, но ошибка генерации PDF: {e}"
                                    )
                                )
                            
                            certificates.append(certificate)
                            certificates_created += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"    ⚠ Не удалось создать сертификат: {e}"
                                )
                            )

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {certificates_created} сертификатов")
        )
        return certificates

    def _create_feedback(self, managers):
        """Создание обращений (feedback) для менеджеров"""
        feedback_created = 0

        topics = ["courses", "career", "technical", "partnership", "other"]

        for _ in range(random.randint(10, 20)):
            is_processed = random.choice([True, False])
            processed_by = random.choice(managers) if is_processed and managers else None

            Feedback.objects.create(
                first_name=fake.first_name(),
                phone_number=fake.phone_number(),
                email=fake.email(),
                topic=random.choice(topics),
                message=fake.text(max_nb_chars=300),
                registered_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                is_processed=is_processed,
                processed_by=processed_by,
                admin_notes=fake.sentence() if is_processed else "",
            )
            feedback_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Создано {feedback_created} обращений (Feedback)")
        )

    def _create_system_logs(self, users_data):
        """Создание системных логов"""
        logs_created = 0

        all_users = (
            users_data["students"]
            + users_data["reviewers"]
            + users_data["mentors"]
            + users_data["managers"]
        )

        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
        
        action_types = [
            "USER_LOGIN",
            "USER_LOGOUT",
            "USER_REGISTERED",
            "USER_UPDATED",
            "FEEDBACK_CREATED",
            "COURSE_CREATED",
            "COURSE_UPDATED",
            "PAYMENT_PROCESSED",
            "ERROR_OCCURRED",
            "SECURITY_EVENT",
        ]

        for _ in range(random.randint(30, 50)):
            user = random.choice(all_users) if all_users else None
            action_type = random.choice(action_types)
            
            if action_type == "ERROR_OCCURRED":
                level = "ERROR"
            elif action_type == "SECURITY_EVENT":
                level = random.choice(["WARNING", "ERROR", "CRITICAL"])
            else:
                level = random.choice(["INFO", "DEBUG"])

            SystemLog.objects.create(
                level=level,
                action_type=action_type,
                user=user,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                message=f"Действие {action_type} выполнено пользователем {user.email if user else 'Anonymous'}",
                details={"timestamp": str(timezone.now()), "status": "success"},
            )
            logs_created += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Создано {logs_created} системных логов"))

    def _print_statistics(self, users_data, courses, submissions, certificates):
        """Вывод статистики созданных данных"""
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("  📊 Статистика созданных данных:"))
        self.stdout.write(self.style.HTTP_INFO("  " + "-" * 78))

        total_enrollments = sum(
            student.student.courses.count() for student in users_data["students"]
        )

        stats = [
            ("Студентов", len(users_data["students"])),
            ("Проверяющих", len(users_data["reviewers"])),
            ("Менторов", len(users_data["mentors"])),
            ("Менеджеров", len(users_data["managers"])),
            ("Курсов", len(courses)),
            (
                "Уроков",
                sum(course.lessons.count() for course in courses),
            ),
            (
                "Шагов",
                sum(
                    lesson.steps.count()
                    for course in courses
                    for lesson in course.lessons.all()
                ),
            ),
            ("Записей на курсы", total_enrollments),
            ("Отправленных заданий", len(submissions)),
            ("Отзывов проверяющих", Review.objects.count()),
            ("Сертификатов", len(certificates)),
            ("Обращений (Feedback)", Feedback.objects.count()),
            ("Системных логов", SystemLog.objects.count()),
        ]

        for label, count in stats:
            self.stdout.write(f"    • {label}: {count}")

    def _print_test_accounts(self, users_data):
        """Вывод информации о тестовых аккаунтах"""
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write(self.style.HTTP_INFO("  🔑 ТЕСТОВЫЕ АККАУНТЫ (пароль для всех: test123)"))
        self.stdout.write(self.style.HTTP_INFO("=" * 80))
        self.stdout.write("")

        accounts = [
            ("👨‍🎓 Студенты", "student1@test.com - student15@test.com"),
            ("👨‍🏫 Менторы", "mentor1@test.com, mentor2@test.com"),
            ("✅ Проверяющие", "reviewer1@test.com - reviewer3@test.com"),
            ("👔 Менеджеры", "manager1@test.com, manager2@test.com"),
        ]

        for role, emails in accounts:
            self.stdout.write(f"  {role}")
            self.stdout.write(f"    Email: {emails}")
            self.stdout.write("")

        self.stdout.write(self.style.WARNING("  💡 Используйте эти аккаунты для тестирования!"))
        self.stdout.write("")
