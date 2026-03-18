/**
 * Book System - 精简基础JS（仅保留加载动画和内容动画）
 * 不污染全局，不影响子模板
 */
(function () {
    'use strict';

    // 只在有 base 元素时执行
    if (!document.getElementById('bsNavbar')) return;

    // 缓存元素
    const el = {
        loader: document.getElementById('bsLoader'),
        content: document.getElementById('bsContent')
    };

    // 页面加载完成 → 隐藏 loader
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

    // 内容区动画（MutationObserver 监听变化）
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