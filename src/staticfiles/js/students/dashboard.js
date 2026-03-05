/**
 * PyLand Dashboard - JavaScript интерактивность
 */

class DashboardManager {
    constructor() {
        this.init();
    }

    init() {
        this.initSidebar();
        this.initCharts();
        this.initModals();
        this.initTooltips();
        this.initAnimations();
        this.initStepToggle();
        this.initLessonSubmission();
        this.initSubmissionTabs();
    }

    // Инициализация боковой панели
    initSidebar() {
        // Находим кнопку дашборда в header
        let mobileToggle = document.querySelector('.dashboard-menu-btn');

        if (!mobileToggle) {
            return;
        }

        // Проверяем, есть ли уже overlay в HTML
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }

        // УДАЛЕНО: обработчики мобильного меню теперь в dashboard-mobile.js
        // Избегаем конфликта двойных обработчиков

        // Обновление активной ссылки
        this.updateActiveNavLink();
    }

    // Обновление активной ссылки навигации
    updateActiveNavLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.dashboard-nav-link');

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // Инициализация графиков (простая реализация)
    initCharts() {
        this.initActivityChart();
        this.initProgressChart();
    }

    // График активности
    initActivityChart() {
        const chartContainer = document.querySelector('#activity-chart');
        if (!chartContainer) return;

        // Получаем данные из data-атрибутов
        const dailyActivity = window.dashboardData?.dailyActivity || [];

        // Проверяем, есть ли активность
        const hasActivity = dailyActivity.length > 0 && dailyActivity.some(day => day.completed_steps > 0);

        // Если нет активности, показываем заглушку
        if (!hasActivity) {
            const translations = window.dashboardData?.translations || {};
            chartContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: var(--gray-500); text-align: center; padding: 2rem;">
                    <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="opacity: 0.4; margin-bottom: 1rem;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                    <p style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem; color: var(--gray-700);">${translations.noActivityTitle}</p>
                    <p style="font-size: 0.875rem; color: var(--gray-500);">${translations.noActivityText}</p>
                </div>
            `;
            return;
        }

        this.renderActivityChart(chartContainer, dailyActivity);
    }

    // Отрисовка графика активности
    renderActivityChart(container, data) {
        if (!data || data.length === 0) {
            return;
        }

        const maxValue = Math.max(...data.map(d => d.completed_steps), 1); // Минимум 1 чтобы избежать деления на 0
        const width = container.offsetWidth - 40;
        const height = 160;
        const barWidth = Math.max(width / data.length - 10, 20); // Минимальная ширина столбца 20px

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', width + 40);
        svg.setAttribute('height', height + 40);
        svg.style.overflow = 'visible';

        data.forEach((item, index) => {
            const barHeight = Math.max((item.completed_steps / maxValue) * height, 2); // Минимальная высота 2px
            const x = index * (barWidth + 10) + 20;
            const y = height - barHeight + 20;

            // Столбец
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', barWidth);
            rect.setAttribute('height', barHeight);
            rect.setAttribute('fill', 'url(#gradient)');
            rect.setAttribute('rx', '4');
            rect.style.transition = 'all 0.3s ease';

            // Анимация появления
            rect.style.opacity = '0';
            rect.style.transform = 'translateY(20px)';
            setTimeout(() => {
                rect.style.opacity = '1';
                rect.style.transform = 'translateY(0)';
            }, index * 100);

            // Подпись - день месяца
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x + barWidth / 2);
            text.setAttribute('y', height + 35);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.setAttribute('fill', '#6b7280');

            // Парсим дату и извлекаем день
            const date = new Date(item.date);
            const dayOfMonth = !isNaN(date.getTime()) ? date.getDate() : '?';
            text.textContent = dayOfMonth;

            // Значение
            const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            valueText.setAttribute('x', x + barWidth / 2);
            valueText.setAttribute('y', y - 5);
            valueText.setAttribute('text-anchor', 'middle');
            valueText.setAttribute('font-size', '12');
            valueText.setAttribute('font-weight', '600');
            valueText.setAttribute('fill', '#374151');
            valueText.textContent = item.completed_steps || 0;

            svg.appendChild(rect);
            svg.appendChild(text);
            svg.appendChild(valueText);
        });

        // Градиент
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'gradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '0%');
        gradient.setAttribute('y2', '100%');

        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', '#3b82f6');

        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', '#1d4ed8');

        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.appendChild(defs);

        container.innerHTML = '';
        container.appendChild(svg);
    }

    // График прогресса курсов
    initProgressChart() {
        const chartContainer = document.querySelector('#progress-chart');
        if (!chartContainer) return;

        // Данные прогресса курсов
        const courseProgress = window.dashboardData?.courseProgress || [];

        // Если нет курсов, показываем заглушку
        if (courseProgress.length === 0) {
            const translations = window.dashboardData?.translations || {};
            chartContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: var(--gray-500); text-align: center; padding: 2rem;">
                    <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="opacity: 0.5; margin-bottom: 1rem;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                    </svg>
                    <p style="font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">${translations.noCoursesTitle}</p>
                    <p style="font-size: 0.875rem;">${translations.noCoursesText}</p>
                </div>
            `;
            return;
        }

        this.renderProgressChart(chartContainer, courseProgress);
    }

    // Отрисовка графика прогресса
    renderProgressChart(container, data) {
        if (!data || data.length === 0) {
            return;
        }

        const radius = 80;
        const centerX = 100;
        const centerY = 100;
        const strokeWidth = 12;

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '200');
        svg.setAttribute('height', '200');
        svg.setAttribute('viewBox', '0 0 200 200');

        let currentAngle = -90; // Начинаем с верха

        data.forEach((item, index) => {
            if (!item || typeof item.progress !== 'number') {
                return;
            }

            const percentage = Math.min(Math.max(item.progress / 100, 0), 1); // Clamp between 0 and 1
            const angle = percentage * 360;
            const largeArcFlag = angle > 180 ? 1 : 0;

            const startAngle = currentAngle * (Math.PI / 180);
            const endAngle = (currentAngle + angle) * (Math.PI / 180);

            const x1 = centerX + radius * Math.cos(startAngle);
            const y1 = centerY + radius * Math.sin(startAngle);
            const x2 = centerX + radius * Math.cos(endAngle);
            const y2 = centerY + radius * Math.sin(endAngle);

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`);
            path.setAttribute('fill', item.color || '#3b82f6');
            path.setAttribute('opacity', '0.8');
            path.style.transition = 'all 0.3s ease';

            // Анимация появления
            path.style.transform = 'scale(0)';
            path.style.transformOrigin = `${centerX}px ${centerY}px`;
            setTimeout(() => {
                path.style.transform = 'scale(1)';
            }, index * 150);

            svg.appendChild(path);
            currentAngle += angle;
        });

        // Центральный круг
        const centerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        centerCircle.setAttribute('cx', centerX);
        centerCircle.setAttribute('cy', centerY);
        centerCircle.setAttribute('r', '30');
        centerCircle.setAttribute('fill', 'white');
        centerCircle.setAttribute('stroke', '#e5e7eb');
        centerCircle.setAttribute('stroke-width', '2');
        svg.appendChild(centerCircle);

        // Общий процент
        const overallProgress = Math.round(data.reduce((sum, item) => sum + item.progress, 0) / data.length);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', centerX);
        text.setAttribute('y', centerY);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.setAttribute('font-size', '18');
        text.setAttribute('font-weight', '700');
        text.setAttribute('fill', '#374151');
        text.textContent = `${overallProgress}%`;
        svg.appendChild(text);

        container.innerHTML = '';
        container.appendChild(svg);

        // Легенда
        const legend = document.createElement('div');
        legend.className = 'chart-legend';
        legend.style.marginTop = '1rem';

        data.forEach(item => {
            const legendItem = document.createElement('div');
            legendItem.style.display = 'flex';
            legendItem.style.alignItems = 'center';
            legendItem.style.gap = '0.5rem';
            legendItem.style.marginBottom = '0.25rem';

            const colorBox = document.createElement('div');
            colorBox.style.width = '12px';
            colorBox.style.height = '12px';
            colorBox.style.backgroundColor = item.color;
            colorBox.style.borderRadius = '2px';

            const label = document.createElement('span');
            label.style.fontSize = '0.875rem';
            label.style.color = '#6b7280';
            label.textContent = `${item.name}: ${item.progress}%`;

            legendItem.appendChild(colorBox);
            legendItem.appendChild(label);
            legend.appendChild(legendItem);
        });

        container.appendChild(legend);
    }

    // Инициализация модальных окон
    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');

        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.openModal(modalId);
            });
        });

        // Закрытие по клику на overlay
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    // Открытие модального окна
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Анимация появления
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.9) translateY(-20px)';
            modalContent.style.opacity = '0';

            setTimeout(() => {
                modalContent.style.transform = 'scale(1) translateY(0)';
                modalContent.style.opacity = '1';
            }, 10);
        }
    }

    // Закрытие модального окна
    closeModal() {
        const activeModal = document.querySelector('.modal.active');
        if (!activeModal) return;

        const modalContent = activeModal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.9) translateY(-20px)';
            modalContent.style.opacity = '0';
        }

        setTimeout(() => {
            activeModal.classList.remove('active');
            document.body.style.overflow = '';
        }, 200);
    }

    // Инициализация подсказок
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');

        tooltipElements.forEach(element => {
            let tooltip = null;

            element.addEventListener('mouseenter', () => {
                const text = element.dataset.tooltip;
                tooltip = this.createTooltip(text);
                document.body.appendChild(tooltip);
                this.positionTooltip(tooltip, element);
            });

            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                    tooltip = null;
                }
            });

            element.addEventListener('mousemove', (e) => {
                if (tooltip) {
                    this.positionTooltip(tooltip, element, e);
                }
            });
        });
    }

    // Создание подсказки
    createTooltip(text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #1f2937;
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
            white-space: nowrap;
        `;

        setTimeout(() => {
            tooltip.style.opacity = '1';
        }, 10);

        return tooltip;
    }

    // Позиционирование подсказки
    positionTooltip(tooltip, element, event = null) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        let top = rect.top - tooltipRect.height - 8;

        // Проверка границ экрана
        if (left < 8) left = 8;
        if (left + tooltipRect.width > window.innerWidth - 8) {
            left = window.innerWidth - tooltipRect.width - 8;
        }

        if (top < 8) {
            top = rect.bottom + 8;
        }

        tooltip.style.left = `${left + window.scrollX}px`;
        tooltip.style.top = `${top + window.scrollY}px`;
    }

    // Инициализация анимаций при скролле
    initAnimations() {
        const animatedElements = document.querySelectorAll('.stat-card, .course-card, .achievement-card');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
            observer.observe(element);
        });
    }

    // Переключение статуса шага
    initStepToggle() {
        const stepCheckboxes = document.querySelectorAll('.step-checkbox:not(.improvement-step-checkbox)');

        if (stepCheckboxes.length === 0) {

            return;
        }

        // Флаг для предотвращения множественных запросов
        let isProcessing = false;

        stepCheckboxes.forEach((checkbox, index) => {

            // Удаляем старые обработчики если есть
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);

            newCheckbox.addEventListener('change', async (e) => {
                // Предотвращаем множественные запросы
                if (isProcessing) {

                    return;
                }

                isProcessing = true;

                const stepId = e.target.dataset.stepId;
                const courseSlug = e.target.dataset.courseSlug;
                const lessonSlug = e.target.dataset.lessonSlug;
                const isCompleted = e.target.checked;

                if (!stepId || !courseSlug || !lessonSlug) {

                    window.showNotification('Ошибка: отсутствуют данные шага', 'error');
                    e.target.checked = !isCompleted;
                    isProcessing = false;
                    return;
                }

                // Получаем текущий язык из URL
                const currentPath = window.location.pathname;
                const langMatch = currentPath.match(/^\/(ru|en|ka)\//);
                const langPrefix = langMatch ? `/${langMatch[1]}` : '/ru';

                const url = `${langPrefix}/students/courses/${courseSlug}/lessons/${lessonSlug}/steps/${stepId}/toggle/`;

                try {
                    const csrfToken = this.getCSRFToken();

                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ completed: isCompleted })
                    });

                    if (response.ok) {
                        const data = await response.json();

                        // Обновляем визуальное состояние чекбокса и карточки шага
                        const stepCard = e.target.closest('.step-item, .step-card');
                        if (stepCard) {
                            if (isCompleted) {
                                stepCard.classList.add('completed');
                            } else {
                                stepCard.classList.remove('completed');
                            }
                        }

                        this.updateProgress(data);

                        // Проверяем, все ли шаги урока выполнены
                        if (data.lesson_progress && data.lesson_progress.is_completed && isCompleted) {
                            window.showNotification(
                                '🎉 Все шаги урока выполнены! Теперь прикрепите ссылку на работу ниже',
                                'success'
                            );
                        } else {
                            window.showNotification(
                                isCompleted ? 'Шаг отмечен как выполненный!' : 'Отметка о выполнении снята',
                                'success'
                            );
                        }
                    } else {
                        const errorText = await response.text();

                        throw new Error('Ошибка при обновлении прогресса');
                    }
                } catch (error) {

                    e.target.checked = !isCompleted; // Откатываем изменение
                    window.showNotification('Произошла ошибка при обновлении прогресса', 'error');
                } finally {
                    isProcessing = false;
                }
            });
        });
    }

    // Обновление прогресса на странице
    updateProgress(data) {

        // Обновляем прогресс бары урока (на странице урока)
        const lessonProgressBar = document.querySelector('.lesson-progress-fill:not([data-lesson-id])');

        if (lessonProgressBar && data.lesson_progress) {
            lessonProgressBar.style.width = `${data.lesson_progress.completion_percentage}%`;
        }

        // Обновляем прогресс конкретного урока на странице курса
        if (data.lesson_progress) {
            const lessonId = data.lesson_progress.lesson_id || this.getCurrentLessonId();
            if (lessonId) {
                // Обновляем прогресс бар урока
                const lessonProgressBars = document.querySelectorAll(`.lesson-progress-fill[data-lesson-id="${lessonId}"]`);
                lessonProgressBars.forEach(bar => {
                    bar.style.width = `${data.lesson_progress.completion_percentage}%`;

                    // Обновляем классы для цвета
                    bar.classList.remove('success', 'warning');
                    if (data.lesson_progress.is_completed) {
                        bar.classList.add('success');
                    } else if (data.lesson_progress.completion_percentage >= 50) {
                        bar.classList.add('warning');
                    }
                });

                // Обновляем текст прогресса
                const progressTexts = document.querySelectorAll(`.lesson-progress-text[data-lesson-id="${lessonId}"]`);
                progressTexts.forEach(text => {
                    const completedSpan = text.querySelector('.completed-steps-count');
                    const totalSpan = text.querySelector('.total-steps-count');
                    if (completedSpan) completedSpan.textContent = data.lesson_progress.completed_steps;
                    if (totalSpan) totalSpan.textContent = data.lesson_progress.total_steps;
                });

                // Обновляем процент
                const percentageTexts = document.querySelectorAll(`.lesson-progress-percentage[data-lesson-id="${lessonId}"]`);
                percentageTexts.forEach(pct => {
                    pct.textContent = `${Math.round(data.lesson_progress.completion_percentage)}%`;
                });

            }
        }

        // Обновляем прогресс курса
        const courseProgressBar = document.querySelector('.course-progress-fill');

        if (courseProgressBar && data.course_progress) {
            courseProgressBar.style.width = `${data.course_progress.completion_percentage}%`;
        }

        // Обновляем счетчики шагов урока
        const completedStepsElement = document.querySelector('.lesson-completed-steps');
        const totalStepsElement = document.querySelector('.lesson-total-steps');

        if (completedStepsElement && data.lesson_progress) {
            completedStepsElement.textContent = data.lesson_progress.completed_steps;
        }

        if (totalStepsElement && data.lesson_progress) {
            totalStepsElement.textContent = data.lesson_progress.total_steps;
        }

        // Обновляем процент прогресса урока
        const lessonPercentageElement = document.querySelector('.lesson-progress-percentage:not([data-lesson-id])');
        if (lessonPercentageElement && data.lesson_progress) {
            lessonPercentageElement.textContent = `${Math.round(data.lesson_progress.completion_percentage)}%`;
        }

        // Обновляем процент прогресса курса
        const coursePercentageElement = document.querySelector('.course-progress-percentage');
        if (coursePercentageElement && data.course_progress) {
            coursePercentageElement.textContent = `${Math.round(data.course_progress.completion_percentage)}%`;
        }

        // Обновляем статус step-card (добавляем/убираем класс completed)
        if (data.step_id) {
            const stepCard = document.querySelector(`[data-step-id="${data.step_id}"]`);
            if (stepCard) {
                if (data.is_completed) {
                    stepCard.classList.add('completed');

                } else {
                    stepCard.classList.remove('completed');

                }
            }
        }
    }

    // Получить ID текущего урока из URL
    getCurrentLessonId() {
        const match = window.location.pathname.match(/\/lessons\/([^\/]+)/);
        return match ? match[1] : null;
    }

    // Обработка отправки работы на проверку
    initLessonSubmission() {
        const form = document.getElementById('lesson-submission-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submit-work-btn');
            const urlInput = document.getElementById('id_lesson_url');
            const errorsDiv = document.getElementById('submission-errors');
            const lessonUrl = urlInput.value.trim();

            // Валидация GitHub URL
            if (!lessonUrl.match(/^https:\/\/github\.com\/.+/)) {
                errorsDiv.innerHTML = '<div class="error-message">Пожалуйста, укажите корректную ссылку на GitHub репозиторий</div>';
                urlInput.classList.add('error');
                return;
            }

            // Получаем данные из URL
            const currentPath = window.location.pathname;
            const langMatch = currentPath.match(/^\/(ru|en|ka)\//);
            const langPrefix = langMatch ? `/${langMatch[1]}` : '/ru';
            // Парсим UUID пользователя из URL (courses/<uuid>/<course_slug>/lessons/<lesson_slug>/)
            const pathMatch = currentPath.match(/courses\/([0-9a-f-]{36})\/([^\/]+)\/lessons\/([^\/]+)/);

            if (!pathMatch) {
                errorsDiv.innerHTML = '<div class="error-message">Ошибка формирования URL. Обновите страницу.</div>';
                return;
            }

            const [, userUuid, courseSlug, lessonSlug] = pathMatch;
            const url = `${langPrefix}/students/courses/${userUuid}/${courseSlug}/lessons/${lessonSlug}/submit/`;

            // Блокируем кнопку
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <svg class="spinner" width="16" height="16" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" opacity="0.25"/>
                    <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="3" fill="none"/>
                </svg>
                <span>Отправка...</span>
            `;

            try {
                const csrfToken = this.getCSRFToken();
                const formData = new FormData();
                formData.append('lesson_url', lessonUrl);

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    errorsDiv.innerHTML = '';
                    urlInput.classList.remove('error');

                    // Показываем уведомление об успехе
                    this.showNotification(data.message, 'success');

                    // Очищаем форму
                    urlInput.value = '';

                    // Показываем информацию об отправленной работе
                    form.innerHTML = `
                        <div class="submission-success">
                            <div class="success-icon">
                                <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <h4>Работа отправлена на проверку!</h4>
                            <p>Ссылка на GitHub: <a href="${data.submission.url}" target="_blank" rel="noopener">${data.submission.url}</a></p>
                            <p class="submission-time">Отправлено: ${new Date(data.submission.submitted_at).toLocaleString('ru-RU')}</p>
                        </div>
                    `;
                } else {
                    // Показываем ошибку
                    let errorMessage = data.error || 'Произошла ошибка при отправке работы';

                    if (data.errors && data.errors.lesson_url) {
                        errorMessage = data.errors.lesson_url.join(', ');
                    }

                    errorsDiv.innerHTML = `<div class="error-message">${errorMessage}</div>`;
                    urlInput.classList.add('error');
                    this.showNotification(errorMessage, 'error');
                }
            } catch (error) {

                errorsDiv.innerHTML = '<div class="error-message">Произошла ошибка при отправке работы. Попробуйте позже.</div>';
                this.showNotification('Ошибка при отправке работы', 'error');
            } finally {
                // Разблокируем кнопку
                submitBtn.disabled = false;
                submitBtn.innerHTML = `
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                    </svg>
                    <span>Отправить работу</span>
                `;
            }
        });
    }

    // Показ уведомления
    showNotification(message, type = 'info') {

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Анимация появления
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Автоматическое скрытие
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Получение CSRF токена
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }

    // Инициализация табов для раздела "Мои работы"
    initSubmissionTabs() {
        const tabButtons = document.querySelectorAll('.submissions-tabs .tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        if (tabButtons.length === 0) return;

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetTab = this.dataset.tab;

                // Remove active class from all buttons
                tabButtons.forEach(btn => {
                    btn.classList.remove('active');
                });

                // Add active class to clicked button
                this.classList.add('active');

                // Hide all tab contents
                tabContents.forEach(content => {
                    content.style.display = 'none';
                });

                // Show target tab content
                const targetContent = document.getElementById(targetTab + '-tab');
                if (targetContent) {
                    targetContent.style.display = 'block';
                }
            });
        });
    }
}

// Утилиты для форматирования
const DashboardUtils = {
    // Форматирование числа с разделителями
    formatNumber(num) {
        return new Intl.NumberFormat('ru-RU').format(num);
    },

    // Форматирование времени
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (hours > 0) {
            return `${hours}ч ${minutes}м`;
        }
        return `${minutes}м`;
    },

    // Форматирование даты
    formatDate(date) {
        return new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        }).format(new Date(date));
    },

    // Форматирование относительного времени
    formatRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} дн. назад`;
        if (hours > 0) return `${hours} ч. назад`;
        if (minutes > 0) return `${minutes} мин. назад`;
        return 'Только что';
    }
};

window.DashboardUtils = DashboardUtils;

// Глобальная функция для показа уведомлений (используется в inline скриптах и других модулях)
window.showNotification = function(message, type = 'info') {

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
        font-weight: 600;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);

    // Автоматическое скрытие
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
};

/**
 * Initialize tabs for submissions section
 */
function initSubmissionTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length === 0) return;

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // Remove active class from all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.borderBottomColor = 'transparent';
                btn.style.color = '#6b7280';
            });

            // Add active class to clicked button
            this.classList.add('active');
            this.style.borderBottomColor = '#3b82f6';
            this.style.color = '#3b82f6';

            // Hide all tab contents
            tabContents.forEach(content => {
                content.style.display = 'none';
            });

            // Show target tab content
            const targetContent = document.getElementById(targetTab + '-tab');
            if (targetContent) {
                targetContent.style.display = 'block';
            }
        });
    });
}

// Initialize tabs on page load
document.addEventListener('DOMContentLoaded', function() {
    initSubmissionTabs();
});

// Initialize DashboardManager on all dashboard pages
document.addEventListener('DOMContentLoaded', function() {

    const dashboardManager = new DashboardManager();
    window.dashboardManager = dashboardManager; // Make it globally accessible
});
