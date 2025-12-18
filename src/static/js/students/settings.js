/**
 * Account Settings Page JavaScript
 * Управление настройками профиля, аватаром и удалением аккаунта
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // Remove active classes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active classes
            this.classList.add('active');
            document.querySelector(`[data-tab-content="${targetTab}"]`).classList.add('active');
        });
    });

    // Avatar preview
    const avatarInput = document.getElementById('avatar-input');
    const avatarPreview = document.getElementById('avatar-preview');

    avatarInput?.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (avatarPreview.tagName === 'IMG') {
                    avatarPreview.src = e.target.result;
                } else {
                    avatarPreview.outerHTML = `<img src="${e.target.result}" alt="Avatar Preview" id="avatar-preview">`;
                }
            };
            reader.readAsDataURL(file);
        }
    });

    // Remove avatar
    initAvatarDeletion();

    // Delete account confirmation
    initDeleteAccountConfirmation();
});

/**
 * Инициализация удаления аватара
 */
function initAvatarDeletion() {
    const removeAvatarBtn = document.getElementById('remove-avatar');
    const avatarInput = document.getElementById('avatar-input');
    
    if (!removeAvatarBtn) return;

    removeAvatarBtn.addEventListener('click', function() {
        const deleteAvatarUrl = removeAvatarBtn.dataset.deleteUrl;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        if (confirm(removeAvatarBtn.dataset.confirmMessage || 'Вы уверены, что хотите удалить фото профиля?')) {
            // Send AJAX request to delete avatar
            fetch(deleteAvatarUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset to placeholder
                    const email = removeAvatarBtn.dataset.userEmail;
                    const initial = email ? email.charAt(0).toUpperCase() : 'U';
                    const avatarPreview = document.getElementById('avatar-preview');
                    if (avatarPreview) {
                        avatarPreview.outerHTML = `<div class="avatar-placeholder" id="avatar-preview">${initial}</div>`;
                    }
                    if (avatarInput) {
                        avatarInput.value = '';
                    }
                    
                    // Hide delete button
                    removeAvatarBtn.style.display = 'none';
                    
                    // Show success notification
                    if (typeof showNotification === 'function') {
                        showNotification(data.message || 'Аватар успешно удален', 'success');
                    }
                    
                    // Reload page to update UI
                    setTimeout(() => location.reload(), 1500);
                } else {
                    if (typeof showNotification === 'function') {
                        showNotification(data.message || 'Ошибка при удалении аватара', 'error');
                    }
                }
            })
            .catch(error => {

                if (typeof showNotification === 'function') {
                    showNotification('Произошла ошибка при удалении аватара', 'error');
                }
            });
        }
    });
}

/**
 * Инициализация подтверждения удаления аккаунта
 */
function initDeleteAccountConfirmation() {
    const deleteConfirmationInput = document.getElementById('delete-confirmation');
    const deletePasswordInput = document.getElementById('delete-password');
    const confirmDeleteBtn = document.getElementById('confirm-delete');

    function checkDeleteConfirmation() {
        if (deleteConfirmationInput && deletePasswordInput && confirmDeleteBtn) {
            const confirmationValid = deleteConfirmationInput.value === 'УДАЛИТЬ';
            const passwordValid = deletePasswordInput.value.length > 0;
            confirmDeleteBtn.disabled = !(confirmationValid && passwordValid);
        }
    }

    deleteConfirmationInput?.addEventListener('input', checkDeleteConfirmation);
    deletePasswordInput?.addEventListener('input', checkDeleteConfirmation);
}

/**
 * Открыть модальное окно удаления аккаунта
 */
window.openDeleteModal = function() {
    const modal = document.getElementById('delete-account-modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

/**
 * Закрыть модальное окно удаления аккаунта
 */
window.closeDeleteModal = function() {
    const modal = document.getElementById('delete-account-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        // Reset form
        const form = document.getElementById('delete-account-form');
        if (form) {
            form.reset();
            const confirmDeleteBtn = document.getElementById('confirm-delete');
            if (confirmDeleteBtn) {
                confirmDeleteBtn.disabled = true;
            }
        }
    }
};
