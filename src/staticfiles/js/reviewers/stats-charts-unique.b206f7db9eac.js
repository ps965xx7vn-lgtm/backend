// Statistics Charts - Ultra Modern Unique Design
// Уникальный ультрасовременный дизайн графиков
// Новые уникальные классы: stats-*

document.addEventListener('DOMContentLoaded', function() {
    console.log('Stats Charts Unique - Initializing...');
    
    // Инициализация графика активности
    initDailyActivityChart();
    
    // Инициализация интерактивности столбцов
    initMonthlyBarsInteraction();
    
    // Инициализация взаимодействия с легендой
    initLegendInteraction();
    
    // Анимация прогресс баров
    animateProgressBars();
    
    // Анимация недельных баров
    animateWeeklyBars();
    
    console.log('Stats Charts Unique - Initialized!');
});

// ========================================
// CANVAS LINE CHART для активности за 30 дней
// ========================================
function initDailyActivityChart() {
    const chartContainer = document.getElementById('dailyActivityChart');
    if (!chartContainer) {
        console.log('Daily activity chart container not found');
        return;
    }
    
    const canvas = document.getElementById('dailyCanvas');
    if (!canvas) {
        console.log('Daily canvas not found');
        return;
    }
    
    // Получаем данные из атрибутов data (должны быть добавлены в шаблон)
    const dataElement = chartContainer.querySelector('[data-chart-data]');
    if (!dataElement) {
        console.log('Chart data not found');
        return;
    }
    
    try {
        const chartData = JSON.parse(dataElement.dataset.chartData);
        console.log('Chart data loaded:', chartData);
        
        // Создаем и рендерим график
        const chart = new ChartRenderer(canvas, chartData);
        chart.draw();
        
        // Сохраняем ссылку для возможного обновления
        window.dailyChart = chart;
    } catch (error) {
        console.error('Error initializing daily activity chart:', error);
    }
}

// ========================================
// CHART RENDERER CLASS
// ========================================
class ChartRenderer {
    constructor(canvas, data) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.data = data;
        
        // Настройки
        this.padding = { top: 40, right: 30, bottom: 50, left: 50 };
        this.colors = {
            approved: '#10b981',
            needsWork: '#3b82f6',
            rejected: '#ef4444',
            grid: 'rgba(107, 114, 128, 0.15)',
            text: getComputedStyle(document.documentElement).getPropertyValue('--text-color') || '#1f2937'
        };
        
        // Размеры
        this.setSize();
        
        // Hover состояние
        this.hoveredPoint = null;
        
