/**
 * Tag List Search Functionality
 * Real-time tag filtering and search
 */

document.addEventListener('DOMContentLoaded', function() {
    const tagSearch = document.getElementById('tagSearch');
    const searchResults = document.getElementById('searchResults');
    const resultCount = document.getElementById('resultCount');
    const scrollDownBtn = document.getElementById('scrollDownBtn');
    const categoriesSection = document.getElementById('categoriesSection');

    // Функция поиска
    function performSearch() {
        const searchTerm = tagSearch.value.toLowerCase().trim();
        
        // Поиск в категориях
        const categoryCards = document.querySelectorAll('.tag-category-card');
        let visibleCategoryTagsCount = 0;
        
        if (searchTerm === '') {
            // Показать все категории
            categoryCards.forEach(card => {
                card.style.display = 'block';
                const tags = card.querySelectorAll('.tag-revolutionary-small');
                tags.forEach(tag => tag.style.display = 'inline-block');
            });
            // Скрыть результаты
            if (searchResults) searchResults.style.display = 'none';
        } else {
            // Фильтровать категории и теги
            categoryCards.forEach(card => {
                const categoryTitle = card.querySelector('.course-title-revolutionary')?.textContent.toLowerCase() || '';
                const categoryDesc = card.querySelector('.course-description-revolutionary')?.textContent.toLowerCase() || '';
                const tags = card.querySelectorAll('.tag-revolutionary-small');
                
                // Проверяем совпадение категории
                const isCategoryMatch = categoryTitle.includes(searchTerm) || categoryDesc.includes(searchTerm);
                
                let hasVisibleTags = false;
                
                // Фильтруем теги
                tags.forEach(tag => {
                    const tagText = tag.textContent.toLowerCase();
                    
                    // Тег видим если: совпадает сам тег ИЛИ совпадает категория
                    const shouldShowTag = tagText.includes(searchTerm) || isCategoryMatch;
                    tag.style.display = shouldShowTag ? 'inline-block' : 'none';
                    
                    // Считаем ТОЛЬКО если тег совпадает по тексту (не по категории!)
                    if (tagText.includes(searchTerm)) {
                        hasVisibleTags = true;
                        visibleCategoryTagsCount++;
                    }
                });
                
                // Показать категорию если есть совпадения в названии, описании или хотя бы один тег совпадает
                const shouldShowCard = isCategoryMatch || hasVisibleTags;
                card.style.display = shouldShowCard ? 'block' : 'none';
            });
            
            // Показать результаты - ТОЛЬКО совпавшие теги
            if (searchResults && resultCount) {
                resultCount.textContent = visibleCategoryTagsCount;
                searchResults.style.display = visibleCategoryTagsCount > 0 ? 'block' : 'none';
            }
        }
    }

    // Слушатели событий
    if (tagSearch) {
        // Поиск при вводе
        tagSearch.addEventListener('input', performSearch);
        
        // Очистка поиска по Escape
        tagSearch.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                performSearch();
            }
        });
        
        // Инициализация если есть значение
        if (tagSearch.value.trim() !== '') {
            performSearch();
        }
    }

    // Кнопка скролла вниз к категориям
    if (scrollDownBtn && categoriesSection) {
        scrollDownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            categoriesSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        });
    }

    // Анимация тегов при наведении
    document.querySelectorAll('.tag-revolutionary').forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(2deg)';
        });
        
        tag.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });

    // Клик по категории - фокус на теги этой категории
    document.querySelectorAll('.tag-category-card').forEach(card => {
        const title = card.querySelector('.course-title-revolutionary');
        if (title) {
            title.style.cursor = 'pointer';
            title.addEventListener('click', function(e) {
                e.preventDefault();
                const category = card.dataset.category;
                if (tagSearch) {
                    tagSearch.value = category;
                    tagSearch.dispatchEvent(new Event('input'));
                    tagSearch.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    tagSearch.focus();
                }
            });
        }
    });
});
