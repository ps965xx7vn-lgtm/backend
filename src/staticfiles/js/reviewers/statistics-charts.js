/* ==================================
   Statistics Charts - Interactive Features
   Интерактивные функции для графиков
   ================================== */

(function() {
    'use strict';

    // Конфигурация
    const CONFIG = {
        animationDuration: 1500,
        chartPadding: 40,
        chartHeight: 300,
        gridLines: 5,
        colors: {
            approved: '#10b981',
            needsWork: '#3b82f6',
            rejected: '#ef4444',
            grid: '#e5e7eb',
            gridDark: '#374151',
            text: '#6b7280',
            textDark: '#9ca3af'
        }
    };

    // Утилиты
    const Utils = {
        isDarkTheme() {
            return document.documentElement.getAttribute('data-theme') === 'dark';
        },

        getColor(key) {
            return this.isDarkTheme() && CONFIG.colors[key + 'Dark'] 
                ? CONFIG.colors[key + 'Dark'] 
                : CONFIG.colors[key];
        },

        animateValue(element, start, end, duration, suffix = '') {
            if (!element) return;
            
            const startTime = performance.now();
            const isFloat = end % 1 !== 0;
            
            function update(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);
                const current = start + (end - start) * easeOut;
                
                element.textContent = (isFloat ? current.toFixed(1) : Math.floor(current)) + suffix;
                
                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            }
            
            requestAnimationFrame(update);
        },

        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // Класс для работы с canvas графиками
    class ChartRenderer {
        constructor(canvasId, data, options = {}) {
            this.canvas = document.getElementById(canvasId);
            if (!this.canvas) return;
            
            this.ctx = this.canvas.getContext('2d');
            this.data = data;
            this.options = {
                padding: CONFIG.chartPadding,
                height: CONFIG.chartHeight,
                gridLines: CONFIG.gridLines,
                ...options
            };
            
            this.resize();
            this.draw();
            this.setupInteraction();
        }

        resize() {
            const container = this.canvas.parentElement;
            const rect = container.getBoundingClientRect();
            
            this.canvas.width = rect.width;
            this.canvas.height = this.options.height;
            
            this.width = this.canvas.width;
            this.height = this.canvas.height;
            this.chartWidth = this.width - this.options.padding * 2;
            this.chartHeight = this.height - this.options.padding * 2;
        }

        draw() {
            this.clear();
            this.drawGrid();
            this.drawAxes();
            this.drawData();
        }

        clear() {
            this.ctx.clearRect(0, 0, this.width, this.height);
        }

        drawGrid() {
            const isDark = Utils.isDarkTheme();
            this.ctx.strokeStyle = isDark ? CONFIG.colors.gridDark : CONFIG.colors.grid;
            this.ctx.lineWidth = 1;

            // Горизонтальные линии
            for (let i = 0; i <= this.options.gridLines; i++) {
                const y = this.options.padding + (this.chartHeight / this.options.gridLines) * i;
                
                this.ctx.beginPath();
                this.ctx.moveTo(this.options.padding, y);
                this.ctx.lineTo(this.width - this.options.padding, y);
                this.ctx.stroke();
            }
        }

        drawAxes() {
            const isDark = Utils.isDarkTheme();
            this.ctx.strokeStyle = isDark ? '#4b5563' : '#d1d5db';
            this.ctx.lineWidth = 2;

            // Оси
            this.ctx.beginPath();
            this.ctx.moveTo(this.options.padding, this.options.padding);
            this.ctx.lineTo(this.options.padding, this.height - this.options.padding);
            this.ctx.lineTo(this.width - this.options.padding, this.height - this.options.padding);
            this.ctx.stroke();

            // Y-axis метки
            const maxValue = Math.max(...this.data.map(d => d.total)) + 2;
            this.ctx.fillStyle = Utils.getColor('text');
            this.ctx.font = '12px system-ui, -apple-system, sans-serif';
            this.ctx.textAlign = 'right';

            for (let i = 0; i <= this.options.gridLines; i++) {
                const y = this.options.padding + (this.chartHeight / this.options.gridLines) * i;
                const value = Math.round(maxValue - (maxValue / this.options.gridLines) * i);
                this.ctx.fillText(value, this.options.padding - 10, y + 4);
            }
        }

        drawData() {
            const maxValue = Math.max(...this.data.map(d => d.total)) + 2;
            const pointSpacing = this.chartWidth / (this.data.length - 1 || 1);

            // Рисуем линии и точки
            this.drawLine(this.data.map(d => d.approved), CONFIG.colors.approved, maxValue, pointSpacing);
            this.drawLine(this.data.map(d => d.needs_work), CONFIG.colors.needsWork, maxValue, pointSpacing);
            this.drawLine(this.data.map(d => d.rejected), CONFIG.colors.rejected, maxValue, pointSpacing);

            // X-axis метки
            this.ctx.fillStyle = Utils.getColor('text');
            this.ctx.font = '11px system-ui, -apple-system, sans-serif';
            this.ctx.textAlign = 'center';

            this.data.forEach((item, index) => {
                if (index % 3 === 0 || index === this.data.length - 1) {
                    const x = this.options.padding + index * pointSpacing;
                    this.ctx.fillText(item.day, x, this.height - this.options.padding + 20);
                }
            });
        }

        drawLine(values, color, maxValue, spacing) {
            // Линия
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 3;
            this.ctx.lineJoin = 'round';
            this.ctx.lineCap = 'round';
            this.ctx.shadowColor = color;
            this.ctx.shadowBlur = 4;

            this.ctx.beginPath();
            values.forEach((value, index) => {
                const x = this.options.padding + index * spacing;
                const y = this.height - this.options.padding - (value / maxValue * this.chartHeight);

                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            });
            this.ctx.stroke();

            // Сброс тени
            this.ctx.shadowColor = 'transparent';
            this.ctx.shadowBlur = 0;

            // Точки
            values.forEach((value, index) => {
                const x = this.options.padding + index * spacing;
                const y = this.height - this.options.padding - (value / maxValue * this.chartHeight);

                // Внешний круг (тень)
                this.ctx.fillStyle = color;
                this.ctx.globalAlpha = 0.2;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 8, 0, Math.PI * 2);
                this.ctx.fill();

                // Основная точка
                this.ctx.globalAlpha = 1;
                this.ctx.fillStyle = color;
                this.ctx.beginPath();
                this.ctx.arc(x, y, 5, 0, Math.PI * 2);
                this.ctx.fill();

                // Белый центр
                this.ctx.fillStyle = '#ffffff';
                this.ctx.beginPath();
                this.ctx.arc(x, y, 2, 0, Math.PI * 2);
                this.ctx.fill();
            });
        }

        setupInteraction() {
            const maxValue = Math.max(...this.data.map(d => d.total)) + 2;
            const pointSpacing = this.chartWidth / (this.data.length - 1 || 1);
            
            let tooltip = document.getElementById('chart-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'chart-tooltip';
                tooltip.style.cssText = `
                    position: fixed;
                    background: var(--card-bg, #ffffff);
                    border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
                    border-radius: 12px;
                    padding: 12px 16px;
                    font-size: 13px;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s ease;
                    z-index: 1000;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
                    max-width: 200px;
                `;
                document.body.appendChild(tooltip);
            }

            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                // Проверяем наведение на точку
                let hoveredPoint = null;
                this.data.forEach((item, index) => {
                    const pointX = this.options.padding + index * pointSpacing;
                    const values = [
                        { name: 'Одобрено', value: item.approved, color: CONFIG.colors.approved },
                        { name: 'Доработка', value: item.needs_work, color: CONFIG.colors.needsWork },
                        { name: 'Отклонено', value: item.rejected, color: CONFIG.colors.rejected }
                    ];

                    values.forEach(v => {
                        const pointY = this.height - this.options.padding - (v.value / maxValue * this.chartHeight);
                        const distance = Math.sqrt(Math.pow(x - pointX, 2) + Math.pow(y - pointY, 2));

                        if (distance < 10) {
                            hoveredPoint = { ...v, day: item.day, x: e.clientX, y: e.clientY };
                        }
                    });
                });

                if (hoveredPoint) {
                    tooltip.innerHTML = `
                        <div style="font-weight: 600; margin-bottom: 6px; color: var(--text-color);">${hoveredPoint.day}</div>
                        <div style="display: flex; align-items: center; gap: 8px; color: var(--text-secondary);">
                            <span style="width: 12px; height: 12px; background: ${hoveredPoint.color}; border-radius: 50%; display: inline-block;"></span>
                            ${hoveredPoint.name}: <strong>${hoveredPoint.value}</strong>
                        </div>
                    `;
                    tooltip.style.left = (hoveredPoint.x + 15) + 'px';
                    tooltip.style.top = (hoveredPoint.y - 15) + 'px';
                    tooltip.style.opacity = '1';
                    this.canvas.style.cursor = 'pointer';
                } else {
                    tooltip.style.opacity = '0';
                    this.canvas.style.cursor = 'default';
                }
            });

            this.canvas.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
                this.canvas.style.cursor = 'default';
            });
        }
    }

    // Инициализация при загрузке
    function initialize() {
        // Анимация значений в карточках
        animateStatValues();

        // Анимация прогресс-баров
        animateProgressBars();

        // Инициализация графика
        initializeDailyChart();

        // Интерактивность для легенды
        setupLegendInteraction();

        // Наблюдатель за темой
        observeThemeChanges();

        // Resize handler
        window.addEventListener('resize', Utils.debounce(() => {
            if (window.dailyChart) {
                window.dailyChart.resize();
                window.dailyChart.draw();
            }
        }, 250));
    }

    function animateStatValues() {
        const statValues = document.querySelectorAll('.stat-value, .performance-value');
        
        statValues.forEach(element => {
            const finalText = element.textContent.trim();
            const matches = finalText.match(/[\d.,]+/);
            
            if (!matches) return;
            
            const finalNumber = parseFloat(matches[0].replace(',', '.'));
            const suffix = finalText.replace(matches[0], '').trim();
            
            element.textContent = '0' + suffix;
            
            setTimeout(() => {
                Utils.animateValue(element, 0, finalNumber, CONFIG.animationDuration, suffix);
            }, 100);
        });
    }

    function animateProgressBars() {
        const progressBars = document.querySelectorAll(
            '.course-progress-fill, .week-bar, .progress-fill'
        );
        
        progressBars.forEach(bar => {
            const finalWidth = bar.style.width || '0%';
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
                bar.style.width = finalWidth;
            }, 200);
        });
    }

    function initializeDailyChart() {
        const canvas = document.getElementById('dailyCanvas');
        if (!canvas) return;

        const dataElement = document.getElementById('daily-activity-data');
        if (!dataElement) return;

        try {
            const data = JSON.parse(dataElement.textContent);
            window.dailyChart = new ChartRenderer('dailyCanvas', data);
        } catch (e) {
        }
    }

    function setupLegendInteraction() {
        const legendItems = document.querySelectorAll('.legend-item');
        
        legendItems.forEach(item => {
            item.addEventListener('click', function() {
                this.classList.toggle('inactive');
                
                // Можно добавить логику фильтрации данных графика
                const label = this.querySelector('.legend-label').textContent;
            });
        });
    }

    function observeThemeChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    if (window.dailyChart) {
                        window.dailyChart.draw();
                    }
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    // Tooltip функционал для month bars
    function setupMonthBarTooltips() {
        const monthBars = document.querySelectorAll('.month-bar');
        
        monthBars.forEach(bar => {
            bar.addEventListener('mouseenter', function() {
                const tooltip = this.getAttribute('data-tooltip');
                if (!tooltip) return;

                // Создаем tooltip элемент
                const tooltipEl = document.createElement('div');
                tooltipEl.className = 'month-bar-tooltip';
                tooltipEl.textContent = tooltip;
                tooltipEl.style.cssText = `
                    position: absolute;
                    background: var(--card-bg, #ffffff);
                    border: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: 600;
                    white-space: nowrap;
                    z-index: 100;
                    pointer-events: none;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    color: var(--text-color);
                `;

                this.style.position = 'relative';
                this.appendChild(tooltipEl);

                // Позиционирование
                const rect = this.getBoundingClientRect();
                tooltipEl.style.bottom = '100%';
                tooltipEl.style.left = '50%';
                tooltipEl.style.transform = 'translateX(-50%) translateY(-8px)';
            });

            bar.addEventListener('mouseleave', function() {
                const tooltip = this.querySelector('.month-bar-tooltip');
                if (tooltip) {
                    tooltip.remove();
                }
            });
        });
    }

    // Запуск при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    // Экспорт для внешнего использования
    window.StatisticsCharts = {
        initialize,
        ChartRenderer,
        Utils
    };
})();
