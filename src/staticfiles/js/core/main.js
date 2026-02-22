/**
 * PyLand - Современная интерактивность
 */

// Utility функции
const PyLand = {
  // Селекторы
  select: (selector, context = document) => context.querySelector(selector),
  selectAll: (selector, context = document) => context.querySelectorAll(selector),

  // Добавление/удаление классов
  addClass: (element, className) => element?.classList.add(className),
  removeClass: (element, className) => element?.classList.remove(className),
  toggleClass: (element, className) => element?.classList.toggle(className),
  hasClass: (element, className) => element?.classList.contains(className),

  // События
  on: (element, event, handler, options = {}) => {
    if (element) {
      element.addEventListener(event, handler, options);
    }
  },

  off: (element, event, handler) => {
    if (element) {
      element.removeEventListener(event, handler);
    }
  },

  // Debounce
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle
  throttle: (func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  },

  // Анимации
  animate: (element, keyframes, options = {}) => {
    if (element && element.animate) {
      return element.animate(keyframes, {
        duration: 300,
        easing: 'ease-out',
        fill: 'forwards',
        ...options
      });
    }
  }
};

// Система языков
class LanguageManager {
  constructor() {
    this.languages = {
      'ru': { name: 'Русский', native: 'РУ', flag: '🇷🇺' },
      'ka': { name: 'ქართული', native: 'ქარ', flag: '🇬🇪' },
      'en': { name: 'English', native: 'EN', flag: '�🇧' }
    };

    // Определяем текущий язык из URL префикса, а не из localStorage
    this.currentLanguage = this.getCurrentLanguageFromURL();
    this.init();
  }

  getCurrentLanguageFromURL() {
    // Извлекаем языковой префикс из URL (например /en/ или /ru/)
    const pathMatch = window.location.pathname.match(/^\/([a-z]{2})\//);
    if (pathMatch && this.languages[pathMatch[1]]) {
      const langFromURL = pathMatch[1];
      // Синхронизируем localStorage с реальным языком страницы
      localStorage.setItem('language', langFromURL);
      return langFromURL;
    }
    // Фолбэк на русский, если префикс не найден
    return 'ru';
  }

  init() {
    // НЕ обновляем отображение при загрузке - Django шаблон уже это сделал
    // this.updateCurrentLanguageDisplay();

    // Проверяем, было ли изменение языка
    this.checkLanguageChanged();

    // Обработчики для опций языка (dropdown управляется универсальной системой)
    const options = document.querySelectorAll('.language-option');
    options.forEach(option => {
      const langCode = option.getAttribute('data-lang');

      option.addEventListener('click', (e) => {
        e.preventDefault();
        this.changeLanguage(langCode);
      });
    });
  }

  checkLanguageChanged() {
    // Проверяем флаг смены языка в sessionStorage
    const langChanged = sessionStorage.getItem('language_changed');
    if (langChanged) {
      const langData = this.languages[langChanged];
      if (langData) {
        // Тексты уведомлений на разных языках
        const notificationTexts = {
          'ru': 'Язык изменен на',
          'ka': 'ენა შეიცვალა',
          'en': 'Language changed to'
        };

        // Используем setTimeout чтобы дать время NotificationManager инициализироваться
        setTimeout(() => {
          if (window.notificationManager) {
            const message = `${notificationTexts[langChanged]} ${langData.name}`;
            window.notificationManager.show(message, 'success', 3000);
          }
        }, 100);
      }
      sessionStorage.removeItem('language_changed');
    }
  }

  updateCurrentLanguageDisplay() {
    // Обновляем флаг и текст в триггере согласно текущему языку
    const flagElement = document.querySelector('[data-current-flag]');
    const langElement = document.querySelector('[data-current-lang]');

    if (flagElement && langElement && this.languages[this.currentLanguage]) {
      const langData = this.languages[this.currentLanguage];
      flagElement.textContent = langData.flag;
      langElement.textContent = langData.native;
    }
  }

  changeLanguage(langCode) {
    if (this.languages[langCode]) {
      this.currentLanguage = langCode;
      localStorage.setItem('language', langCode);

      // Сохраняем флаг для показа уведомления после перезагрузки
      sessionStorage.setItem('language_changed', langCode);

      // Переключиться на нужный язык через Django i18n
      this.redirectToLanguage(langCode);
    }
  }

  redirectToLanguage(langCode) {
    const currentPath = window.location.pathname;

    // Убираем существующий языковой префикс
    const pathWithoutLang = currentPath.replace(/^\/[a-z]{2}\//, '/');

    // Формируем новый путь с языковым префиксом
    // Теперь все языки имеют префикс, включая русский
    const newPath = `/${langCode}${pathWithoutLang}`;

    // Переходим на новую страницу
    window.location.href = newPath + window.location.search;
  }
}

// Система тем
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme') || 'light';
    this.init();
  }

