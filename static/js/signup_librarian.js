// 等待DOM完全加载后执行验证逻辑
document.addEventListener('DOMContentLoaded', function() {
    // 获取表单核心元素
    const form = document.querySelector('form');
    const submitBtn = form.querySelector('button[type="submit"]');

    // 定义管理员注册表单常见字段（可根据实际业务调整字段名）
    const formFields = {
        username: form.querySelector('input[name="username"]'),      // 用户名/账号
        email: form.querySelector('input[name="email"]'),            // 邮箱
        librarian_id: form.querySelector('input[name="librarian_id"]'), // 管理员工号
        password1: form.querySelector('input[name="password1"]'),    // 密码
        password2: form.querySelector('input[name="password2"]')     // 确认密码
    };

    // 创建统一的错误提示容器（无则创建，有则复用）
    let errorContainer = form.querySelector('.librarian-signup-error');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'librarian-signup-error';
        errorContainer.style.cssText = `
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 15px 0;
            display: none;
            font-size: 14px;
        `;
        // 插入到提交按钮上方
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * 管理员注册表单验证核心函数
     * @returns {Boolean} 验证通过返回true，否则false
     */
    const validateLibrarianForm = function() {
        const errors = [];

        // 1. 验证用户名（必填 + 长度限制）
        if (formFields.username) {
            const usernameVal = formFields.username.value.trim();
            if (!usernameVal) {
                errors.push('❌ 管理员账号不能为空');
            } 
        }

        // 2. 验证邮箱（选填但填了要符合格式）
        if (formFields.email && formFields.email.value.trim()) {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(formFields.email.value)) {
                errors.push('❌ 请输入有效的邮箱地址');
            }
        }

        // 3. 验证管理员工号（必填 + 格式限制）
        if (formFields.librarian_id) {
            const idVal = formFields.librarian_id.value.trim();
            if (!idVal) {
                errors.push('❌ 管理员工号不能为空');
            } 
        }

        // 4. 验证密码（必填 + 复杂度 + 长度）
        if (formFields.password1) {
            const pwdVal = formFields.password1.value.trim();
            if (!pwdVal) {
                errors.push('❌ 密码不能为空');
            } else if (pwdVal.length < 4) {
                errors.push('❌ 密码长度不能少于4位');
            } 
        }

        // 5. 验证确认密码（必填 + 与密码一致）
        if (formFields.password2) {
            const pwd2Val = formFields.password2.value.trim();
            if (!pwd2Val) {
                errors.push('❌ 请确认密码');
            } else if (formFields.password1 && pwd2Val !== formFields.password1.value) {
                errors.push('❌ 两次输入的密码不一致');
            }
        }

        // 渲染错误提示/清空提示
        if (errors.length > 0) {
            errorContainer.innerHTML = errors.join('<br>');
            errorContainer.style.display = 'block';
            return false;
        } else {
            errorContainer.style.display = 'none';
            return true;
        }
    };

    // 为所有输入框添加「失去焦点」实时验证
    Object.values(formFields).forEach(field => {
        if (field) {
            field.addEventListener('blur', validateLibrarianForm);
            // 输入时实时更新验证状态（提升体验）
            field.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validateLibrarianForm();
                }
            });
        }
    });

    // 表单提交时的最终验证（阻止非法提交）
    form.addEventListener('submit', function(e) {
        if (!validateLibrarianForm()) {
            e.preventDefault(); // 阻止表单提交
            // 平滑滚动到错误提示位置
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
});