// Blog Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    
    // Animated Counter for Stats
    function animateCounters() {
        const counters = document.querySelectorAll('[data-counter]');
        const observerOptions = {
            threshold: 0.7,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.dataset.counter);
                    let current = 0;
                    const increment = target / 60; // 60 frames for smooth animation
                    
                    const updateCounter = () => {
                        if (current < target) {
                            current += increment;
                            counter.textContent = Math.floor(current);
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.textContent = target;
                        }
                    };
                    
                    updateCounter();
                    observer.unobserve(counter);
                }
            });
        }, observerOptions);

        counters.forEach(counter => observer.observe(counter));
    }

    // Newsletter Subscription Handler
    function setupNewsletterForm() {
        const form = document.getElementById('newsletter-form');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const btn = this.querySelector('.newsletter-btn');
            const input = this.querySelector('.newsletter-input');
            const originalText = btn.textContent;
            
            // Loading state
            btn.textContent = 'Подписываем...';
            btn.disabled = true;
            btn.style.background = '#94a3b8';
            
            fetch('/ru/blog/newsletter/subscribe/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btn.textContent = '✓ Подписан!';
                    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                    input.value = '';
                    
                    // Show success animation
                    btn.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        btn.style.transform = 'scale(1)';
                    }, 200);
                    
                    // Reset after 3 seconds
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.style.background = '';
                        btn.disabled = false;
                    }, 3000);
                } else {
                    btn.textContent = 'Ошибка!';
                    btn.style.background = '#ef4444';
                    
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.style.background = '';
                        btn.disabled = false;
                    }, 2000);

                }
            })
            .catch(error => {

                btn.textContent = 'Ошибка сети!';
                btn.style.background = '#ef4444';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '';
                    btn.disabled = false;
                }, 2000);
            });
        });
    }

    // Particle Animation System
    function createParticles() {
        const heroSection = document.querySelector('.blog-hero');
        if (!heroSection) return;

        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles-container';
        heroSection.appendChild(particlesContainer);

        function createParticle() {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position and properties
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = (Math.random() * 3 + 5) + 's';
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            // Random size
            const size = Math.random() * 4 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            
            particlesContainer.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 8000);
        }

        // Create particles continuously
        setInterval(createParticle, 300);
    }

    // Smooth Card Animations on Scroll
    function setupScrollAnimations() {
        const cards = document.querySelectorAll('.featured-card, .latest-card, .category-card');
        
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, observerOptions);

        cards.forEach(card => {
            observer.observe(card);
        });
    }

    // Enhanced Hover Effects
    function setupHoverEffects() {
        // Featured cards glow effect
        const featuredCards = document.querySelectorAll('.featured-card');
        featuredCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 25px 60px rgba(102, 126, 234, 0.2)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
            });
        });

        // Category cards bounce effect
        const categoryCards = document.querySelectorAll('.category-card');
        categoryCards.forEach(card => {
            card.addEventListener('click', function() {
                this.style.animation = 'pulse 0.6s ease-in-out';
                setTimeout(() => {
                    this.style.animation = '';
                }, 600);
            });
        });
    }

    // Parallax Effect for Hero Section
    function setupParallax() {
        const hero = document.querySelector('.blog-hero');
        if (!hero) return;

        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const heroHeight = hero.offsetHeight;
            
            if (scrolled < heroHeight) {
                const translateY = scrolled * 0.5;
                hero.style.transform = `translateY(${translateY}px)`;
            }
        });
    }

    // Search Functionality Enhancement
    function setupSearchEnhancements() {
        const searchInputs = document.querySelectorAll('.search-input');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const searchTerm = this.value.toLowerCase().trim();
                
                // Add loading indicator
                this.style.background = 'linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%)';
                this.style.backgroundSize = '200% 100%';
                this.style.animation = 'loading 1.5s infinite';
                
                searchTimeout = setTimeout(() => {
                    // Remove loading indicator
                    this.style.background = '';
                    this.style.animation = '';
                    
                    // Perform search logic here
                    if (searchTerm.length > 0) {

                        // Add your search logic here
                    }
                }, 500);
            });
        });
    }

    // Dynamic Theme Color Based on Scroll
    function setupDynamicTheme() {
        const sections = document.querySelectorAll('section');
        const colors = [
            '#667eea', // Hero
            '#10b981', // Featured
            '#f59e0b', // Latest
            '#8b5cf6', // Categories
            '#ef4444'  // Newsletter
        ];

        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset;
            
            sections.forEach((section, index) => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                
                if (scrollTop >= sectionTop - 100 && scrollTop < sectionTop + sectionHeight - 100) {
                    document.documentElement.style.setProperty('--dynamic-color', colors[index]);
                }
            });
        });
    }

    // Loading Animation for Images
    function setupImageLoading() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            img.addEventListener('load', function() {
                this.style.animation = 'fadeIn 0.5s ease-in-out';
            });
        });
    }

    // Initialize all features
    function init() {
        animateCounters();
        setupNewsletterForm();
        createParticles();
        setupScrollAnimations();
        setupHoverEffects();
        setupParallax();
        setupSearchEnhancements();
        setupDynamicTheme();
        setupImageLoading();
        
        // Add smooth scrolling to all anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Run initialization
    init();
});

// Add CSS animations dynamically
const additionalStyles = `
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.search-input:focus {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    border-color: #667eea;
}

:root {
    --dynamic-color: #667eea;
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);