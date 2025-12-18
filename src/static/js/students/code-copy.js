// Code Copy Functionality

document.addEventListener('DOMContentLoaded', function() {

    // Add copy buttons to all code blocks
    addCopyButtonsToCodeBlocks();
});

function addCopyButtonsToCodeBlocks() {
    // Find all pre elements with code - ищем внутри контейнеров
    const codeBlocks = document.querySelectorAll('.article-text-revolutionary pre, .markdown-content pre, .step-section-content pre');

    codeBlocks.forEach((pre, index) => {
        // Skip if already has a wrapper
        if (pre.parentElement.classList.contains('code-block-wrapper')) {

            return;
        }

        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.classList.add('code-block-wrapper');
        
        // Insert wrapper before pre element
        pre.parentNode.insertBefore(wrapper, pre);
        
        // Move pre into wrapper
        wrapper.appendChild(pre);
        
        // Create copy button
        const copyButton = createCopyButton(pre, index);
        wrapper.appendChild(copyButton);
    });
}

function createCopyButton(codeElement, index) {
    const button = document.createElement('button');
    button.classList.add('copy-code-btn');
    button.setAttribute('data-code-index', index);
    button.innerHTML = `
        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/>
        </svg>
        <span class="copy-text">Копировать</span>
    `;
    
    button.addEventListener('click', () => copyCodeToClipboard(codeElement, button));
    
    return button;
}

async function copyCodeToClipboard(codeElement, button) {
    // Get the code text
    let codeText = '';
    
    // Check if it's a highlight block (Pygments)
    const highlightElement = codeElement.querySelector('.highlight');
    if (highlightElement) {
        codeText = highlightElement.textContent || highlightElement.innerText;
    } else {
        // Regular code block
        const codeTag = codeElement.querySelector('code');
        codeText = codeTag ? (codeTag.textContent || codeTag.innerText) : (codeElement.textContent || codeElement.innerText);
    }
    
    // Clean up the text (remove extra whitespace)
    codeText = codeText.trim();
    
    try {
        // Use modern clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(codeText);
        } else {
            // Fallback for older browsers
            fallbackCopyTextToClipboard(codeText);
        }
        
        // Show success feedback
        showCopySuccess(button);
        
    } catch (err) {

        // Try fallback method
        try {
            fallbackCopyTextToClipboard(codeText);
            showCopySuccess(button);
        } catch (fallbackErr) {

            showCopyError(button);
        }
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (!successful) {
            throw new Error('execCommand failed');
        }
    } finally {
        document.body.removeChild(textArea);
    }
}

function showCopySuccess(button) {
    const originalHTML = button.innerHTML;
    
    button.classList.add('copied');
    button.innerHTML = `
        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
        </svg>
        <span class="copy-text">Скопировано!</span>
    `;
    
    // Reset after 2 seconds
    setTimeout(() => {
        button.classList.remove('copied');
        button.innerHTML = originalHTML;
    }, 2000);
}

function showCopyError(button) {
    const originalHTML = button.innerHTML;
    
    button.innerHTML = `
        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
        </svg>
        <span class="copy-text">Ошибка</span>
    `;
    
    // Reset after 2 seconds
    setTimeout(() => {
        button.innerHTML = originalHTML;
    }, 2000);
}

// Export for global use
window.addCopyButtonsToCodeBlocks = addCopyButtonsToCodeBlocks;