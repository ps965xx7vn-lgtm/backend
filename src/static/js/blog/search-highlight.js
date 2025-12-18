/**
 * Search Results Highlighting
 * Highlights search query in article titles and descriptions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get query from data attribute or window variable
    const searchContainer = document.querySelector('[data-search-query]');
    const query = searchContainer ? searchContainer.dataset.searchQuery : '';
    
    if (query && query.trim() !== '') {
        const articles = document.querySelectorAll('.course-title-revolutionary, .course-description-revolutionary');
        articles.forEach(article => {
            const regex = new RegExp(`(${query})`, 'gi');
            article.innerHTML = article.innerHTML.replace(regex, '<mark class="search-highlight">$1</mark>');
        });
    }
});
