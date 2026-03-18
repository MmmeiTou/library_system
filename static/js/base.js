/**
 * Book System - 精简基础JS
 * 不污染全局，不影响子模板
 */
(function() {
    'use strict';

    // 只在有 base 元素时执行
    if (!document.getElementById('bsNavbar')) return;

    // 缓存元素
    const el = {
        loader: document.getElementById('bsLoader'),
        navbar: document.getElementById('bsNavbar'),
        menuBtn: document.getElementById('bsMenuBtn'),
        navMenu: document.getElementById('bsNavMenu'),
        content: document.getElementById('bsContent')
    };

    // 页面加载完成
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

    // 导航栏滚动效果
    let scrolled = false;
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 30 && !scrolled) {
            el.navbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            scrolled = true;
        } else if (window.pageYOffset <= 30 && scrolled) {
            el.navbar.style.boxShadow = 'none';
            scrolled = false;
        }
    }, { passive: true });

    // 移动端菜单
    if (el.menuBtn && el.navMenu) {
        el.menuBtn.addEventListener('click', function() {
            el.navMenu.classList.toggle('show');
        });

        // 点击外部关闭
        document.addEventListener('click', function(e) {
            if (!el.navbar.contains(e.target) && el.navMenu.classList.contains('show')) {
                el.navMenu.classList.remove('show');
            }
        });
    }

    // 内容区动画
    if (el.content) {
        const observer = new MutationObserver(function() {
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

    // 工具函数 - 暴露给子模板使用
    window.BookSystem = {
        // 显示通知
        notify: function(msg, type) {
            // 移除旧通知
            const old = document.querySelector('.bs-toast');
            if (old) old.remove();

            const toast = document.createElement('div');
            toast.className = 'bs-toast';
            toast.textContent = msg;
            toast.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                padding: 0.75rem 1.25rem;
                background: ${type === 'error' ? '#e74c3c' : type === 'success' ? '#27ae60' : '#5b5fd9'};
                color: #fff;
                border-radius: 6px;
                font-size: 0.875rem;
                z-index: 9999;
                animation: bs-toast-in 0.3s ease;
            `;
            document.body.appendChild(toast);

            setTimeout(() => {
                toast.style.animation = 'bs-toast-out 0.3s ease forwards';
                setTimeout(() => toast.remove(), 300);
            }, 2500);
        },

        // 显示/隐藏加载
        loading: function(show) {
            if (!el.loader) return;
            if (show) {
                el.loader.style.display = 'flex';
                el.loader.classList.remove('hidden');
            } else {
                el.loader.classList.add('hidden');
                setTimeout(() => el.loader.style.display = 'none', 300);
            }
        }
    };

    // 添加 toast 动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes bs-toast-in { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes bs-toast-out { from { opacity: 1; transform: translateX(0); } to { opacity: 0; transform: translateX(20px); } }
    `;
    document.head.appendChild(style);

})();