        // Привязываем обработчики событий
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }
    
    setSize() {
        const rect = this.canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        
        this.ctx.scale(dpr, dpr);
        
        this.width = rect.width;
        this.height = rect.height;
        
        this.chartWidth = this.width - this.padding.left - this.padding.right;
        this.chartHeight = this.height - this.padding.top - this.padding.bottom;
    }
    
    draw() {
        // Очистка
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // Рисуем элементы
        this.drawGrid();
        this.drawAxes();
        this.drawLines();
        this.drawPoints();
        
        // Hover tooltip
        if (this.hoveredPoint) {
            this.drawTooltip(this.hoveredPoint);
        }
    }
    
    drawGrid() {
        const { ctx, padding, chartWidth, chartHeight } = this;
        
        ctx.strokeStyle = this.colors.grid;
        ctx.lineWidth = 1;
        
        // Горизонтальные линии (5 линий)
        for (let i = 0; i <= 5; i++) {
            const y = padding.top + (chartHeight / 5) * i;
            
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(padding.left + chartWidth, y);
            ctx.stroke();
        }
        
        // Вертикальные линии (каждый 5-й день)
        const points = this.data.dates.length;
        const step = Math.ceil(points / 6);
        
        for (let i = 0; i <= points; i += step) {
            const x = padding.left + (chartWidth / (points - 1)) * i;
            
            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, padding.top + chartHeight);
            ctx.stroke();
        }
    }
    
    drawAxes() {
        const { ctx, padding, chartWidth, chartHeight, data } = this;
        
        // Максимальное значение
        const maxValue = Math.max(
            ...data.approved,
            ...data.needsWork,
            ...data.rejected
        );
        const yMax = Math.ceil(maxValue / 10) * 10 + 10;
        
        ctx.fillStyle = this.colors.text;
        ctx.font = 'bold 11px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'right';
        
        // Y-axis labels
        for (let i = 0; i <= 5; i++) {
            const value = Math.round((yMax / 5) * (5 - i));
            const y = padding.top + (chartHeight / 5) * i;
            
            ctx.fillText(value.toString(), padding.left - 10, y + 4);
        }
        
        // X-axis labels (даты)
        ctx.textAlign = 'center';
        const points = data.dates.length;
        const step = Math.ceil(points / 6);
        
        for (let i = 0; i < points; i += step) {
            const x = padding.left + (chartWidth / (points - 1)) * i;
            const date = data.dates[i];
            
            ctx.fillText(date, x, padding.top + chartHeight + 25);
        }
        
        // Сохраняем yMax для использования в других методах
        this.yMax = yMax;
    }
    
    drawLines() {
        this.drawLine(this.data.approved, this.colors.approved);
        this.drawLine(this.data.needsWork, this.colors.needsWork);
        this.drawLine(this.data.rejected, this.colors.rejected);
    }
    
    drawLine(values, color) {
        const { ctx, padding, chartWidth, chartHeight, yMax } = this;
        const points = values.length;
        
        if (points === 0) return;
        
        // Линия с градиентом
        const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, color + '80');
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Путь линии
        ctx.beginPath();
        
        for (let i = 0; i < points; i++) {
            const x = padding.left + (chartWidth / (points - 1)) * i;
            const y = padding.top + chartHeight - (values[i] / yMax) * chartHeight;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        
        ctx.stroke();
        
        // Заполнение под линией
        ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
        ctx.lineTo(padding.left, padding.top + chartHeight);
        ctx.closePath();
        
        const fillGradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
        fillGradient.addColorStop(0, color + '40');
        fillGradient.addColorStop(1, color + '05');
        
        ctx.fillStyle = fillGradient;
        ctx.fill();
    }
    
    drawPoints() {
        this.drawPointsForLine(this.data.approved, this.colors.approved);
        this.drawPointsForLine(this.data.needsWork, this.colors.needsWork);
        this.drawPointsForLine(this.data.rejected, this.colors.rejected);
    }
    
    drawPointsForLine(values, color) {
        const { ctx, padding, chartWidth, chartHeight, yMax } = this;
        const points = values.length;
        
        for (let i = 0; i < points; i++) {
            const x = padding.left + (chartWidth / (points - 1)) * i;
            const y = padding.top + chartHeight - (values[i] / yMax) * chartHeight;
            
            // Внешний круг
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
            
            // Внутренний круг (белый)
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x, y, 2.5, 0, Math.PI * 2);
            ctx.fill();
            
            // Если это точка под курсором
            if (this.hoveredPoint && this.hoveredPoint.index === i) {
                ctx.strokeStyle = color;
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(x, y, 8, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
    }
    
    drawTooltip(point) {
        const { ctx, padding, chartWidth, chartHeight, yMax, data } = this;
        const points = data.dates.length;
        
        const x = padding.left + (chartWidth / (points - 1)) * point.index;
        const approved = data.approved[point.index];
        const needsWork = data.needsWork[point.index];
        const rejected = data.rejected[point.index];
        const date = data.dates[point.index];
        
        // Размеры tooltip
        const tooltipWidth = 180;
        const tooltipHeight = 110;
        let tooltipX = x + 15;
        let tooltipY = padding.top + 10;
        
        // Проверка выхода за правую границу
        if (tooltipX + tooltipWidth > this.width - padding.right) {
            tooltipX = x - tooltipWidth - 15;
        }
        
        // Фон tooltip
        ctx.fillStyle = 'rgba(255, 255, 255, 0.98)';
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.3)';
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        ctx.roundRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight, 12);
        ctx.fill();
        ctx.stroke();
        
        // Текст
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 13px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(date, tooltipX + 15, tooltipY + 25);
        
        // Значения
        ctx.font = '12px system-ui, -apple-system, sans-serif';
        
        // Approved
        ctx.fillStyle = this.colors.approved;
        ctx.fillText('● Одобрено:', tooltipX + 15, tooltipY + 48);
        ctx.fillStyle = '#1f2937';
        ctx.textAlign = 'right';
        ctx.fillText(approved.toString(), tooltipX + tooltipWidth - 15, tooltipY + 48);
        
        // Needs Work
        ctx.textAlign = 'left';
        ctx.fillStyle = this.colors.needsWork;
        ctx.fillText('● Доработка:', tooltipX + 15, tooltipY + 70);
        ctx.fillStyle = '#1f2937';
        ctx.textAlign = 'right';
        ctx.fillText(needsWork.toString(), tooltipX + tooltipWidth - 15, tooltipY + 70);
        
        // Rejected
        ctx.textAlign = 'left';
        ctx.fillStyle = this.colors.rejected;
        ctx.fillText('● Отклонено:', tooltipX + 15, tooltipY + 92);
        ctx.fillStyle = '#1f2937';
        ctx.textAlign = 'right';
        ctx.fillText(rejected.toString(), tooltipX + tooltipWidth - 15, tooltipY + 92);
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const { padding, chartWidth, chartHeight, data } = this;
        const points = data.dates.length;
        
        // Проверяем, находится ли курсор в области графика
        if (mouseX < padding.left || mouseX > padding.left + chartWidth ||
            mouseY < padding.top || mouseY > padding.top + chartHeight) {
            if (this.hoveredPoint) {
                this.hoveredPoint = null;
                this.draw();
                this.canvas.style.cursor = 'default';
            }
            return;
        }
        
        // Находим ближайшую точку
        const relativeX = mouseX - padding.left;
        const index = Math.round((relativeX / chartWidth) * (points - 1));
        
        if (index >= 0 && index < points) {
            this.hoveredPoint = { index };
            this.draw();
            this.canvas.style.cursor = 'pointer';
        }
    }
    
    handleMouseLeave() {
        if (this.hoveredPoint) {
            this.hoveredPoint = null;
            this.draw();
            this.canvas.style.cursor = 'default';
        }
    }
}

