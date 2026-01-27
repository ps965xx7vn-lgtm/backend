/**
 * Article Detail Page JavaScript
 * Handles article interactions: copy, bookmark, report, comments
 */

// Show notification
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

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Ссылка скопирована!', 'success');
    }).catch(err => {

        showNotification('Ошибка копирования', 'error');
    });
}

// Bookmark article
// Bookmark toggling via AJAX when possible
function bookmarkArticle() {
    // kept for backward compatibility when called directly

}

// Report article
function reportArticle() {

}

// Helper to get CSRF cookie
function _getCookie(name) {
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

// Attach quick-action handlers (if the new markup is present)
document.addEventListener('DOMContentLoaded', function() {
    const containers = document.querySelectorAll('.quick-actions-revolutionary');
    containers.forEach(container => {
        const articleId = container.dataset.articleId;
        const toggleUrl = container.dataset.toggleBookmarkUrl || '/blog/api/toggle-bookmark/';
        const reportUrl = container.dataset.reportUrl || '/blog/api/report-article/';

        const printBtn = container.querySelector('.print-action');
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                window.print();
                // Show notification after print dialog closes
                setTimeout(() => {
                    showNotification('📄 Готово к печати', 'info');
                }, 500);
            });
        }

        const bookmarkBtn = container.querySelector('.bookmark-action');
        if (bookmarkBtn) {
            bookmarkBtn.addEventListener('click', async function() {
                const wasBookmarked = this.classList.contains('bookmarked');
                this.classList.toggle('bookmarked');
                
                const csrftoken = _getCookie('csrftoken');
                try {
                    const resp = await fetch(toggleUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Accept': 'application/json',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `article_id=${encodeURIComponent(articleId)}`
                    });
                    if (!resp.ok) {
                        this.classList.toggle('bookmarked');
                        showNotification('Ошибка при сохранении', 'error');

                    } else {
                        const data = await resp.json();
                        if (data.bookmarked) {
                            this.classList.add('bookmarked');
                            showNotification('✓ Добавлено в закладки', 'success');
                        } else {
                            this.classList.remove('bookmarked');
                            showNotification('Удалено из закладок', 'info');
                        }
                    }
                } catch (e) {
                    this.classList.toggle('bookmarked');
                    showNotification('Ошибка сети', 'error');

                }
            });
        }

        const reportBtn = container.querySelector('.report-action');
        if (reportBtn) {
            reportBtn.addEventListener('click', async function() {
                const reason = prompt('Опишите проблему (необязательно):');
                if (reason === null) return; // user cancelled
                
                const csrftoken = _getCookie('csrftoken');
                try {
                    const resp = await fetch(reportUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Accept': 'application/json',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `article_id=${encodeURIComponent(articleId)}&reason=${encodeURIComponent(reason || '')}`
                    });
                    if (resp.ok) {
                        showNotification('✓ Репорт отправлен', 'success');
                    } else {
                        showNotification('Ошибка при отправке', 'error');
                    }
                } catch (e) {

                    showNotification('Ошибка сети', 'error');
                }
            });
        }
    });
});

// Toggle reply form visibility
function toggleReplyForm(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (!form) return;
    
    // Hide all other reply forms
    document.querySelectorAll('.comment-reply-form-revolutionary').forEach(f => {
        if (f.id !== `reply-form-${commentId}`) {
            f.classList.add('hidden');
        }
    });
    
    // Toggle current form
    form.classList.toggle('hidden');
    
    // Focus on textarea if form is shown
    if (!form.classList.contains('hidden')) {
        const textarea = form.querySelector('textarea');
        if (textarea) textarea.focus();
    }
}

// Toggle edit form visibility
function toggleEditForm(commentId) {
    const form = document.getElementById(`edit-form-${commentId}`);
    if (!form) return;
    
    // Hide all other edit forms
    document.querySelectorAll('.comment-edit-form-revolutionary').forEach(f => {
        if (f.id !== `edit-form-${commentId}`) {
            f.classList.add('hidden');
        }
    });
    
    // Toggle current form
    form.classList.toggle('hidden');
    
    // Focus on textarea if form is shown
    if (!form.classList.contains('hidden')) {
        const textarea = form.querySelector('textarea');
        if (textarea) textarea.focus();
    }
}

// Validate comment form
function validateCommentForm(form) {
    const textarea = form.querySelector('textarea[name="content"]');
    if (!textarea) return true;
    
    const content = textarea.value.trim();
    
    if (content.length === 0) {
        showNotification('Комментарий не может быть пустым', 'error');
        textarea.focus();
        return false;
    }
    
    if (content.length < 3) {
        showNotification('Комментарий слишком короткий. Минимум 3 символа.', 'error');
        textarea.focus();
        return false;
    }
    
    if (content.length > 5000) {
        showNotification('Комментарий слишком длинный. Максимум 5000 символов.', 'error');
        textarea.focus();
        return false;
    }
    
    return true;
}

// Initialize delete confirmations with data attributes
document.addEventListener('DOMContentLoaded', function() {
    // Comment/reply delete forms
    document.querySelectorAll('form[data-confirm-delete]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.dataset.confirmDelete || 'Вы уверены, что хотите удалить?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Validate main comment form
    const mainCommentForm = document.getElementById('mainCommentForm');
    if (mainCommentForm) {
        mainCommentForm.addEventListener('submit', function(e) {
            if (!validateCommentForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Validate all reply forms
    document.querySelectorAll('.reply-form-revolutionary, .edit-form-revolutionary').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateCommentForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// Export functions to window for onclick usage
window.toggleReplyForm = toggleReplyForm;
window.toggleEditForm = toggleEditForm;
