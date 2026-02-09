/**
 * Submission Review Page - JavaScript
 * Handles improvement additions, character counter, and status changes
 */

(function() {
    'use strict';

    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initReviewPage);
    } else {
        initReviewPage();
    }

    function initReviewPage() {

        // Character counter for comments
        initCharacterCounter();

        // Add improvement functionality
        initImprovements();

        // Status radio listeners
        initStatusRadios();

        // Form validation
        initFormValidation();

    }

    function initCharacterCounter() {
        const commentsTextarea = document.getElementById('comments');
        const charCountSpan = document.getElementById('charCount');

        if (commentsTextarea && charCountSpan) {
            commentsTextarea.addEventListener('input', function() {
                charCountSpan.textContent = this.value.length;
            });
        } else {
        }
    }

    function initImprovements() {
        let improvementCounter = 0;
        const maxImprovements = 10;

        const addBtn = document.getElementById('addImprovementBtn');
        const container = document.getElementById('improvementsContainer');

        if (!addBtn) {
            return;
        }

        if (!container) {
            return;
        }

        // Add click listener
        addBtn.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();

            if (improvementCounter >= maxImprovements) {
                alert('Максимум 10 предложений по улучшению');
                return;
            }

            improvementCounter++;

            const improvementDiv = document.createElement('div');
            improvementDiv.className = 'review-improvement-item';
            improvementDiv.innerHTML =
                '<div class="review-improvement-header">' +
                    '<div class="review-improvement-label">' +
                        '<span class="review-improvement-text">Улучшение ' + improvementCounter + '</span>' +
                    '</div>' +
                    '<button type="button" class="review-improvement-remove" data-remove-improvement>' +
                        '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>' +
                        '</svg>' +
                    '</button>' +
                '</div>' +
                '<input type="text" name="improvement_title_' + improvementCounter + '" class="review-improvement-title-input" ' +
                    'placeholder="Название шага (например: Добавить проверку на пустые значения)" required>' +
                '<textarea name="improvement_text_' + improvementCounter + '" class="review-improvement-textarea" ' +
                    'placeholder="Опишите конкретное предложение по улучшению" required></textarea>';

            container.appendChild(improvementDiv);

            // Add remove listener to the new button
            const removeBtn = improvementDiv.querySelector('[data-remove-improvement]');
            removeBtn.addEventListener('click', function() {
                removeImprovement(this);
            });

            // Update section header with counter
            updateSectionHeader(improvementCounter, maxImprovements);

            if (improvementCounter >= maxImprovements) {
                addBtn.disabled = true;
                addBtn.style.opacity = '0.5';
            }
        });

        // Remove improvement function
        function removeImprovement(button) {
            const improvementItem = button.closest('.review-improvement-item');
            if (!improvementItem) return;

            improvementItem.remove();
            improvementCounter--;

            // Renumber remaining improvements
            const remainingItems = document.querySelectorAll('.review-improvement-item');
            remainingItems.forEach(function(item, index) {
                const numberSpan = item.querySelector('.review-improvement-number');
                const textarea = item.querySelector('textarea');
                numberSpan.textContent = index + 1;
                textarea.name = 'improvement_' + (index + 1);
            });

            // Re-enable button if below max
            if (improvementCounter < maxImprovements && addBtn) {
                addBtn.disabled = false;
                addBtn.style.opacity = '1';
            }

            // Update section header
            updateSectionHeader(improvementCounter, maxImprovements);
        }

        // Update section header with correct declension
        function updateSectionHeader(count, max) {
            const counterSpan = document.getElementById('improvementsCounter');
            if (!counterSpan) return;

            let text;
            if (count === 0) {
                text = '';
            } else if (count === 1) {
                text = '(1 улучшение)';
            } else if (count >= 2 && count <= 4) {
                text = '(' + count + ' улучшения)';
            } else {
                text = '(' + count + ' улучшений)';
            }

            counterSpan.textContent = text;
        }
    }

    function initStatusRadios() {
        const statusRadios = document.querySelectorAll('input[name="status"]');
        const improvementsRequiredBadge = document.querySelector('.review-improvements-required');
        const improvementsSection = document.getElementById('improvementsSection');
        const formActions = document.querySelector('.review-form-actions');

        if (statusRadios.length) {
            statusRadios.forEach(function(radio) {
                radio.addEventListener('change', function() {
                    const isChangesRequested = this.value === 'changes_requested';

                    // Show/hide required badge
                    if (improvementsRequiredBadge) {
                        improvementsRequiredBadge.style.display = isChangesRequested ? 'inline' : 'none';
                    }

                    // Show/hide entire improvements section
                    if (improvementsSection) {
                        improvementsSection.style.display = isChangesRequested ? 'block' : 'none';
                    }

                    // Toggle class on form actions to remove border
                    if (formActions) {
                        if (isChangesRequested) {
                            formActions.classList.remove('no-border-top');
                        } else {
                            formActions.classList.add('no-border-top');
                        }
                    }
                });
            });

            // Initially hide improvements section and add no-border class
            if (improvementsSection) {
                improvementsSection.style.display = 'none';
            }

            if (formActions) {
                formActions.classList.add('no-border-top');
            }

        } else {
        }
    }

    function initFormValidation() {
        const form = document.getElementById('reviewForm');

        if (!form) {
            return;
        }

        form.addEventListener('submit', function(event) {

            // Get form values
            const statusRadio = document.querySelector('input[name="status"]:checked');
            const commentsTextarea = document.getElementById('comments');
            const improvementsContainer = document.getElementById('improvementsContainer');

            // Check if status is selected
            if (!statusRadio) {
                event.preventDefault();
                showNotification('Выберите статус проверки', 'error');
                return false;
            }

            const status = statusRadio.value;
            const comments = commentsTextarea ? commentsTextarea.value.trim() : '';

            // Check comments length
            if (comments.length < 20) {
                event.preventDefault();
                showNotification('Комментарии должны содержать минимум 20 символов', 'error');
                commentsTextarea.focus();
                return false;
            }

            // If changes_requested, check improvements
            if (status === 'changes_requested') {
                const improvements = improvementsContainer.querySelectorAll('.review-improvement-item');

                if (improvements.length === 0) {
                    event.preventDefault();
                    showNotification('Для доработок необходимо добавить минимум 1 улучшение', 'error');
                    return false;
                }

                // Check each improvement has content
                let hasEmptyImprovement = false;
                improvements.forEach(function(item, index) {
                    const textarea = item.querySelector('textarea');
                    if (textarea) {
                        const text = textarea.value.trim();
                        if (text.length < 10) {
                            hasEmptyImprovement = true;
                        }
                    }
                });

                if (hasEmptyImprovement) {
                    event.preventDefault();
                    showNotification('Каждое улучшение должно содержать минимум 10 символов', 'error');
                    return false;
                }
            }

            showNotification('Отправка проверки...', 'info');
            return true;
        });

    }
})();