  init() {
    this.applyTheme(this.currentTheme);
    this.setupToggle();
  }

  applyTheme(theme, showNotification = false) {
    document.documentElement.setAttribute('data-theme', theme);
    this.currentTheme = theme;
    localStorage.setItem('theme', theme);

    // Обновить все кнопки переключения темы
    this.updateToggleButtons();

    // Показать уведомление если запрошено
    if (showNotification && window.notificationManager && window.djangoTranslations) {
      const themeName = theme === 'light' ?
        window.djangoTranslations.lightTheme :
        window.djangoTranslations.darkTheme;
      const message = `${window.djangoTranslations.themeChanged}: ${themeName}`;
      window.notificationManager.show(message, 'success', 2000);
    }
  }

  updateToggleButtons() {
    const toggles = document.querySelectorAll('#theme-toggle, [data-theme-toggle]');
    toggles.forEach(toggle => {
      const sunIcon = toggle.querySelector('.sun-icon');
      const moonIcon = toggle.querySelector('.moon-icon');

      if (sunIcon && moonIcon) {
        if (this.currentTheme === 'dark') {
          sunIcon.style.transform = 'rotate(-90deg) scale(0)';
          sunIcon.style.opacity = '0';
          moonIcon.style.transform = 'rotate(0deg) scale(1)';
          moonIcon.style.opacity = '1';
        } else {
          sunIcon.style.transform = 'rotate(0deg) scale(1)';
          sunIcon.style.opacity = '1';
          moonIcon.style.transform = 'rotate(90deg) scale(0)';
          moonIcon.style.opacity = '0';
        }
      }
    });
  }

  toggle() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme, true);

    // Плавная анимация переключения
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
      document.body.style.transition = '';
    }, 300);
  }

  setupToggle() {
    // Основные переключатели в header
    const headerToggles = document.querySelectorAll('#theme-toggle');
    headerToggles.forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggle();
      });
    });

    // Мобильные переключатели
    const mobileToggles = document.querySelectorAll('[data-theme-toggle]');
    mobileToggles.forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggle();
      });
    });
  }
}

// Система уведомлений
class NotificationManager {
  constructor() {
    this.container = null;
    this.notifications = new Map();
    this.init();
  }

  init() {
    this.createContainer();
  }

