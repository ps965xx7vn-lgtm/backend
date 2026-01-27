/**
 * Course Detail Page JavaScript
 * Handles tabs switching and smooth scrolling
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tabs functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Hide all tab contents
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to current button
            this.classList.add('active');
            
            // Show target tab content
            const targetTab = tabId === 'curriculum' ? 
                document.getElementById('curriculum-content') : 
                tabId === 'reviews' ? 
                document.getElementById('reviews-content') : 
                document.getElementById('overview');
            
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });
    
    // Smooth scroll to curriculum section
    const curriculumLinks = document.querySelectorAll('a[href="#curriculum"]');
    curriculumLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Switch to curriculum tab
            const curriculumTabBtn = document.querySelector('.tab-btn[data-tab="curriculum"]');
            if (curriculumTabBtn) {
                curriculumTabBtn.click();
            }
            
            // Scroll to content section
            const contentSection = document.querySelector('#curriculum');
            if (contentSection) {
                contentSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
