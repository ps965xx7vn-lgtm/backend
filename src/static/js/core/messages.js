// Django Messages Auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        // Add click to dismiss
        messagesContainer.querySelectorAll('.alert').forEach(alert => {
            alert.style.cursor = 'pointer';
            alert.addEventListener('click', () => {
                messagesContainer.classList.add('hide');
                setTimeout(() => messagesContainer.remove(), 300);
            });
        });

        // Auto-hide after 3 seconds
        setTimeout(() => {
            messagesContainer.classList.add('hide');
            setTimeout(() => messagesContainer.remove(), 300);
        }, 3000); // 3 seconds
    }
});