  createContainer() {
    this.container = document.createElement('div');
    this.container.className = 'notification-container';
    this.container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    `;
    document.body.appendChild(this.container);
  }

  show(message, type = 'info', duration = 5000) {
    const id = Date.now() + Math.random();
    const notification = this.createNotification(message, type, id);

    this.container.appendChild(notification);
    this.notifications.set(id, notification);

    // Анимация появления
    PyLand.animate(notification, [
      { transform: 'translateX(100%)', opacity: 0 },
      { transform: 'translateX(0)', opacity: 1 }
    ], { duration: 300 });

    // Автоматическое скрытие
    if (duration > 0) {
      setTimeout(() => this.hide(id), duration);
    }

    return id;
  }

  createNotification(message, type, id) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
      background: white;
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
      border: 1px solid var(--gray-200);
      max-width: 400px;
      pointer-events: auto;
      cursor: pointer;
      transition: transform 0.2s ease;
      position: relative;
      overflow: hidden;
    `;

    // Цветовая полоска
    const stripe = document.createElement('div');
    stripe.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--${this.getTypeColor(type)}-500);
    `;

    // Иконка
    const icon = document.createElement('div');
    icon.style.cssText = `
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--${this.getTypeColor(type)}-100);
      color: var(--${this.getTypeColor(type)}-600);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: bold;
      float: left;
      margin-right: 12px;
      margin-top: 2px;
    `;
    icon.textContent = this.getTypeIcon(type);

    // Текст
    const text = document.createElement('div');
    text.textContent = message;
    text.style.cssText = `
      color: #000000;
      font-size: 14px;
      line-height: 1.4;
      margin-left: 32px;
    `;

    notification.appendChild(stripe);
    notification.appendChild(icon);
    notification.appendChild(text);

    // Клик для закрытия
    PyLand.on(notification, 'click', () => this.hide(id));

    // Hover эффект
    PyLand.on(notification, 'mouseenter', () => {
      notification.style.transform = 'translateX(-4px)';
    });

    PyLand.on(notification, 'mouseleave', () => {
      notification.style.transform = 'translateX(0)';
    });

    return notification;
  }

  hide(id) {
    const notification = this.notifications.get(id);
    if (!notification) return;

    PyLand.animate(notification, [
      { transform: 'translateX(0)', opacity: 1 },
      { transform: 'translateX(100%)', opacity: 0 }
    ], { duration: 200 }).addEventListener('finish', () => {
      notification.remove();
      this.notifications.delete(id);
    });
  }

  getTypeColor(type) {
    const colors = {
      success: 'success',
      error: 'error',
      warning: 'warning',
      info: 'primary'
    };
    return colors[type] || 'primary';
  }

  getTypeIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '!',
      info: 'i'
    };
    return icons[type] || 'i';
  }
}

// Система модальных окон
class ModalManager {
  constructor() {
    this.activeModals = new Set();
    this.init();
  }

  init() {
    this.setupTriggers();
    this.setupKeyboardHandling();
  }

  setupTriggers() {
    PyLand.on(document, 'click', (e) => {
      const trigger = e.target.closest('[data-modal-target]');
      if (trigger) {
        e.preventDefault();
        const targetId = trigger.getAttribute('data-modal-target');
        this.open(targetId);
      }

      const closeBtn = e.target.closest('[data-modal-close]');
      if (closeBtn) {
        e.preventDefault();
        const modal = closeBtn.closest('.modal-overlay');
        if (modal) {
          this.close(modal.id);
        }
      }
    });

    // Клик по оверлею для закрытия
    PyLand.on(document, 'click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.close(e.target.id);
      }
    });
  }

  setupKeyboardHandling() {
    PyLand.on(document, 'keydown', (e) => {
      if (e.key === 'Escape' && this.activeModals.size > 0) {
        const lastModal = Array.from(this.activeModals).pop();
        this.close(lastModal);
      }
    });
  }

  open(modalId) {
    const modal = PyLand.select(`#${modalId}`);
    if (!modal) return;

    this.activeModals.add(modalId);
    PyLand.addClass(modal, 'active');
    document.body.style.overflow = 'hidden';

    // Фокус на модальном окне
    const firstFocusable = modal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (firstFocusable) {
      firstFocusable.focus();
    }

    // Анимация
    const modalContent = modal.querySelector('.modal');
    if (modalContent) {
      PyLand.animate(modalContent, [
        { transform: 'scale(0.9) translateY(20px)', opacity: 0 },
        { transform: 'scale(1) translateY(0)', opacity: 1 }
      ], { duration: 200 });
    }
  }

  close(modalId) {
    const modal = PyLand.select(`#${modalId}`);
    if (!modal) return;

    this.activeModals.delete(modalId);
    PyLand.removeClass(modal, 'active');

    if (this.activeModals.size === 0) {
      document.body.style.overflow = '';
    }
  }
}

