/**
 * Lesson submission form handling
 * Handles homework submission, resubmission, and editing for lessons
 * Version: 2.2.0
 */

// Основная инициализация обработчиков форм
document.addEventListener('DOMContentLoaded', function() {
    // Главная форма отправки работы
    initMainSubmissionForm();

    // Форма повторной отправки
    initResubmitForm();

    // Кнопки редактирования и их формы
    initEditButtons();
});

/**
 * Главная форма отправки работы (первая отправка)
 */
function initMainSubmissionForm() {
    const submissionForm = document.getElementById('lesson-submission-form');
    if (!submissionForm) {
        return;
    }

    submissionForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-work-btn');
        const urlInput = document.getElementById('id_lesson_url');
        const errorsDiv = document.getElementById('submission-errors');

        if (!submitBtn || !urlInput || !errorsDiv) {
            console.error('Не найдены элементы главной формы:', {submitBtn, urlInput, errorsDiv});
            return;
        }

        await handleSubmission(urlInput, submitBtn, errorsDiv, 'submit-work-btn');
    });
}

/**
 * Форма повторной отправки (после изменений от ментора)
 */
function initResubmitForm() {
    const resubmitForm = document.getElementById('lesson-resubmit-form');
    if (!resubmitForm) {
        return;
    }

    resubmitForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('resubmit-work-btn');
        const urlInput = document.getElementById('id_resubmit_url');
        const errorsDiv = document.getElementById('resubmission-errors');

        if (!submitBtn || !urlInput || !errorsDiv) {
            console.error('Не найдены элементы формы resubmit:', {submitBtn, urlInput, errorsDiv});
            return;
        }

        await handleSubmission(urlInput, submitBtn, errorsDiv, 'resubmit-work-btn');
    });
}

/**
 * Кнопки "Изменить ссылку" и их скрытые формы
 */
function initEditButtons() {
    const editButtons = document.querySelectorAll('.btn-edit-submission');

    editButtons.forEach((button) => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const formId = this.dataset.formId;
            const form = document.getElementById(formId);

            if (form) {
                const currentDisplay = window.getComputedStyle(form).display;

                if (currentDisplay === 'none' || form.style.display === 'none') {
                    form.style.display = 'block';
                    form.style.visibility = 'visible';
                    form.style.opacity = '1';
                } else {
                    form.style.display = 'none';
                }
            } else {
                console.error('Form not found:', formId);
            }
        });
    });

    // Обработчик для формы редактирования (pending status)
    const editFormPending = document.getElementById('edit-form-pending');

    if (editFormPending) {
        editFormPending.addEventListener('submit', async function(e) {
            e.preventDefault();

            const urlInput = this.querySelector('input[name="lesson_url"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            const errorsDiv = document.getElementById('edit-errors-pending');

            if (!urlInput || !submitBtn || !errorsDiv) {
                console.error('❌ Не найдены элементы формы edit:', {urlInput, submitBtn, errorsDiv});
                return;
            }

            await handleSubmission(urlInput, submitBtn, errorsDiv, null);
        });
    } else {
        console.log('⚠️ Форма edit-form-pending не найдена (возможно, нет pending submission)');
    }

    console.log('=== initEditButtons END ===');
}

/**
 * Общая функция обработки отправки работы
 * @param {HTMLInputElement} urlInput - Поле ввода URL
 * @param {HTMLButtonElement} submitBtn - Кнопка отправки
 * @param {HTMLElement} errorsDiv - Блок для отображения ошибок
 * @param {string|null} buttonId - ID кнопки для логирования
 */
