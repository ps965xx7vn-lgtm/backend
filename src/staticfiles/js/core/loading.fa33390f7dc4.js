/**
 * Loading Overlay Manager
 * Управляет показом/скрытием экрана загрузки
 */

(function() {
    'use strict';

    // Функция для скрытия loading overlay
    function hideLoadingOverlay() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay && !loadingOverlay.classList.contains('hidden')) {
            loadingOverlay.classList.add('hiding');
            setTimeout(() => {
                loadingOverlay.classList.add('hidden');
                loadingOverlay.classList.remove('hiding');
            }, 300);
        }
    }

    // Скрываем по DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(hideLoadingOverlay, 500);
        });
    } else {
        // DOM уже загружен
        setTimeout(hideLoadingOverlay, 100);
    }

    // Fallback: скрываем по window.load (полная загрузка всех ресурсов)
    window.addEventListener('load', function() {
        setTimeout(hideLoadingOverlay, 100);
    });

    // Emergency fallback: скрываем через 3 секунды в любом случае
    setTimeout(hideLoadingOverlay, 3000);

    // Экспорт для использования из других модулей
    window.LoadingManager = {
        hide: hideLoadingOverlay,
        show: function() {
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden', 'hiding');
            }
        }
    };
})();