// Система прогресс-баров
class ProgressManager {
  static animateProgress(element, targetValue, duration = 1000) {
    if (!element) return;

    const startValue = parseInt(element.style.width) || 0;
    const difference = targetValue - startValue;
    const startTime = performance.now();

    function updateProgress(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (difference * easeOutCubic);

      element.style.width = `${currentValue}%`;

      // Обновить текст если есть
      const valueText = element.parentElement?.querySelector('.progress-text');
      if (valueText) {
        valueText.textContent = `${Math.round(currentValue)}%`;
      }

      if (progress < 1) {
        requestAnimationFrame(updateProgress);
      }
    }

    requestAnimationFrame(updateProgress);
  }

  static initProgressBars() {
    const progressBars = PyLand.selectAll('.progress-bar[data-progress]');

    progressBars.forEach(bar => {
      const targetValue = parseInt(bar.getAttribute('data-progress'));

      // Intersection Observer для анимации при появлении в viewport
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.animateProgress(bar, targetValue);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });

      observer.observe(bar);
    });
  }
}

// Система анимаций при скролле
class ScrollAnimations {
  constructor() {
    this.observer = null;
    this.init();
  }

  init() {
    this.setupIntersectionObserver();
    this.setupParallax();
    this.setupScrollProgress();
  }

  setupIntersectionObserver() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          const animationClass = element.getAttribute('data-animate') || 'animate-fade-in-up';
          const delay = element.getAttribute('data-delay') || '0';

          setTimeout(() => {
            PyLand.addClass(element, animationClass);
          }, parseInt(delay));

          this.observer.unobserve(element);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    // Наблюдение за элементами с data-animate
    const animatedElements = PyLand.selectAll('[data-animate]');
    animatedElements.forEach(el => this.observer.observe(el));
  }

  setupParallax() {
    const parallaxElements = PyLand.selectAll('.parallax');

    if (parallaxElements.length === 0) return;

    const updateParallax = PyLand.throttle(() => {
      const scrollTop = window.pageYOffset;

      parallaxElements.forEach(element => {
        const speed = parseFloat(element.getAttribute('data-speed')) || 0.5;
        const yPos = -(scrollTop * speed);
        element.style.transform = `translate3d(0, ${yPos}px, 0)`;
      });
    }, 16);

    PyLand.on(window, 'scroll', updateParallax);
  }

  setupScrollProgress() {
    const progressBar = PyLand.select('.scroll-progress');
    if (!progressBar) return;

    const updateScrollProgress = PyLand.throttle(() => {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;

      progressBar.style.width = scrolled + '%';
    }, 16);

    PyLand.on(window, 'scroll', updateScrollProgress);
  }
}

// Система управления формами
class FormManager {
  constructor() {
    this.init();
  }

  init() {
    this.setupValidation();
    this.setupEnhancements();
  }

