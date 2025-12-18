/**
 * Tag Detail Filter Functionality
 * Article sorting and filtering
 */

function filterArticles(sortType) {
    // Получаем текущий URL
    const url = new URL(window.location.href);
    
    // Устанавливаем параметр sort
    url.searchParams.set('sort', sortType);
    
    // Сбрасываем страницу на первую
    url.searchParams.delete('page');
    
    // Переходим на новый URL
    window.location.href = url.toString();
}

// Добавляем визуальную обратную связь при клике
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Убираем active со всех кнопок
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            // Добавляем active на текущую
            this.classList.add('active');
        });
    });
});
