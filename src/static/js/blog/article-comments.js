/**
 * Функции управления комментариями в статьях блога
 * 
 * Функциональность:
 * - Показ/скрытие форм ответа на комментарии
 * - Показ/скрытие форм редактирования комментариев
 * - Плавная прокрутка к формам
 * - Автофокус на полях ввода
 * - Копирование ссылок в буфер обмена
 */

(function() {
    'use strict';

    /**
     * Переключает видимость формы ответа на комментарий
     * @param {number} commentId - ID комментария
     */
    window.toggleReplyForm = function(commentId) {
        const replyForm = document.getElementById(`reply-form-${commentId}`);
        const allReplyForms = document.querySelectorAll('.comment-reply-form-revolutionary');
        const allEditForms = document.querySelectorAll('.comment-edit-form-revolutionary');
        
        if (!replyForm) {

            return;
        }
        
        // Скрываем все остальные формы ответов и редактирования
        allReplyForms.forEach(form => {
            if (form.id !== `reply-form-${commentId}`) {
                form.classList.add('hidden');
                form.style.display = 'none';
            }
        });
        
        allEditForms.forEach(form => {
            form.classList.add('hidden');
            form.style.display = 'none';
            const contentId = form.id.replace('edit-form-', 'content-');
            const content = document.getElementById(contentId);
            if (content) {
                content.style.display = 'block';
            }
        });
        
        // Переключаем текущую форму
        const isHidden = replyForm.classList.contains('hidden') || 
                        replyForm.style.display === 'none' || 
                        replyForm.style.display === '';
        
        if (isHidden) {
            replyForm.classList.remove('hidden');
            replyForm.style.display = 'block';
            
            // Плавная прокрутка к форме
            setTimeout(() => {
                replyForm.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
                
                // Фокус на textarea
                const textarea = replyForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                }
            }, 100);
        } else {
            replyForm.classList.add('hidden');
            replyForm.style.display = 'none';
        }
    };

    /**
     * Переключает видимость формы редактирования комментария
     * @param {number} commentId - ID комментария
     */
    window.toggleEditForm = function(commentId) {
        const editForm = document.getElementById(`edit-form-${commentId}`);
        const content = document.getElementById(`content-${commentId}`);
        const allReplyForms = document.querySelectorAll('.comment-reply-form-revolutionary');
        const allEditForms = document.querySelectorAll('.comment-edit-form-revolutionary');
        
        if (!editForm || !content) {

            return;
        }
        
        // Скрываем все формы ответов
        allReplyForms.forEach(form => {
            form.classList.add('hidden');
            form.style.display = 'none';
        });
        
        // Скрываем все остальные формы редактирования и показываем их контент
        allEditForms.forEach(form => {
            if (form.id !== `edit-form-${commentId}`) {
                form.classList.add('hidden');
                form.style.display = 'none';
                const contentId = form.id.replace('edit-form-', 'content-');
                const otherContent = document.getElementById(contentId);
                if (otherContent) {
                    otherContent.style.display = 'block';
                }
            }
        });
        
        // Переключаем текущую форму
        const isHidden = editForm.classList.contains('hidden') || 
                        editForm.style.display === 'none' || 
                        editForm.style.display === '';
        
        if (isHidden) {
            content.style.display = 'none';
            editForm.classList.remove('hidden');
            editForm.style.display = 'block';
            
            // Плавная прокрутка к форме
            setTimeout(() => {
                editForm.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
                
                // Фокус на textarea и перемещение курсора в конец
                const textarea = editForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                    // Перемещаем курсор в конец текста
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                }
            }, 100);
        } else {
            editForm.classList.add('hidden');
            editForm.style.display = 'none';
            content.style.display = 'block';
        }
    };

    /**
     * Копирует текст в буфер обмена и показывает визуальный фидбек
     * @param {string} text - Текст для копирования
     */
    window.copyToClipboard = function(text) {
        if (!navigator.clipboard) {

            fallbackCopyTextToClipboard(text);
            return;
        }
        
        navigator.clipboard.writeText(text).then(() => {
            showCopySuccess();
        }).catch(err => {

            fallbackCopyTextToClipboard(text);
        });
    };

    /**
     * Показывает визуальный фидбек успешного копирования
     */
    function showCopySuccess() {
        const btn = event.target.closest('.hero-share-btn') || 
                    event.target.closest('.share-btn-revolutionary');
        
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<span>✅</span>';
            btn.classList.add('copy-success');
            
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.classList.remove('copy-success');
            }, 2000);
        }
    }

    /**
     * Fallback метод копирования для старых браузеров
     * @param {string} text - Текст для копирования
     */
    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = '0';
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showCopySuccess();
            }
        } catch (err) {

        }
        
        document.body.removeChild(textArea);
    }

    /**
     * Инициализация обработчиков событий при загрузке страницы
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Обработка социальных ссылок
        const socialLinks = document.querySelectorAll('.social-link-hero');
        socialLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });

        // Обработка кнопок с data-action атрибутами
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;
            const commentId = target.dataset.commentId;

            if (action === 'toggle-reply') {
                window.toggleReplyForm(parseInt(commentId));
            } else if (action === 'toggle-edit') {
                window.toggleEditForm(parseInt(commentId));
            }
        });

        // Обработка кнопок копирования с data-copy-url
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[data-copy-url]');
            if (!target) return;

            const url = target.dataset.copyUrl;
            window.copyToClipboard(url);
        });
    });

})();
