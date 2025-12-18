/**
 * Authentication pages JavaScript
 * Handles password toggle and strength checking for signin/signup pages
 */

/**
 * Toggle password visibility
 * @param {string} inputId - ID of the password input field
 */
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const toggle = input.parentElement.querySelector('.password-toggle');
    if (!toggle) return;
    
    const eyeOpen = toggle.querySelector('.eye-open');
    const eyeClosed = toggle.querySelector('.eye-closed');
    
    if (input.type === 'password') {
        input.type = 'text';
        if (eyeOpen) eyeOpen.style.display = 'none';
        if (eyeClosed) eyeClosed.style.display = 'block';
    } else {
        input.type = 'password';
        if (eyeOpen) eyeOpen.style.display = 'block';
        if (eyeClosed) eyeClosed.style.display = 'none';
    }
}

/**
 * Initialize password strength checker
 * Should be called with password field ID from template
 */
function initPasswordStrength(passwordFieldId, weakText, mediumText, goodText, strongText) {
    const passwordField = document.getElementById(passwordFieldId);
    if (!passwordField) return;
    
    passwordField.addEventListener('input', function(e) {
        const password = e.target.value;
        const strengthBar = document.getElementById('strength-bar');
        const strengthText = document.getElementById('strength-text');
        
        if (!strengthBar || !strengthText) return;
        
        let strength = 0;
        let text = weakText;
        
        // Check password strength criteria
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        // Set strength level and visual feedback
        if (strength === 0) {
            strengthBar.style.width = '0%';
            strengthBar.className = 'strength-bar';
            text = weakText;
        } else if (strength <= 2) {
            strengthBar.style.width = '25%';
            strengthBar.className = 'strength-bar weak';
            text = weakText;
        } else if (strength <= 3) {
            strengthBar.style.width = '50%';
            strengthBar.className = 'strength-bar medium';
            text = mediumText;
        } else if (strength <= 4) {
            strengthBar.style.width = '75%';
            strengthBar.className = 'strength-bar good';
            text = goodText;
        } else {
            strengthBar.style.width = '100%';
            strengthBar.className = 'strength-bar strong';
            text = strongText;
        }
        
        strengthText.textContent = text;
    });
}

/**
 * Initialize password strength checker for password reset with requirements
 * Should be called with password field ID from template and translated strings
 */
function initPasswordStrengthWithRequirements(passwordFieldId, translations) {
    const passwordInput = document.getElementById(passwordFieldId);
    if (!passwordInput) return;
    
    passwordInput.addEventListener('input', function() {
        checkPasswordStrength(this.value, translations);
        checkPasswordRequirements(this.value);
    });
}

/**
 * Check password strength for reset form
 */
function checkPasswordStrength(password, translations) {
    const strengthContainer = document.querySelector('.password-strength-container');
    const strengthText = document.getElementById('strength-text');
    
    if (!strengthContainer || !strengthText) return;
    
    let score = 0;
    let feedback = '';
    
    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Character variety checks
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    // Remove previous strength classes
    strengthContainer.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
    
    if (password.length === 0) {
        feedback = translations.default || 'Сила пароля';
    } else if (score <= 2) {
        strengthContainer.classList.add('strength-weak');
        feedback = translations.weak || 'Слабый';
    } else if (score <= 4) {
        strengthContainer.classList.add('strength-fair');
        feedback = translations.fair || 'Удовлетворительный';
    } else if (score <= 5) {
        strengthContainer.classList.add('strength-good');
        feedback = translations.good || 'Хороший';
    } else {
        strengthContainer.classList.add('strength-strong');
        feedback = translations.strong || 'Отличный';
    }
    
    strengthText.textContent = feedback;
}

/**
 * Check password requirements and update UI
 */
function checkPasswordRequirements(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };
    
    Object.keys(requirements).forEach(requirement => {
        const item = document.querySelector(`[data-requirement="${requirement}"]`);
        if (item) {
            if (requirements[requirement]) {
                item.classList.add('valid');
            } else {
                item.classList.remove('valid');
            }
        }
    });
}
