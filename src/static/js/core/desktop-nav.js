/**
 * Desktop Navigation Enhancement
 * Handles dropdown interactions and sticky header
 */

(function() {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDesktopNav);
    } else {
        initDesktopNav();
    }

    function initDesktopNav() {
        // Only run on desktop (≥ 1280px)
        if (window.innerWidth < 1280) return;

        const header = document.querySelector('.header-main[data-sticky]');
        const dropdowns = document.querySelectorAll('.nav-dropdown, .user-account-dropdown');

        // Sticky Header on Scroll
        if (header) {
            let lastScroll = 0;
            window.addEventListener('scroll', () => {
                const currentScroll = window.pageYOffset;
                
                if (currentScroll > 100) {
                    header.classList.add('is-sticky');
                } else {
                    header.classList.remove('is-sticky');
                }
                
                lastScroll = currentScroll;
            });
        }

        // Dropdown Hover Enhancement
        dropdowns.forEach(dropdown => {
            let timeout;

            dropdown.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
                dropdown.classList.add('active');
            });

            dropdown.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => {
                    dropdown.classList.remove('active');
                }, 150);
            });

            // Keyboard accessibility
            const trigger = dropdown.querySelector('[data-dropdown-trigger]');
            if (trigger) {
                trigger.addEventListener('click', (e) => {
                    if (window.innerWidth >= 1280) {
                        // Prevent default for user dropdown, allow for nav links
                        if (dropdown.classList.contains('user-account-dropdown')) {
                            e.preventDefault();
                            dropdown.classList.toggle('active');
                        }
                        // Nav dropdowns can follow the link
                    }
                });

                trigger.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        dropdown.classList.toggle('active');
                    }
                    if (e.key === 'Escape') {
                        dropdown.classList.remove('active');
                    }
                });
            }
        });

        // Close dropdowns on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-dropdown') && !e.target.closest('.user-account-dropdown')) {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });

        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth < 1280) {
                    // Close all dropdowns when switching to mobile
                    dropdowns.forEach(dropdown => {
                        dropdown.classList.remove('active');
                    });
                }
            }, 250);
        });
    }
})();
