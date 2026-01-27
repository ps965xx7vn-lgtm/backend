/**
 * Course list search and filter functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('course-search');
    const filterSelect = document.getElementById('course-filter');
    const coursesGrid = document.getElementById('courses-grid');
    const courseCards = document.querySelectorAll('.course-card');

    // Search functionality
    searchInput?.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const selectedFilter = filterSelect?.value || 'all';
        filterCourses(searchTerm, selectedFilter);
    });

    // Filter functionality
    filterSelect?.addEventListener('change', function() {
        const searchTerm = searchInput?.value.toLowerCase() || '';
        const selectedFilter = this.value;
        filterCourses(searchTerm, selectedFilter);
    });

    function filterCourses(searchTerm, filter) {
        courseCards.forEach(card => {
            const courseName = card.dataset.courseName;
            const courseStatus = card.dataset.courseStatus;

            const matchesSearch = !searchTerm || courseName.includes(searchTerm);
            const matchesFilter = filter === 'all' || courseStatus === filter;

            if (matchesSearch && matchesFilter) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease';
            } else {
                card.style.display = 'none';
            }
        });

        // Show/hide no results message
        const visibleCards = Array.from(courseCards).filter(card => card.style.display !== 'none');
        const noResultsMessage = getNoResultsMessage();
        
        if (visibleCards.length === 0 && coursesGrid) {
            if (!document.getElementById('no-results')) {
                const noResults = document.createElement('div');
                noResults.id = 'no-results';
                noResults.className = 'no-results';
                noResults.innerHTML = noResultsMessage;
                coursesGrid.appendChild(noResults);
            }
        } else {
            const noResults = document.getElementById('no-results');
            if (noResults) {
                noResults.remove();
            }
        }
    }
});

/**
 * Get no results message HTML
 * Can be set via data attribute on coursesGrid
 */
function getNoResultsMessage() {
    const coursesGrid = document.getElementById('courses-grid');
    const customMessage = coursesGrid?.dataset.noResultsMessage;
    
    if (customMessage) {
        return customMessage;
    }
    
    // Default message
    return `
        <svg class="no-results-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <h3 class="no-results-title">Курсы не найдены</h3>
        <p>Попробуйте изменить критерии поиска</p>
    `;
}