  setupValidation() {
    const forms = PyLand.selectAll('form[data-validate]');

    forms.forEach(form => {
      PyLand.on(form, 'submit', (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
        }
      });

      // Валидация в реальном времени
      const inputs = form.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        PyLand.on(input, 'blur', () => this.validateField(input));
        PyLand.on(input, 'input', PyLand.debounce(() => this.validateField(input), 300));
      });
    });
  }

  validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });

    return isValid;
  }

  validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;
    let message = '';

    // Проверка обязательных полей
    if (field.hasAttribute('required') && !value) {
      isValid = false;
      message = 'Это поле обязательно для заполнения';
    }

    // Проверка email
    if (type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        message = 'Введите корректный email адрес';
      }
    }

    // Проверка пароля
    if (type === 'password' && value && field.getAttribute('data-min-length')) {
      const minLength = parseInt(field.getAttribute('data-min-length'));
      if (value.length < minLength) {
        isValid = false;
        message = `Пароль должен содержать минимум ${minLength} символов`;
      }
    }

    // Отображение результата
    this.showFieldValidation(field, isValid, message);

    return isValid;
  }

  showFieldValidation(field, isValid, message) {
    const errorElement = field.parentElement.querySelector('.form-error');

    if (isValid) {
      PyLand.removeClass(field, 'invalid');
      if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
      }
    } else {
      PyLand.addClass(field, 'invalid');
      if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
      }
    }
  }

  setupEnhancements() {
    // Автоматическое изменение размера textarea
    const textareas = PyLand.selectAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
      const resize = () => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
      };

      PyLand.on(textarea, 'input', resize);
      resize(); // Начальный размер
    });

    // Показ/скрытие пароля
    const passwordToggles = PyLand.selectAll('[data-password-toggle]');
    passwordToggles.forEach(toggle => {
      PyLand.on(toggle, 'click', () => {
        const targetId = toggle.getAttribute('data-password-toggle');
        const passwordField = PyLand.select(`#${targetId}`);

        if (passwordField.type === 'password') {
          passwordField.type = 'text';
          toggle.textContent = '👁️';
        } else {
          passwordField.type = 'password';
          toggle.textContent = '👁️‍🗨️';
        }
      });
    });
  }
}

// Инициализация всех систем
document.addEventListener('DOMContentLoaded', () => {
  // Инициализация менеджеров
  window.languageManager = new LanguageManager();
  window.themeManager = new ThemeManager();
  window.notificationManager = new NotificationManager();
  window.modalManager = new ModalManager();
  window.scrollAnimations = new ScrollAnimations();
  window.formManager = new FormManager();

  // Инициализация прогресс-баров
  ProgressManager.initProgressBars();

  // Глобальные утилиты
  window.PyLand = PyLand;

  // Smooth scroll для якорных ссылок
  PyLand.on(document, 'click', (e) => {
    const anchor = e.target.closest('a[href^="#"]');
    if (anchor && anchor.getAttribute('href') !== '#') {
      e.preventDefault();
      const targetId = anchor.getAttribute('href').substring(1);
      const target = PyLand.select(`#${targetId}`);

      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  });

  // Lazy loading для изображений
  const images = PyLand.selectAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.getAttribute('data-src');
        img.removeAttribute('data-src');
        PyLand.addClass(img, 'loaded');
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));

  // Инициализация Header функций
  initHeader();

});

