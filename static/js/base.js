(function () {
    'use strict';

    if (!document.getElementById('bsNavbar')) return;

    // Cache elements
    const el = {
        loader: document.getElementById('bsLoader'),
        content: document.getElementById('bsContent')
    };

    // When the page finishes loading → hide the loader
    function hideLoader() {
        if (el.loader) {
            el.loader.classList.add('hidden');
            setTimeout(() => el.loader.style.display = 'none', 300);
        }
    }

    if (document.readyState === 'complete') {
        hideLoader();
    } else {
        window.addEventListener('load', hideLoader);
    }

    // Content area animation (using MutationObserver to detect changes)
    if (el.content) {
        const observer = new MutationObserver(function () {
            el.content.style.opacity = '0';
            el.content.style.transform = 'translateY(10px)';
            requestAnimationFrame(() => {
                el.content.style.transition = 'all 0.4s ease';
                el.content.style.opacity = '1';
                el.content.style.transform = 'translateY(0)';
            });
        });
        observer.observe(el.content, { childList: true, subtree: true });
    }

})();