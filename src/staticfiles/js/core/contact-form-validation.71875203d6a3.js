// Contact Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Простая валидация на клиенте
            const name = form.querySelector('input[name="first_name"]').value;
            const phoneInput = form.querySelector('input[name="phone_number"]');
            const phone = phoneInput ? phoneInput.value : '';
            const email = form.querySelector('input[name="email"]').value;
            const message = form.querySelector('textarea[name="message"]').value;
            const agree = form.querySelector('input[name="agree_terms"]').checked;
            
            if (!name || !phone || !email || !message) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля');
                return false;
            }
            
            if (!agree) {
                e.preventDefault();
                alert('Необходимо согласие с политикой конфиденциальности');
                return false;
            }
            
            // Проверка валидности телефона
            if (phoneInput && typeof phoneInputHandler !== 'undefined' && !phoneInputHandler.validate(phoneInput)) {
                e.preventDefault();
                alert('Пожалуйста, введите корректный номер телефона');
                return false;
            }
            
            // Если все ОК - форма отправится на сервер естественным образом
            // Django обработает валидацию и покажет сообщения через messages framework
        });
    }
});
