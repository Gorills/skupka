document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initContactForm();
    initPhoneMask();
    initSmoothScroll();
    initHeaderScroll();
    initAnimations();
    initDropdowns();
});

function initPhoneMask() {
    const input = document.getElementById('id_phone') || document.querySelector('.js-phone-mask');
    if (!input) return;

    function getDigits(value) {
        return value.replace(/\D/g, '');
    }

    function formatPhone(value) {
        var digits = getDigits(value);
        if (digits.length > 0 && digits[0] === '8') digits = '7' + digits.slice(1);
        if (digits.length > 0 && digits[0] !== '7') digits = '7' + digits;
        digits = digits.slice(0, 11);
        if (digits.length === 0) return '';
        var s = '+7';
        if (digits.length > 1) s += ' (' + digits.slice(1, 4);
        if (digits.length >= 4) s += ') ' + digits.slice(4, 7);
        if (digits.length >= 7) s += '-' + digits.slice(7, 9);
        if (digits.length >= 9) s += '-' + digits.slice(9, 11);
        return s;
    }

    function onInput() {
        var start = input.selectionStart;
        var oldLen = input.value.length;
        var oldDigits = getDigits(input.value);
        input.value = formatPhone(input.value);
        var newLen = input.value.length;
        var newDigits = getDigits(input.value);
        var diff = newDigits.length - oldDigits.length;
        var newStart = Math.max(0, start + (newLen - oldLen));
        input.setSelectionRange(newStart, newStart);
    }

    input.addEventListener('input', onInput);
    input.addEventListener('paste', function(e) {
        e.preventDefault();
        var pasted = (e.clipboardData || window.clipboardData).getData('text');
        var digits = getDigits(pasted);
        if (digits[0] === '8') digits = '7' + digits.slice(1);
        if (digits[0] !== '7') digits = '7' + digits;
        input.value = formatPhone(digits);
    });

    if (input.value) input.value = formatPhone(input.value);
}

function initMobileMenu() {
    const burgerBtn = document.getElementById('burger-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const closeBtn = document.getElementById('mobile-menu-close');
    
    if (!burgerBtn || !mobileMenu) return;
    
    let scrollPosition = 0;

    function closeMobileMenu() {
        burgerBtn.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        window.scrollTo(0, scrollPosition);
    }

    function openMobileMenu() {
        scrollPosition = window.scrollY || window.pageYOffset;
        burgerBtn.classList.add('active');
        mobileMenu.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
        document.body.style.top = `-${scrollPosition}px`;
        document.body.style.width = '100%';
    }
    
    burgerBtn.addEventListener('click', function() {
        if (mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMobileMenu);
    }
    
    const mobileLinks = mobileMenu.querySelectorAll('.mobile-menu__link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    const ctaBtn = mobileMenu.querySelector('.mobile-menu__cta');
    if (ctaBtn) {
        ctaBtn.addEventListener('click', closeMobileMenu);
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
}

function initContactForm() {
    const form = document.getElementById('contact-form-el');
    if (!form) return;
    
    const hasRecaptcha = document.getElementById('recaptcha-token');
    
    if (!hasRecaptcha) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm(form);
        });
    }
    
    window.submitContactForm = submitContactForm;
}

async function submitContactForm(form) {
    const submitBtn = form.querySelector('.contact-form__submit');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loading">Отправка...</span>';
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const formFields = form.querySelector('.contact-form__fields');
            const privacy = form.querySelector('.contact-form__privacy');
            const honeypot = form.querySelector('.contact-form__honeypot');
            
            if (formFields) formFields.style.display = 'none';
            if (honeypot) honeypot.style.display = 'none';
            submitBtn.style.display = 'none';
            if (privacy) privacy.style.display = 'none';
            
            const successEl = document.getElementById('form-success');
            if (successEl) {
                successEl.style.display = 'block';
                successEl.style.animation = 'fadeInUp 0.5s ease-out';
            }
        } else {
            let errorMessage = 'Пожалуйста, исправьте ошибки:\n';
            for (const field in data.errors) {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && input.type !== 'hidden') {
                    input.style.borderColor = '#ef4444';
                    input.addEventListener('focus', function() {
                        this.style.borderColor = '';
                    }, { once: true });
                }
                if (field === '__all__') {
                    errorMessage = data.errors[field].join('\n');
                } else {
                    errorMessage += `• ${data.errors[field].join(', ')}\n`;
                }
            }
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        showNotification('Произошла ошибка. Пожалуйста, позвоните нам.', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        submitBtn.style.opacity = '';
    }
}

function showNotification(message, type = 'info') {
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <span class="notification__icon">${type === 'error' ? '❌' : '✅'}</span>
        <span class="notification__text">${message}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        max-width: 400px;
        padding: 16px 24px;
        background: ${type === 'error' ? '#fef2f2' : '#f0fdf4'};
        border: 1px solid ${type === 'error' ? '#fecaca' : '#bbf7d0'};
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        display: flex;
        align-items: flex-start;
        gap: 12px;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        font-size: 14px;
        line-height: 1.5;
        color: ${type === 'error' ? '#991b1b' : '#166534'};
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const header = document.querySelector('.header');
                const headerHeight = header ? header.offsetHeight : 80;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initHeaderScroll() {
    const header = document.getElementById('header');
    if (!header) return;
    
    let lastScroll = 0;
    let ticking = false;
    
    function updateHeader() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    });
    
    updateHeader();
}

function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const animatedElements = document.querySelectorAll(
        '.service-card, .advantage-card, .stats__item, .location__item'
    );
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `all 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`;
        observer.observe(el);
    });
}

function initDropdowns() {
    const dropdowns = document.querySelectorAll('.header__dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.header__dropdown-toggle');
        const menu = dropdown.querySelector('.header__dropdown-menu');
        
        if (!toggle || !menu) return;
        
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdown.classList.toggle('active');
        });
        
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    });
}

const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .loading {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .loading::after {
        content: '';
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255,255,255,0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