async function handleSubmission(urlInput, submitBtn, errorsDiv, buttonId) {
    console.log('🔄 handleSubmission START');
    console.log('- urlInput:', urlInput);
    console.log('- submitBtn:', submitBtn);
    console.log('- errorsDiv:', errorsDiv);

    const lessonUrl = urlInput.value.trim();
    console.log('- lessonUrl:', lessonUrl);

    // Валидация URL (GitHub или CodeHS)
    const isGitHub = lessonUrl.match(/^https:\/\/github\.com\/.+/);
    const isCodeHS = lessonUrl.match(/^https:\/\/codehs\.com\/(sandbox|share)\/.+/);

    if (!isGitHub && !isCodeHS) {
        console.warn('⚠️ Невалидная ссылка');
        errorsDiv.innerHTML = '<div class="error-message">Пожалуйста, укажите корректную ссылку на CodeHS или GitHub</div>';
        urlInput.classList.add('error');

        if (window.showNotification) {
            window.showNotification('Пожалуйста, укажите корректную ссылку на CodeHS или GitHub', 'error');
        } else {
            alert('Пожалуйста, укажите корректную ссылку на CodeHS или GitHub');
        }
        return;
    }

    // Получаем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    console.log('- CSRF token:', csrfToken ? '✅ Found' : '❌ NOT FOUND');

    if (!csrfToken) {
        console.error('❌ CSRF токен не найден');
        errorsDiv.innerHTML = '<div class="error-message">Ошибка: отсутствует CSRF токен</div>';

        if (window.showNotification) {
            window.showNotification('Ошибка: отсутствует CSRF токен', 'error');
        } else {
            alert('Ошибка: отсутствует CSRF токен');
        }
        return;
    }

    // Формируем URL для отправки
    const currentPath = window.location.pathname;
    const submitUrl = currentPath + (currentPath.endsWith('/') ? '' : '/') + 'submit/';
    console.log('📤 URL для отправки:', submitUrl);

    // Блокируем кнопку и показываем загрузку
    const originalButtonHTML = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner">⏳</span> Отправка...';
    console.log('🔒 Кнопка заблокирована');

    // Очищаем предыдущие ошибки
    errorsDiv.innerHTML = '';
    urlInput.classList.remove('error');

    try {
        const formData = new FormData();
        formData.append('lesson_url', lessonUrl);

        console.log('📨 Отправка запроса...');
        console.log('📨 Method: POST');
        console.log('📨 Body:', {lesson_url: lessonUrl});

        const response = await fetch(submitUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        console.log('📥 Ответ получен!');
        console.log('📥 Status:', response.status);
        console.log('📥 Status Text:', response.statusText);

        // Проверяем Content-Type перед парсингом
        const contentType = response.headers.get('content-type');
        console.log('📥 Content-Type:', contentType);

        let data;
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
            console.log('📥 Data:', data);
        } else {
            // Если пришел не JSON (например, HTML с ошибкой), читаем как текст
            const text = await response.text();
            console.error('❌ Получен не JSON ответ:', text.substring(0, 200));
            throw new Error('Сервер вернул некорректный ответ. Попробуйте обновить страницу и попробовать снова.');
        }

        if (response.ok && data.success) {
            console.log('✅ SUCCESS! Response OK and data.success=true');

            // Очищаем ошибки
            errorsDiv.innerHTML = '';
            urlInput.classList.remove('error');

            // Показываем уведомление об успехе
            const successMessage = data.message || 'Работа успешно отправлена!';
            console.log('📢 Showing success notification:', successMessage);

            if (window.showNotification) {
                window.showNotification(successMessage, 'success');
            } else {
                alert(successMessage);
            }

            // Перезагружаем страницу чтобы показать обновленный статус
            console.log('🔄 Reloading page in 1.5s...');
            setTimeout(() => {
                window.location.reload();
            }, 1500);

        } else {
            console.error('❌ ERROR Response:', {
                ok: response.ok,
                status: response.status,
                success: data.success,
                error: data.error,
                errors: data.errors
            });

            // Показываем ошибку
            let errorMessage = data.error || 'Произошла ошибка при отправке работы';

            if (data.errors && data.errors.lesson_url) {
                errorMessage = Array.isArray(data.errors.lesson_url)
                    ? data.errors.lesson_url.join(', ')
                    : data.errors.lesson_url;
            }

            console.error('📢 Error message:', errorMessage);
            errorsDiv.innerHTML = `<div class="error-message">${errorMessage}</div>`;
            urlInput.classList.add('error');

            if (window.showNotification) {
                window.showNotification(errorMessage, 'error');
            } else {
                alert(errorMessage);
            }

            // Разблокируем кнопку
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalButtonHTML;
        }
    } catch (error) {
        console.error('❌ CATCH ERROR:', error);
        console.error('Stack:', error.stack);

        const errorMsg = 'Произошла ошибка при отправке работы: ' + error.message;
        errorsDiv.innerHTML = '<div class="error-message">' + errorMsg + '</div>';

        if (window.showNotification) {
            window.showNotification(errorMsg, 'error');
        } else {
            alert(errorMsg);
        }

        // Разблокируем кнопку
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalButtonHTML;
    }
}
