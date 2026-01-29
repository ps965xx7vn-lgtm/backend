/**
 * Lesson detail page functionality
 * Handles step expansion, improvement tracking, and resubmit functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Highlight first incomplete step and scroll to it
    initStepScrolling();

    // Track improvement steps checkboxes
    initImprovementTracking();

    // Initialize self-check items checkboxes
    initSelfCheckItems();

    // Initialize troubleshooting accordions
    initTroubleshootingAccordions();
});

/**
 * Initialize scrolling to first incomplete step
 */
function initStepScrolling() {
    const firstIncompleteStep = document.querySelector('.step-card:not(.completed)');
    if (firstIncompleteStep) {
        firstIncompleteStep.classList.add('expanded');
        setTimeout(() => {
            firstIncompleteStep.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 500);
    }
}

/**
 * Initialize improvement steps tracking with checkboxes
 */
function initImprovementTracking() {
    const improvementCheckboxes = document.querySelectorAll('.improvement-step-checkbox');
    const resubmitBtn = document.getElementById('resubmit-work-btn');
    const progressText = document.getElementById('improvement-progress-text');
    const resubmitForm = document.getElementById('lesson-resubmit-form');

    if (improvementCheckboxes.length === 0 || !resubmitBtn) {
        return;
    }

    const totalSteps = improvementCheckboxes.length;
    let wasAllChecked = false; // Track if all steps were completed

    /**
     * Update progress text and button state
     * @param {boolean} showCompletionNotification - Whether to show completion notification
     */
    function updateProgress(showCompletionNotification = true) {
        try {
            const checkedSteps = document.querySelectorAll('.improvement-step-checkbox:checked').length;
            const allChecked = checkedSteps === totalSteps;

            // Update button state
            resubmitBtn.disabled = !allChecked;

            // Update progress text
            if (progressText) {
                if (allChecked) {
                    progressText.innerHTML = '✅ Все шаги доработки выполнены! Можно отправлять работу <strong>(' + checkedSteps + '/' + totalSteps + ')</strong>';
                } else {
                    progressText.innerHTML = 'Отметьте все шаги доработки выше, чтобы отправить работу <strong>(' + checkedSteps + '/' + totalSteps + ')</strong>';
                }
            }

            // Show notification only when all steps are completed for the first time
            if (allChecked && !wasAllChecked) {
                window.showNotification('🎉 Все шаги доработки выполнены! Можно отправлять работу', 'success');
                wasAllChecked = true;
            } else if (!allChecked && wasAllChecked) {
                wasAllChecked = false;
            }
        } catch (error) {

        }
    }

    // Listen to checkbox changes
    improvementCheckboxes.forEach(function(checkbox, index) {

        checkbox.addEventListener('change', function(e) {

            e.stopPropagation();

            const improvementId = e.target.dataset.improvementId;
            const isChecked = e.target.checked;

            // Save to server
            saveImprovementState(improvementId, isChecked);

            updateProgress();
        });

        // Also add click handler to container
        const container = checkbox.closest('.step-checkbox-container');
        if (container) {
            container.addEventListener('click', function(e) {

                if (e.target === container || e.target.closest('.step-checkbox-custom')) {
                    const wasChecked = checkbox.checked;
                    checkbox.checked = !wasChecked;

                    const improvementId = checkbox.dataset.improvementId;
                    const isChecked = checkbox.checked;

                    // Save to server
                    saveImprovementState(improvementId, isChecked);

                    updateProgress();
                }
            });
        }
    });

    // Initial update without notification

    updateProgress(false);

    /**
     * Save improvement completion state to server
     * @param {string} improvementId - UUID of the improvement
     * @param {boolean} isChecked - Whether the checkbox is checked
     */
    function saveImprovementState(improvementId, isChecked) {
        console.log('Saving improvement state:', improvementId, isChecked);

        // Get current language prefix from URL (e.g., /ru/, /en/, /ka/)
        const pathParts = window.location.pathname.split('/');
        const langPrefix = ['ru', 'en', 'ka'].includes(pathParts[1]) ? `/${pathParts[1]}` : '';

        fetch(`${langPrefix}/students/api/toggle-improvement/${improvementId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                // Check if all improvements are now completed
                const allCheckboxes = document.querySelectorAll('.improvement-step-checkbox');
                const allChecked = Array.from(allCheckboxes).every(cb => cb.checked);

                // Show notification
                if (isChecked && allChecked) {
                    // Don't show individual notification, updateProgress will show completion message
                } else if (isChecked) {
                    window.showNotification('Шаг доработки отмечен как выполненный', 'success');
                } else {
                    window.showNotification('Отметка снята', 'info');
                }
            } else {
                window.showNotification('Ошибка при сохранении', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving improvement state:', error);
            window.showNotification('Ошибка при сохранении: ' + error.message, 'error');
        });
    }
}

/**
 * Get CSRF token from cookies or meta tag
 */
function getCookie(name) {
    // First try to get from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken && name === 'csrftoken') {
        const token = metaToken.getAttribute('content');
        if (token) {
            return token;
        }
    }

    // Fallback to cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

/**
 * Mark step as completed via Django view (session-based auth)
 * @param {string} stepId - UUID of the step
 * @param {string} courseSlug - Course slug
 * @param {string} lessonSlug - Lesson slug
 * @returns {Promise}
 */
async function markStepAsCompleted(stepId, courseSlug, lessonSlug) {
    // Get language prefix from current URL
    const pathParts = window.location.pathname.split('/');
    const langPrefix = ['ru', 'en', 'ka'].includes(pathParts[1]) ? `/${pathParts[1]}` : '';

    // Use Django view endpoint (with session auth)
    const url = `${langPrefix}/students/courses/${courseSlug}/lessons/${lessonSlug}/steps/${stepId}/toggle/`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ completed: true })  // Устанавливаем как выполненный
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error('[markStepAsCompleted] Error:', response.status, errorText.substring(0, 200));
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Initialize troubleshooting help accordions
 */
function initTroubleshootingAccordions() {
    const accordions = document.querySelectorAll('.step-troubleshooting-accordion');

    accordions.forEach(accordion => {
        const header = accordion.querySelector('.troubleshooting-header');
        const content = accordion.querySelector('.step-accordion-content');

        if (header && content) {
            header.addEventListener('click', function() {
                // Toggle expanded class
                accordion.classList.toggle('expanded');

                // Toggle content visibility with smooth animation
                if (accordion.classList.contains('expanded')) {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        }
    });
}

/**
 * Initialize self-check items functionality with checkboxes and next step button
 */
function initSelfCheckItems() {
    const selfCheckContainers = document.querySelectorAll('.self-check-items');

    selfCheckContainers.forEach(container => {
        const stepId = container.dataset.stepId;
        const checkboxes = container.querySelectorAll('.self-check-checkbox');
        const nextStepBtn = container.querySelector('.btn-next-step');
        const checkedCountEl = container.querySelector('.checked-count');
        const totalCountEl = container.querySelector('.total-count');

        if (checkboxes.length === 0) return;

        // Load saved state from localStorage
        const savedState = localStorage.getItem(`self-check-${stepId}`);
        if (savedState) {
            try {
                const checkedIndexes = JSON.parse(savedState);
                checkboxes.forEach((checkbox, index) => {
                    if (checkedIndexes.includes(index)) {
                        checkbox.checked = true;
                    }
                });
            } catch (e) {
                console.error('Error loading saved state:', e);
            }
        }

        /**
         * Update progress counter and button visibility
         */
        function updateSelfCheckProgress() {
            const checkedCount = container.querySelectorAll('.self-check-checkbox:checked').length;
            const totalCount = checkboxes.length;
            const allChecked = checkedCount === totalCount;

            // Update counter
            if (checkedCountEl) checkedCountEl.textContent = checkedCount;
            if (totalCountEl) totalCountEl.textContent = totalCount;

            // Show/hide next step button
            if (nextStepBtn) {
                nextStepBtn.style.display = allChecked ? 'block' : 'none';
            }

            // Save state to localStorage
            const checkedIndexes = [];
            checkboxes.forEach((checkbox, index) => {
                if (checkbox.checked) {
                    checkedIndexes.push(index);
                }
            });
            localStorage.setItem(`self-check-${stepId}`, JSON.stringify(checkedIndexes));
        }

        // Listen to checkbox changes
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSelfCheckProgress);
        });

        // Next step button click handler
        if (nextStepBtn) {
            nextStepBtn.addEventListener('click', async function() {
                // Get course and lesson slugs from button data attributes
                const courseSlug = nextStepBtn.dataset.courseSlug;
                const lessonSlug = nextStepBtn.dataset.lessonSlug;

                // Find next step card
                const currentStepCard = container.closest('.step-card');
                if (currentStepCard) {
                    const allSteps = document.querySelectorAll('.step-card');
                    const currentIndex = Array.from(allSteps).indexOf(currentStepCard);

                    if (currentIndex >= 0 && currentIndex < allSteps.length - 1) {
                        const nextStep = allSteps[currentIndex + 1];

                        // Отмечаем текущий шаг как выполненный
                        try {
                            const response = await markStepAsCompleted(stepId, courseSlug, lessonSlug);

                            // Проверяем что запрос успешен
                            if (response && response.success) {
                                // Визуально отмечаем шаг как завершённый
                                currentStepCard.classList.add('completed');

                                // Обновляем бейдж статуса в правой части
                                const notCompletedBadge = currentStepCard.querySelector('.step-badge.not-completed');
                                if (notCompletedBadge) {
                                    notCompletedBadge.className = 'step-badge completed';
                                    notCompletedBadge.innerHTML = `
                                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        <span>Выполнено</span>
                                    `;
                                }

                                // Отмечаем чекбокс - обновляем визуально
                                const sidebarCheckbox = currentStepCard.querySelector('.step-checkbox');
                                if (sidebarCheckbox && !sidebarCheckbox.checked) {
                                    // Временно удаляем обработчики событий чтобы избежать рекурсии
                                    const oldCheckbox = sidebarCheckbox.cloneNode(true);
                                    sidebarCheckbox.parentNode.replaceChild(oldCheckbox, sidebarCheckbox);
                                    oldCheckbox.checked = true;
                                }

                                // Обновляем счётчик из ответа сервера
                                if (response.lesson_progress) {
                                    const completedStepsCounter = document.querySelector('.lesson-completed-steps');
                                    if (completedStepsCounter) {
                                        completedStepsCounter.textContent = response.lesson_progress.completed_steps;
                                    }

                                    // Обновляем прогресс-бар урока
                                    const progressPercentage = response.lesson_progress.completion_percentage;
                                    const progressBar = document.querySelector('.lesson-progress-fill');
                                    const progressPercentageElem = document.querySelector('.progress-percentage');

                                    if (progressBar) {
                                        progressBar.style.width = `${progressPercentage}%`;
                                    }
                                    if (progressPercentageElem) {
                                        progressPercentageElem.textContent = `${progressPercentage}%`;
                                    }
                                }
                            } else {
                                console.error('[Next Step] API returned unsuccessfull response:', response);
                            }

                            // Обновляем счётчик выполненных шагов
                            const completedStepsCounter = document.querySelector('.lesson-completed-steps');
                            if (completedStepsCounter) {
                                const currentCount = parseInt(completedStepsCounter.textContent) || 0;
                                completedStepsCounter.textContent = currentCount + 1;
                            }

                            // Обновляем прогресс-бар урока
                            const totalSteps = parseInt(document.querySelector('.lesson-total-steps')?.textContent) || 0;
                            const newCompleted = (parseInt(completedStepsCounter?.textContent) || 0);
                            const progressPercentage = totalSteps > 0 ? Math.round((newCompleted / totalSteps) * 100) : 0;

                            const progressBar = document.querySelector('.lesson-progress-fill');
                            const progressPercentageElem = document.querySelector('.progress-percentage');

                            if (progressBar) {
                                progressBar.style.width = `${progressPercentage}%`;
                            }
                            if (progressPercentageElem) {
                                progressPercentageElem.textContent = `${progressPercentage}%`;
                            }

                        } catch (error) {
                            console.error('Error marking step as completed:', error);
                        }

                        // Collapse current step
                        currentStepCard.classList.remove('expanded');

                        // Expand next step
                        nextStep.classList.add('expanded');

                        // Scroll to next step (к началу карточки, не к действиям)
                        setTimeout(() => {
                            // Скроллим к шапке карточки
                            nextStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            // Добавляем небольшой отступ сверху
                            window.scrollBy(0, -20);
                        }, 300);

                        // Show success notification
                        if (window.showNotification) {
                            window.showNotification('✅ Переход к следующему шагу', 'success');
                        }
                    } else {
                        // Last step - show completion message
                        if (window.showNotification) {
                            window.showNotification('🎉 Вы достигли последнего шага урока!', 'success');
                        }
                    }
                }
            });
        }

        // Initial update
        updateSelfCheckProgress();
    });
}
