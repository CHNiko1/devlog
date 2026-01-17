/**
 * DevLog Frontend JavaScript
 * Georgian Junior Developer Community Platform
 * Minimal vanilla JS for UI interactions
 */

(function() {
    'use strict';

    // ============================================
    // AUTO-CLOSE ALERTS
    // ============================================
    function initAutoCloseAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (!alert.classList.contains('alert-error')) {
                setTimeout(() => {
                    const closeButton = alert.querySelector('.btn-close');
                    if (closeButton) {
                        closeButton.click();
                    }
                }, 5000); // Close after 5 seconds
            }
        });
    }

    // ============================================
    // FORM VALIDATION
    // ============================================
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // ============================================
    // SMOOTH SCROLL TO ANCHOR LINKS
    // ============================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    // ============================================
    // NAVBAR COLLAPSE ON LINK CLICK (MOBILE)
    // ============================================
    function initNavbarCollapseOnClick() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse) {
            const navbarLinks = navbarCollapse.querySelectorAll('.nav-link');
            navbarLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                });
            });
        }
    }

    // ============================================
    // LAZY LOAD IMAGES (Optional)
    // ============================================
    function initLazyLoad() {
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[loading="lazy"]');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('loading');
                        observer.unobserve(img);
                    }
                });
            });
            images.forEach(img => imageObserver.observe(img));
        }
    }

    // ============================================
    // CHARACTER COUNTER FOR TEXTAREA
    // ============================================
    function initCharacterCounter() {
        const textareas = document.querySelectorAll('textarea[name="content"]');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                const count = this.value.length;
                const minChars = 10;
                
                if (count < minChars) {
                    this.classList.add('border-warning');
                } else {
                    this.classList.remove('border-warning');
                }
            });
        });
    }

    // ============================================
    // HANDLE AI SIMPLIFY BUTTON
    // ============================================
    function initAISimplify() {
        const simplifyBtn = document.querySelector('button[onclick="handleAISimplify()"]');
        if (simplifyBtn) {
            // AI button is already handled inline, but we can enhance it here if needed
        }
    }

    // ============================================
    // SEARCH FORM AUTO-SUBMIT
    // ============================================
    function initAutoSubmitSearch() {
        const searchInputs = document.querySelectorAll('input[name="q"]');
        searchInputs.forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    this.form.submit();
                }
            });
        });
    }

    // ============================================
    // ANIMATE ELEMENTS ON SCROLL
    // ============================================
    function initScrollAnimations() {
        if ('IntersectionObserver' in window) {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            document.querySelectorAll('.card, .post-card').forEach(el => {
                observer.observe(el);
            });
        }
    }

    // ============================================
    // COPY CODE BLOCKS (OPTIONAL)
    // ============================================
    function initCodeBlockCopy() {
        const codeBlocks = document.querySelectorAll('pre');
        codeBlocks.forEach(block => {
            const button = document.createElement('button');
            button.textContent = '📋 კოპირება';
            button.className = 'btn btn-sm btn-outline-secondary';
            button.style.position = 'absolute';
            button.style.top = '5px';
            button.style.right = '5px';
            button.style.fontSize = '0.75rem';
            button.style.zIndex = '10';
            
            block.style.position = 'relative';
            block.appendChild(button);

            button.addEventListener('click', function() {
                const code = block.textContent;
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = button.textContent;
                    button.textContent = '✅ კოპირებული!';
                    setTimeout(() => {
                        button.textContent = originalText;
                    }, 2000);
                }).catch(() => {
                    alert('დამაკოპირება ვერ მოხერხდა');
                });
            });
        });
    }

    // ============================================
    // INITIALIZE ALL ON DOM READY
    // ============================================
    function initAll() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                runInitializations();
            });
        } else {
            runInitializations();
        }
    }

    function runInitializations() {
        initAutoCloseAlerts();
        initFormValidation();
        initSmoothScroll();
        initNavbarCollapseOnClick();
        initLazyLoad();
        initCharacterCounter();
        initAISimplify();
        initAutoSubmitSearch();
        initScrollAnimations();
        initCodeBlockCopy();
    }

    // Start initialization
    initAll();

    // ============================================
    // GLOBAL UTILITY FUNCTIONS
    // ============================================

    /**
     * Handle AI Simplify button click
     */
    window.handleAISimplify = function() {
        const checkbox = document.getElementById('aiSimplify');
        if (checkbox && checkbox.checked) {
            // This would integrate with backend AI service
            alert('🚀 AI გამარტივება მალე ხელმისაწვდომი იქნება!');
            // TODO: Implement actual AI simplification API call
            // Example:
            // fetch('/api/simplify', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ post_id: postId, ai_simplify: true })
            // }).then(r => r.json()).then(data => {
            //     console.log('Simplified content:', data);
            // });
        }
    };

    /**
     * Show notification toast
     */
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container-fluid:first-of-type');
        if (container) {
            container.insertAdjacentElement('afterbegin', alertDiv);
            setTimeout(() => {
                alertDiv.remove();
            }, duration);
        }
    };

    /**
     * Format date to Georgian format
     */
    window.formatDateGE = function(date) {
        if (!date) return 'უცნობი';
        return new Date(date).toLocaleDateString('ka-GE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    };

    /**
     * Truncate text
     */
    window.truncateText = function(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

})();
