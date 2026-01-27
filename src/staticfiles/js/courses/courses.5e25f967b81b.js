// JavaScript для курсов
document.addEventListener('DOMContentLoaded', function() {
    
    // Анимации при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами для анимации
    document.querySelectorAll('.course-card-revolutionary, .feature-card-revolutionary, .stat-card-revolutionary').forEach(el => {
        observer.observe(el);
    });

    // Фильтры курсов
    const filterBtns = document.querySelectorAll('.filter-btn');
    const courseCards = document.querySelectorAll('.course-card-revolutionary');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Убираем активный класс у всех кнопок
            filterBtns.forEach(b => b.classList.remove('active'));
            
            // Добавляем активный класс к текущей кнопке
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Фильтруем курсы
            courseCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.5s ease forwards';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Плавная прокрутка к якорям
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

    // Параллакс эффект для particles
    const particles = document.querySelectorAll('.particle');
    if (particles.length > 0) {
        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            particles.forEach((particle, index) => {
                const speed = 0.2 + (index * 0.1);
                particle.style.transform = `translateY(${scrollY * speed}px)`;
            });
        });
    }

    // Анимация набора текста для кода
    const codeLines = document.querySelectorAll('.code-line');
    if (codeLines.length > 0) {
        const codeObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const codeContainer = entry.target.closest('.code-animation');
                    if (codeContainer) {
                        animateTyping(codeContainer);
                    }
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('.code-animation').forEach(codeBlock => {
            codeObserver.observe(codeBlock);
        });
    }

    function animateTyping(container) {
        const lines = container.querySelectorAll('.code-line');
        lines.forEach((line, index) => {
            setTimeout(() => {
                line.style.opacity = '1';
                line.style.animation = 'slideInLeft 0.5s ease forwards';
            }, index * 200);
        });
    }

    // Добавляем анимации для слайда
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInLeft {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .code-line {
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .course-card-revolutionary {
            transition: all 0.3s ease;
        }
        
        .course-card-revolutionary:hover {
            transform: translateY(-8px) scale(1.02);
        }
        
        .feature-card-revolutionary {
            transition: all 0.3s ease;
        }
        
        .feature-card-revolutionary:hover {
            transform: translateY(-8px) scale(1.02);
        }
    `;
    document.head.appendChild(style);

    // Динамическая загрузка курсов (если нужно)
    const loadMoreBtn = document.querySelector('.load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Здесь можно добавить AJAX загрузку дополнительных курсов

        });
    }

    // Поиск курсов
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            courseCards.forEach(card => {
                const title = card.querySelector('.course-title-revolutionary').textContent.toLowerCase();
                const description = card.querySelector('.course-description-revolutionary').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Инициализация счетчиков статистики
    const statNumbers = document.querySelectorAll('.stat-number-revolutionary');
    statNumbers.forEach(stat => {
        const text = stat.textContent;
        const number = parseInt(text.replace(/\D/g, ''));
        if (number && !isNaN(number)) {
            animateCounter(stat, 0, number, 2000);
        }
    });

    function animateCounter(element, start, end, duration) {
        const startTime = performance.now();
        const originalText = element.textContent;
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = originalText.replace(end.toString(), current.toString());
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
});