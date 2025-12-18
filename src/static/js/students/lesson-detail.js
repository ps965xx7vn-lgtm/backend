/**
 * Lesson detail page functionality
 * Handles step expansion, improvement tracking, and resubmit functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Highlight first incomplete step and scroll to it
    initStepScrolling();
    
    // Track improvement steps checkboxes
    initImprovementTracking();
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
 * Get CSRF token from cookies
 */
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
