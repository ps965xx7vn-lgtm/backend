/**
 * Modern Code Preloader Manager
 * Управляет показом/скрытием современного экрана загрузки
 */

(function() {
    'use strict';

    let isHiding = false;

    // Функция для скрытия preloader с плавной анимацией
    function hideLoadingOverlay() {
        if (isHiding) return;

        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay && !loadingOverlay.classList.contains('hidden')) {
            isHiding = true;

            // Добавляем класс hiding для плавного исчезновения
            loadingOverlay.classList.add('hiding');

            // Удаляем элемент через 500мс после начала анимации
            setTimeout(() => {
                loadingOverlay.classList.add('hidden');
                loadingOverlay.classList.remove('hiding');
                isHiding = false;
            }, 500);
        }
    }

    // Минимальное время показа прелоадера для плавности (800мс)
    const minDisplayTime = 800;
    const startTime = Date.now();

    function hideWithMinTime() {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, minDisplayTime - elapsed);

        setTimeout(hideLoadingOverlay, remaining);
    }

    // Скрываем по DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideWithMinTime);
    } else {
        // DOM уже загружен
        hideWithMinTime();
    }

    // Fallback: скрываем по window.load (полная загрузка всех ресурсов)
    window.addEventListener('load', function() {
        setTimeout(hideLoadingOverlay, 200);
    });

    // Emergency fallback: скрываем через 4 секунды в любом случае
    setTimeout(() => {
        if (!isHiding) {
            hideLoadingOverlay();
        }
    }, 4000);

    // Экспорт для использования из других модулей
    window.LoadingManager = {
        hide: hideLoadingOverlay,
        show: function() {
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                isHiding = false;
                loadingOverlay.classList.remove('hidden', 'hiding');
            }
        }
    };
})();
