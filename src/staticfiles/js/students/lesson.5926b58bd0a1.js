/**
 * Lesson Steps Functionality
 * Handles step accordion, nested accordions, and step interactions
 */

// Show notification function (from blog)
function showNotification(message, type = 'info') {
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
}

document.addEventListener('DOMContentLoaded', function() {

    // Step accordion toggle
    const stepHeaders = document.querySelectorAll('.step-header');
    stepHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            if (e.target.closest('.step-checkbox-container')) {
                return;
            }
            
            const stepCard = this.closest('.step-card');
            const isExpanded = stepCard.classList.contains('expanded');
            
            if (isExpanded) {
                stepCard.classList.remove('expanded');

            } else {
                stepCard.classList.add('expanded');

                // Добавляем кнопки копирования к code blocks после раскрытия
                setTimeout(() => {
                    if (window.addCopyButtonsToCodeBlocks) {

                        window.addCopyButtonsToCodeBlocks();
                    }
                }, 100);
            }
        });
    });

    // Expand all / Collapse all buttons
    const expandAllBtn = document.getElementById('expand-all-steps');
    const collapseAllBtn = document.getElementById('collapse-all-steps');
    
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', function() {

            document.querySelectorAll('.step-card').forEach(card => {
                card.classList.add('expanded');
            });
            
            // Добавляем кнопки копирования после раскрытия всех шагов
            setTimeout(() => {
                if (window.addCopyButtonsToCodeBlocks) {

                    window.addCopyButtonsToCodeBlocks();
                }
            }, 100);
        });
    }
    
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {

            document.querySelectorAll('.step-card').forEach(card => {
                card.classList.remove('expanded');
            });
        });
    }

    // Nested accordion for Tips and ExtraSources
    document.querySelectorAll('.step-accordion-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.stopPropagation(); // Не закрывать родительский аккордеон
            
            const accordionItem = this.closest('.step-accordion-item');
            const content = accordionItem.querySelector('.step-accordion-content');
            const icon = this.querySelector('.accordion-toggle-icon');
            
            const isVisible = content.style.display !== 'none';
            
            if (isVisible) {
                // Закрыть
                content.style.display = 'none';
                icon.style.transform = 'rotate(0deg)';

            } else {
                // Открыть
                content.style.display = 'block';
                icon.style.transform = 'rotate(180deg)';

            }
        });
    });

    // Copy code functionality
    document.querySelectorAll('.copy-code').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const code = this.dataset.code;
            navigator.clipboard.writeText(code).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = `
                    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                    Скопировано!
                `;
                this.classList.add('copied');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('copied');
                }, 2000);
            });
        });
    });

    // Resubmit form handler (for changes_requested status)
    const resubmitForm = document.getElementById('lesson-resubmit-form');
    if (resubmitForm) {
        resubmitForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('resubmit-work-btn');
            const errorsDiv = document.getElementById('resubmission-errors');
            const urlInput = document.getElementById('id_resubmit_url');
            const submitUrl = resubmitForm.dataset.submitUrl;
            
            // Clear previous errors
            if (errorsDiv) errorsDiv.innerHTML = '';
            
            // Disable button
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>⏳ Отправка...</span>';
            
            try {
                const formData = new FormData(resubmitForm);
                
                const response = await fetch(submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message || 'Работа успешно отправлена!', 'success');
                    // Success - reload page to show updated submission
                    setTimeout(() => location.reload(), 1000);
                } else {
                    // Show errors
                    let errorMessage = '';
                    if (data.errors) {
                        if (typeof data.errors === 'object') {
                            errorMessage = Object.values(data.errors).flat().join(', ');
                        } else {
                            errorMessage = data.errors;
                        }
                    } else if (data.error) {
                        errorMessage = data.error;
                    } else {
                        errorMessage = 'Произошла ошибка при отправке';
                    }
                    
                    showNotification(errorMessage, 'error');
                    if (errorsDiv) {
                        errorsDiv.innerHTML = `<div class="alert alert-danger" role="alert">${errorMessage}</div>`;
                    }
                    
                    // Re-enable button
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            } catch (error) {

                const errorMsg = 'Произошла ошибка при отправке';
                showNotification(errorMsg, 'error');
                if (errorsDiv) {
                    errorsDiv.innerHTML = `<div class="alert alert-danger" role="alert">${errorMsg}</div>`;
                }
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Toggle edit form visibility
    const editButtons = document.querySelectorAll('.btn-edit-submission');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const formId = this.dataset.formId;
            const form = document.getElementById(formId);
            if (form) {
                const isHidden = form.style.display === 'none' || !form.style.display;
                form.style.display = isHidden ? 'block' : 'none';
                this.textContent = isHidden ? '❌ Отменить' : '✏️ Изменить ссылку';
            }
        });
    });

    // Handle all edit forms submission (for pending, in_review, approved)
    const editForms = document.querySelectorAll('.submission-resubmit-form');
    editForms.forEach(form => {
        if (form.id !== 'lesson-resubmit-form') { // Skip the main resubmit form as it's handled above
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const submitBtn = this.querySelector('button[type="submit"]');
                const errorsDiv = this.querySelector('.form-errors');
                const submitUrl = this.dataset.submitUrl;
                
                // Clear previous errors
                if (errorsDiv) errorsDiv.innerHTML = '';
                
                // Disable button
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>⏳ Сохранение...</span>';
                
                try {
                    const formData = new FormData(this);
                    
                    const response = await fetch(submitUrl, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showNotification(data.message || 'Ссылка успешно обновлена!', 'success');
                        // Success - reload page to show updated submission
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        // Show errors
                        let errorMessage = '';
                        if (data.errors) {
                            if (typeof data.errors === 'object') {
                                errorMessage = Object.values(data.errors).flat().join(', ');
                            } else {
                                errorMessage = data.errors;
                            }
                        } else if (data.error) {
                            errorMessage = data.error;
                        } else {
                            errorMessage = 'Произошла ошибка при сохранении';
                        }
                        
                        showNotification(errorMessage, 'error');
                        if (errorsDiv) {
                            errorsDiv.innerHTML = `<div class="alert alert-danger" role="alert">${errorMessage}</div>`;
                        }
                        
                        // Re-enable button
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalBtnText;
                    }
                } catch (error) {

                    const errorMsg = 'Произошла ошибка при сохранении';
                    showNotification(errorMsg, 'error');
                    if (errorsDiv) {
                        errorsDiv.innerHTML = `<div class="alert alert-danger" role="alert">${errorMsg}</div>`;
                    }
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            });
        }
    });

});

// Helper function to get CSRF token
function getCookie(name) {
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