// Header функциональность
function initHeader() {
  // Sticky header
  const header = PyLand.select('[data-sticky]');
  if (header) {
    window.addEventListener('scroll', PyLand.throttle(() => {
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }, 100));
  }

  // Dropdown меню
  const dropdowns = PyLand.selectAll('[data-dropdown]');

  dropdowns.forEach(dropdown => {
    const trigger = dropdown.querySelector('[data-dropdown-trigger]');
    const menu = dropdown.querySelector('[data-dropdown-menu]');

    if (trigger && menu) {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        // Закрываем другие dropdown'ы
        dropdowns.forEach(other => {
          if (other !== dropdown) {
            other.classList.remove('open');
          }
        });

        // Переключаем текущий
        const isOpen = dropdown.classList.contains('open');
        if (isOpen) {
          dropdown.classList.remove('open');
        } else {
          dropdown.classList.add('open');
        }
      });
    }
  });

  // Закрытие dropdown при клике вне
  document.addEventListener('click', (e) => {
    if (!e.target.closest('[data-dropdown]')) {
      dropdowns.forEach(dropdown => {
        dropdown.classList.remove('open');
      });
    }
  });

  // Мобильное меню
  const mobileToggle = PyLand.select('[data-mobile-toggle]');
  const mobileMenu = PyLand.select('[data-mobile-menu]');
  const mobileClose = PyLand.select('[data-mobile-close]');
  const mobileOverlay = PyLand.select('[data-mobile-overlay]');

  if (mobileToggle && mobileMenu) {
    const toggleMobileMenu = (open) => {
      if (open) {
        mobileMenu.classList.add('open');
        mobileOverlay?.classList.add('open');
        mobileToggle.classList.add('active');
        document.body.style.overflow = 'hidden';
      } else {
        mobileMenu.classList.remove('open');
        mobileOverlay?.classList.remove('open');
        mobileToggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    };

    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.contains('open');
      toggleMobileMenu(!isOpen);
    });

    mobileClose?.addEventListener('click', () => {
      toggleMobileMenu(false);
    });

    mobileOverlay?.addEventListener('click', () => {
      toggleMobileMenu(false);
    });

    // Закрытие при нажатии Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('open')) {
        toggleMobileMenu(false);
      }
    });
  }

  // Newsletter форма
  const newsletterForm = PyLand.select('[data-newsletter]');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const emailInput = newsletterForm.querySelector('input[type="email"]');
      const submitBtn = newsletterForm.querySelector('button[type="submit"]');

      // Валидация email для незарегистрированных
      if (emailInput && !emailInput.value.trim()) {
        if (window.notificationManager) {
          window.notificationManager.show('Пожалуйста, введите email', 'warning', 3000);
        }
        return;
      }

      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>';
      submitBtn.disabled = true;

      try {
        // Получаем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name="csrf-token"]')?.content ||
                         getCookie('csrftoken');

        // Определяем язык из URL
        const currentLang = window.location.pathname.split('/')[1] || 'ru';
        const subscribeUrl = `/${currentLang}/blog/newsletter/subscribe/`;

        // Формируем данные для отправки
        const formData = new URLSearchParams();
        if (emailInput) {
          formData.append('email', emailInput.value.trim());
        }

        const response = await fetch(subscribeUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
          },
          body: formData.toString(),
          credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success) {
          if (window.notificationManager) {
            window.notificationManager.show(data.message, 'success', 5000);
          }
          // Очищаем поле email
          if (emailInput) {
            emailInput.value = '';
          }
          // Скрываем блок подписки после успешной подписки
          const newsletterSection = newsletterForm.closest('.footer-newsletter');
          if (newsletterSection) {
            newsletterSection.style.transition = 'opacity 0.3s, transform 0.3s';
            newsletterSection.style.opacity = '0';
            newsletterSection.style.transform = 'translateY(-20px)';
            setTimeout(() => {
              newsletterSection.remove();
            }, 300);
          }
        } else {
          if (window.notificationManager) {
            window.notificationManager.show(data.message, 'warning', 5000);
          }
        }
      } catch (error) {
        if (window.notificationManager) {
          window.notificationManager.show('Произошла ошибка. Попробуйте позже.', 'error', 5000);
        }
      } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }
    });
  }

  // Анимация счетчиков в footer
  const counters = PyLand.selectAll('[data-counter]');
  if (counters.length > 0) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
          entry.target.classList.add('counted');
          const target = parseInt(entry.target.dataset.counter);
          let count = 0;
          const increment = target / 50;

          const updateCounter = () => {
            if (count < target) {
              count = Math.min(count + increment, target);
              entry.target.textContent = Math.floor(count);
              requestAnimationFrame(updateCounter);
            } else {
              entry.target.textContent = target;
            }
          };

          updateCounter();
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
  }

  // Анимация счётчиков в секции современной статистики (.stat-modern-number)
  const modernCounters = PyLand.selectAll('.stat-modern-number[data-count]');
  if (modernCounters.length > 0) {
    const modernCounterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
          entry.target.classList.add('counted');
          const target = parseInt(entry.target.dataset.count);
          const suffix = entry.target.dataset.suffix || '';
          const decimal = entry.target.dataset.decimal ? parseInt(entry.target.dataset.decimal) : 0;
          const divisor = Math.pow(10, decimal);
          let count = 0;
          const duration = 1600;
          const frames = 60;
          const increment = target / frames;

          const updateCounter = () => {
            if (count < target) {
              count = Math.min(count + increment, target);
              const value = decimal > 0
                ? (count / divisor).toFixed(decimal)
                : Math.floor(count);
              entry.target.textContent = value + suffix;
              requestAnimationFrame(updateCounter);
            } else {
              const finalValue = decimal > 0
                ? (target / divisor).toFixed(decimal)
                : target;
              entry.target.textContent = finalValue + suffix;
            }
          };

          updateCounter();
        }
      });
    }, { threshold: 0.4 });

    modernCounters.forEach(counter => modernCounterObserver.observe(counter));
  }

  // === СОВРЕМЕННЫЙ HERO БЛОК ===

  // Эффект печатания текста
  const typingEffect = () => {
    const typedTextElement = PyLand.select('.typed-text');
    if (!typedTextElement) return;

    const texts = [
      'Python • JavaScript • React • Django',
      'Индивидуальный подход к каждому',
      'Практические проекты и портфолио',
      'Поддержка менторов 24/7'
    ];

    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;

    function type() {
      const currentText = texts[textIndex];

      if (isDeleting) {
        typedTextElement.textContent = currentText.substring(0, charIndex - 1);
        charIndex--;
      } else {
        typedTextElement.textContent = currentText.substring(0, charIndex + 1);
        charIndex++;
      }

      let typeSpeed = isDeleting ? 50 : 100;

      if (!isDeleting && charIndex === currentText.length) {
        typeSpeed = 2000;
        isDeleting = true;
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % texts.length;
        typeSpeed = 500;
      }

      setTimeout(type, typeSpeed);
    }

    type();
  };

  // Анимация счетчиков статистики
  const animateStatCounters = () => {
    const statNumbers = PyLand.selectAll('.stat-number[data-target]');

    const statObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
          entry.target.classList.add('animated');
          const target = parseInt(entry.target.dataset.target);
          let count = 0;
          const increment = target / 60;

          const updateCounter = () => {
            if (count < target) {
              count = Math.min(count + increment, target);
              entry.target.textContent = Math.floor(count);
              requestAnimationFrame(updateCounter);
            } else {
              entry.target.textContent = target;
            }
          };

          updateCounter();
        }
      });
    }, { threshold: 0.5 });

    statNumbers.forEach(counter => statObserver.observe(counter));
  };

  // Анимация прогресс бара
  const animateProgressBar = () => {
    const progressFill = PyLand.select('.progress-fill[data-progress]');
    if (!progressFill) return;

    const progressObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
          entry.target.classList.add('animated');
          const progress = entry.target.dataset.progress;
          setTimeout(() => {
            entry.target.style.width = progress + '%';
          }, 500);
        }
      });
    }, { threshold: 0.5 });

    progressObserver.observe(progressFill);
  };

  // Параллакс эффект для орбов
  const parallaxOrbs = () => {
    const orbs = PyLand.selectAll('.orb');
    if (orbs.length === 0) return;

    let ticking = false;

    const updateParallax = () => {
      const scrolled = window.pageYOffset;
      const heroSection = PyLand.select('.modern-hero-section');

      if (heroSection) {
        const heroHeight = heroSection.offsetHeight;
        const scrollProgress = Math.min(scrolled / heroHeight, 1);

        orbs.forEach((orb, index) => {
          const speed = 0.5 + (index * 0.2);
          const yPos = scrollProgress * 100 * speed;
          orb.style.transform = `translateY(${yPos}px)`;
        });
      }

      ticking = false;
    };

    const requestTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    };

    window.addEventListener('scroll', requestTick);
  };

  // Инициализация современного hero блока
  if (PyLand.select('.modern-hero-section')) {
    typingEffect();
    animateStatCounters();
    animateProgressBar();
    parallaxOrbs();
  }

  // === СОВРЕМЕННЫЙ БЛОК СТАТИСТИКИ ===

  // Анимация счетчиков в современном блоке статистики
  const animateModernStats = () => {
    const statNumbers = PyLand.selectAll('.stat-number-modern[data-target]');
    const progressRings = PyLand.selectAll('.progress-ring circle:nth-child(2)');

    const modernStatsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
          entry.target.classList.add('animated');
          const target = parseInt(entry.target.dataset.target);
          let count = 0;
          const increment = target / 80; // Более плавная анимация

          const updateCounter = () => {
            if (count < target) {
              count = Math.min(count + increment, target);
              if (target === 24) {
                entry.target.textContent = '24/7';
              } else if (target === 98) {
                entry.target.textContent = Math.floor(count) + '%';
              } else {
                entry.target.textContent = Math.floor(count) + '+';
              }
              requestAnimationFrame(updateCounter);
            } else {
              if (target === 24) {
                entry.target.textContent = '24/7';
              } else if (target === 98) {
                entry.target.textContent = target + '%';
              } else {
                entry.target.textContent = target + '+';
              }
            }
          };

          updateCounter();
        }
      });
    }, { threshold: 0.3 });

    statNumbers.forEach(counter => modernStatsObserver.observe(counter));
  };

  // Анимация круговых прогресс-баров
  const animateProgressRings = () => {
    const progressRings = PyLand.selectAll('.progress-ring');

    const ringObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('ring-animated')) {
          entry.target.classList.add('ring-animated');
          const circle = entry.target.querySelector('circle:nth-child(2)');
          const card = entry.target.closest('.modern-stat-card');

          if (circle && card) {
            const stat = card.dataset.stat;
            let percentage = 0;

            switch(stat) {
              case 'support': percentage = 100; break;  // 24/7 support
              case 'practice': percentage = 100; break; // 100% practice
              case 'mentors': percentage = 95; break;   // Expert mentors
              case 'quality': percentage = 98; break;   // High quality
            }

            const circumference = 2 * Math.PI * 25; // r=25
            const offset = circumference - (percentage / 100) * circumference;

            setTimeout(() => {
              circle.style.strokeDashoffset = offset;
            }, 500);
          }
        }
      });
    }, { threshold: 0.5 });

    progressRings.forEach(ring => ringObserver.observe(ring));
  };

  // Интерактивность карточек статистики
  const addStatCardInteractivity = () => {
    const statCards = PyLand.selectAll('.modern-stat-card');

    statCards.forEach(card => {
      PyLand.on(card, 'mouseenter', () => {
        // Добавляем эффект свечения
        const pulse = card.querySelector('.stat-pulse');
        if (pulse) {
          pulse.style.animationDuration = '1s';
        }
      });

      PyLand.on(card, 'mouseleave', () => {
        // Возвращаем обычную анимацию
        const pulse = card.querySelector('.stat-pulse');
        if (pulse) {
          pulse.style.animationDuration = '2s';
        }
      });

      // Добавляем клик эффект
      PyLand.on(card, 'click', () => {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        setTimeout(() => {
          card.style.transform = '';
        }, 200);
      });
    });
  };

  // Параллакс эффект для плавающих чисел
  const parallaxFloatingNumbers = () => {
    const floatingNumbers = PyLand.selectAll('.number-particle');
    if (floatingNumbers.length === 0) return;

    let ticking = false;

    const updateParallax = () => {
      const scrolled = window.pageYOffset;
      const statsSection = PyLand.select('.modern-stats-section');

      if (statsSection) {
        const rect = statsSection.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

        if (isVisible) {
          const scrollProgress = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / (window.innerHeight + rect.height)));

          floatingNumbers.forEach((number, index) => {
            const speed = 0.3 + (index * 0.1);
            const yPos = scrollProgress * 50 * speed;
            const rotation = scrollProgress * 10 * (index % 2 === 0 ? 1 : -1);
            number.style.transform = `translateY(${yPos}px) rotate(${rotation}deg)`;
          });
        }
      }

      ticking = false;
    };

    const requestTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    };

    window.addEventListener('scroll', requestTick);
  };

  // Инициализация современного блока статистики
  if (PyLand.select('.modern-stats-section')) {
    animateModernStats();
    animateProgressRings();
    addStatCardInteractivity();
    parallaxFloatingNumbers();
  }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PyLand, LanguageManager, ThemeManager, NotificationManager, ModalManager, ScrollAnimations, FormManager };
}
