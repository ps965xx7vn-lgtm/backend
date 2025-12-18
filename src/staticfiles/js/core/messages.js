// Django Messages Auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        setTimeout(() => {
            messagesContainer.classList.add('hide');
            setTimeout(() => messagesContainer.remove(), 300);
        }, 5000);
    }
});