// ========================================
// MONTHLY BARS INTERACTION
// ========================================
function initMonthlyBarsInteraction() {
    const monthBars = document.querySelectorAll('.stats-month-bar');
    
    monthBars.forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            // Масштабирование и подсветка
            this.style.transform = 'translateY(-12px) scale(1.1) rotateX(5deg)';
            
            // Показываем значение
            const valueSpan = this.querySelector('.stats-bar-value');
            if (valueSpan) {
                valueSpan.style.opacity = '1';
                valueSpan.style.transform = 'translateX(-50%) translateY(-8px)';
            }
        });
        
        bar.addEventListener('mouseleave', function() {
            this.style.transform = '';
            
            const valueSpan = this.querySelector('.stats-bar-value');
            if (valueSpan) {
                valueSpan.style.opacity = '0';
                valueSpan.style.transform = 'translateX(-50%)';
            }
        });
    });
}

// ========================================
// LEGEND INTERACTION
// ========================================
function initLegendInteraction() {
    const legendItems = document.querySelectorAll('.stats-legend-item');
    
    legendItems.forEach(item => {
        item.addEventListener('click', function() {
            // Получаем класс статуса (approved, needs-work, rejected)
            const colorSpan = this.querySelector('.stats-legend-color');
            if (!colorSpan) return;
            
            const statusClass = Array.from(colorSpan.classList).find(cls => 
                cls === 'approved' || cls === 'needs-work' || cls === 'rejected'
            );
            
            if (!statusClass) return;
            
            // Переключаем видимость соответствующих элементов
            const elements = document.querySelectorAll(`.stats-month-bar.${statusClass}`);
            
            elements.forEach(el => {
                if (el.style.opacity === '0.2') {
                    el.style.opacity = '1';
                    el.style.pointerEvents = 'auto';
                } else {
                    el.style.opacity = '0.2';
                    el.style.pointerEvents = 'none';
                }
            });
            
            // Визуальная обратная связь на легенде
            if (this.style.opacity === '0.5') {
                this.style.opacity = '1';
            } else {
                this.style.opacity = '0.5';
            }
        });
    });
}

// ========================================
// ANIMATE PROGRESS BARS (Course Stats)
// ========================================
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.stats-course-fill');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.style.width;
                entry.target.style.width = '0%';
                
                setTimeout(() => {
                    entry.target.style.transition = 'width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    entry.target.style.width = targetWidth;
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// ========================================
// ANIMATE WEEKLY BARS
// ========================================
function animateWeeklyBars() {
    const weeklyBars = document.querySelectorAll('.stats-week-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.style.width;
                entry.target.style.width = '0%';
                
                setTimeout(() => {
                    entry.target.style.transition = 'width 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    entry.target.style.width = targetWidth;
                }, 100 + index * 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    weeklyBars.forEach(bar => observer.observe(bar));
}

// ========================================
// HELPER: Animated Value Counter
// ========================================
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        element.textContent = Math.round(current);
    }, 16);
}

// ========================================
// ТЕМНАЯ ТЕМА - Обновление цветов графика
// ========================================
function updateChartTheme() {
    if (window.dailyChart) {
        window.dailyChart.colors.text = getComputedStyle(document.documentElement)
            .getPropertyValue('--text-color') || '#1f2937';
        window.dailyChart.draw();
    }
}

// Слушаем изменения темы
const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
            updateChartTheme();
        }
    });
});

themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
});

// Полифилл для roundRect (для старых браузеров)
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r) {
        if (w < 2 * r) r = w / 2;
        if (h < 2 * r) r = h / 2;
        
        this.beginPath();
        this.moveTo(x + r, y);
        this.arcTo(x + w, y, x + w, y + h, r);
        this.arcTo(x + w, y + h, x, y + h, r);
        this.arcTo(x, y + h, x, y, r);
        this.arcTo(x, y, x + w, y, r);
        this.closePath();
        
        return this;
    };
}
