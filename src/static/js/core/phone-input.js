/* International Phone Input Handler */

const phoneInputHandler = {
    countries: [
        { code: 'RU', name: 'Россия', dialCode: '+7', flag: '🇷🇺', mask: '(___) ___-__-__' },
        { code: 'GE', name: 'Грузия', dialCode: '+995', flag: '🇬🇪', mask: '___ __ __ __' },
        { code: 'KZ', name: 'Казахстан', dialCode: '+7', flag: '🇰🇿', mask: '(___) ___-__-__' },
        { code: 'BY', name: 'Беларусь', dialCode: '+375', flag: '🇧🇾', mask: '(__) ___-__-__' },
        { code: 'UA', name: 'Украина', dialCode: '+380', flag: '🇺🇦', mask: '(__) ___-__-__' },
        { code: 'AM', name: 'Армения', dialCode: '+374', flag: '🇦🇲', mask: '__ ___-___' },
        { code: 'AZ', name: 'Азербайджан', dialCode: '+994', flag: '🇦🇿', mask: '__ ___-__-__' },
        { code: 'KG', name: 'Киргизия', dialCode: '+996', flag: '🇰🇬', mask: '___ ___-___' },
        { code: 'TJ', name: 'Таджикистан', dialCode: '+992', flag: '🇹🇯', mask: '__ ___-____' },
        { code: 'UZ', name: 'Узбекистан', dialCode: '+998', flag: '🇺🇿', mask: '__ ___-____' },
        { code: 'MD', name: 'Молдова', dialCode: '+373', flag: '🇲🇩', mask: '____ ____' },
        { code: 'US', name: 'США', dialCode: '+1', flag: '🇺🇸', mask: '(___) ___-____' },
        { code: 'GB', name: 'Великобритания', dialCode: '+44', flag: '🇬🇧', mask: '____ ______' },
        { code: 'DE', name: 'Германия', dialCode: '+49', flag: '🇩🇪', mask: '___ ________' },
        { code: 'FR', name: 'Франция', dialCode: '+33', flag: '🇫🇷', mask: '_ __ __ __ __' },
        { code: 'IT', name: 'Италия', dialCode: '+39', flag: '🇮🇹', mask: '___ _______' },
        { code: 'ES', name: 'Испания', dialCode: '+34', flag: '🇪🇸', mask: '___ __ __ __' },
        { code: 'PL', name: 'Польша', dialCode: '+48', flag: '🇵🇱', mask: '___ ___-___' },
        { code: 'TR', name: 'Турция', dialCode: '+90', flag: '🇹🇷', mask: '___ ___-____' },
    ],

    init: function(selectElement, inputElement) {
        if (!selectElement || !inputElement) return;

        // Populate country select
        this.populateCountrySelect(selectElement);

        // Set default country based on input value or default to Russia
        const currentValue = inputElement.value;
        if (currentValue) {
            this.parsePhoneNumber(currentValue, selectElement, inputElement);
        } else {
            this.setCountry(selectElement, inputElement, 'RU');
        }

        // Add event listeners
        selectElement.addEventListener('change', () => {
            this.onCountryChange(selectElement, inputElement);
        });

        inputElement.addEventListener('input', (e) => {
            this.onPhoneInput(e, selectElement, inputElement);
        });

        inputElement.addEventListener('keydown', (e) => {
            this.onKeyDown(e, inputElement);
        });
    },

    populateCountrySelect: function(selectElement) {
        selectElement.innerHTML = '';
        this.countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country.code;
            option.textContent = `${country.flag} ${country.name} ${country.dialCode}`;
            option.dataset.dialCode = country.dialCode;
            option.dataset.mask = country.mask;
            selectElement.appendChild(option);
        });
    },

    setCountry: function(selectElement, inputElement, countryCode) {
        selectElement.value = countryCode;
        const country = this.countries.find(c => c.code === countryCode);
        if (country) {
            inputElement.placeholder = `${country.dialCode} ${country.mask}`;
            inputElement.dataset.dialCode = country.dialCode;
            inputElement.dataset.mask = country.mask;
        }
    },

    onCountryChange: function(selectElement, inputElement) {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const dialCode = selectedOption.dataset.dialCode;
        const mask = selectedOption.dataset.mask;

        inputElement.placeholder = `${dialCode} ${mask}`;
        inputElement.dataset.dialCode = dialCode;
        inputElement.dataset.mask = mask;

        // Clear input or update with new dial code
        const currentValue = inputElement.value.replace(/\D/g, '');
        if (currentValue) {
            inputElement.value = '';
        }
        inputElement.focus();
    },

    onPhoneInput: function(e, selectElement, inputElement) {
        const dialCode = inputElement.dataset.dialCode || '+7';
        let value = inputElement.value;

        // Remove all non-digits except the plus sign at the start
        value = value.replace(/[^\d+]/g, '');

        // Ensure it starts with the dial code
        if (!value.startsWith(dialCode)) {
            if (value.startsWith('+')) {
                // User is typing a different country code
                const enteredCode = value;
                const country = this.countries.find(c => enteredCode.startsWith(c.dialCode));
                if (country) {
                    this.setCountry(selectElement, inputElement, country.code);
                    value = enteredCode;
                } else {
                    value = dialCode + value.replace(/^\+/, '');
                }
            } else {
                value = dialCode + value;
            }
        }

        // Apply formatting based on country
        value = this.formatPhoneNumber(value, inputElement.dataset.mask, dialCode);

        inputElement.value = value;
    },

    formatPhoneNumber: function(value, mask, dialCode) {
        // Remove dial code for formatting
        const digits = value.replace(dialCode, '').replace(/\D/g, '');
        
        if (!digits) return dialCode + ' ';

        // Apply mask
        let formatted = dialCode + ' ';
        let digitIndex = 0;

        for (let i = 0; i < mask.length && digitIndex < digits.length; i++) {
            if (mask[i] === '_') {
                formatted += digits[digitIndex];
                digitIndex++;
            } else {
                formatted += mask[i];
            }
        }

        return formatted;
    },

    onKeyDown: function(e, inputElement) {
        const dialCode = inputElement.dataset.dialCode || '+7';
        
        // Prevent deleting the dial code
        if ((e.key === 'Backspace' || e.key === 'Delete') && 
            inputElement.selectionStart <= dialCode.length + 1) {
            e.preventDefault();
        }
    },

    parsePhoneNumber: function(phoneNumber, selectElement, inputElement) {
        if (!phoneNumber) return;

        // Find matching country by dial code
        let matchedCountry = null;
        
        for (const country of this.countries) {
            if (phoneNumber.startsWith(country.dialCode)) {
                matchedCountry = country;
                break;
            }
        }

        if (matchedCountry) {
            this.setCountry(selectElement, inputElement, matchedCountry.code);
            // Format the existing number
            const digits = phoneNumber.replace(/\D/g, '');
            const formatted = this.formatPhoneNumber('+' + digits, matchedCountry.mask, matchedCountry.dialCode);
            inputElement.value = formatted;
        } else {
            // Default to Russia if no match
            this.setCountry(selectElement, inputElement, 'RU');
        }
    },

    getFullPhoneNumber: function(inputElement) {
        return inputElement.value.replace(/\s/g, '');
    },

    validate: function(inputElement) {
        const value = inputElement.value.replace(/\s/g, '');
        const dialCode = inputElement.dataset.dialCode || '+7';
        
        // Minimum length check (dial code + at least 7 digits)
        return value.length >= dialCode.length + 7;
    }
};

// Auto-initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all phone inputs with class 'international-phone'
    document.querySelectorAll('.phone-input-group').forEach(group => {
        const select = group.querySelector('.country-select');
        const input = group.querySelector('.phone-number-input');
        if (select && input) {
            phoneInputHandler.init(select, input);
        }
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = phoneInputHandler;
}
