/**
 * Course detail page functionality
 * Handles lesson expand/collapse functionality
 */

/**
 * Toggle single lesson expansion
 * @param {string} lessonId - The ID of the lesson to toggle
 */
function toggleLesson(lessonId) {
    console.log('toggleLesson called with ID:', lessonId);
    const lessonItem = document.querySelector(`.lesson-item[data-lesson-id="${lessonId}"]`);
    if (lessonItem) {
        lessonItem.classList.toggle('expanded');
        console.log('Lesson toggled, expanded:', lessonItem.classList.contains('expanded'));
    } else {
        console.error('Lesson item not found for ID:', lessonId);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Course detail page loaded');
    
    const expandAllBtn = document.getElementById('expand-all');
    const collapseAllBtn = document.getElementById('collapse-all');
    
    // Expand all lessons
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', function() {
            console.log('Expanding all lessons');
            document.querySelectorAll('.lesson-item:not(.lesson-locked)').forEach(item => {
                item.classList.add('expanded');
            });
        });
    }
    
    // Collapse all lessons
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {
            console.log('Collapsing all lessons');
            document.querySelectorAll('.lesson-item').forEach(item => {
                item.classList.remove('expanded');
            });
        });
    }
    
    // Add click handlers to lesson headers (alternative to inline onclick)
    document.querySelectorAll('.lesson-header').forEach(header => {
        const lessonItem = header.closest('.lesson-item');
        if (lessonItem && !lessonItem.classList.contains('lesson-locked')) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function(e) {
                // Don't toggle if clicking on a button or link
                if (e.target.closest('a, button')) {
                    return;
                }
                const lessonId = lessonItem.getAttribute('data-lesson-id');
                if (lessonId) {
                    toggleLesson(lessonId);
                }
            });
        }
    });
    
    console.log('Found', document.querySelectorAll('.lesson-item').length, 'lesson items');
});
