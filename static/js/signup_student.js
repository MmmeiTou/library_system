// 等待DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取表单元素（适配Django form.as_p结构）
    const form = document.querySelector('form');
    // 定义学生注册常见字段（根据实际业务调整，若字段名不同可修改）
    const fieldSelectors = {
        username: form.querySelector('input[name="username"]'), // 用户名
        email: form.querySelector('input[name="email"]'),       // 邮箱
        student_id: form.querySelector('input[name="student_id"]'), // 学号
        password1: form.querySelector('input[name="password1"]'),   // 密码
        password2: form.querySelector('input[name="password2"]')    // 确认密码
    };

    // 创建统一的错误提示容器（如果不存在）
    let errorContainer = form.querySelector('.signup-error-container');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'signup-error-container';
        errorContainer.style.cssText = `
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 10px 15px;
            margin: 15px 0;
            display: none;
        `;
        // 将错误提示插入到提交按钮上方
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * 表单验证核心函数
     * @returns {Boolean} 验证通过返回true，否则false
     */
    const validateSignupForm = function() {
        let errorMessages = [];

        // 1. 验证用户名
        if (fieldSelectors.username) {
            if (!fieldSelectors.username.value.trim()) {
                errorMessages.push('✖ 用户名不能为空');
            } 
        }

        // 2. 验证邮箱（如果有邮箱字段）
        if (fieldSelectors.email && fieldSelectors.email.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(fieldSelectors.email.value)) {
                errorMessages.push('✖ 请输入有效的邮箱地址');
            }
        }

        // 3. 验证学号（如果有学号字段）
        if (fieldSelectors.student_id) {
            if (!fieldSelectors.student_id.value.trim()) {
                errorMessages.push('✖ 学号不能为空');
            } 
        }

        // 4. 验证密码
        if (fieldSelectors.password1) {
            if (!fieldSelectors.password1.value.trim()) {
                errorMessages.push('✖ 密码不能为空');
            } else {
                // 密码长度验证
                if (fieldSelectors.password1.value.length < 4) {
                    errorMessages.push('✖ 密码长度不能少于4位');
                }
                
            }
        }

        // 5. 验证确认密码
        if (fieldSelectors.password2) {
            if (!fieldSelectors.password2.value.trim()) {
                errorMessages.push('✖ 请确认密码');
            } else if (fieldSelectors.password1 && fieldSelectors.password1.value !== fieldSelectors.password2.value) {
                errorMessages.push('✖ 两次输入的密码不一致');
            }
        }

        // 显示/隐藏错误提示
        if (errorMessages.length > 0) {
            errorContainer.innerHTML = errorMessages.join('<br>');
            errorContainer.style.display = 'block';
            return false;
        } else {
            errorContainer.style.display = 'none';
            return true;
        }
    };

    // 为所有输入框添加实时验证（失去焦点时）
    Object.values(fieldSelectors).forEach(input => {
        if (input) {
            // 失去焦点验证
            input.addEventListener('blur', validateSignupForm);
            // 输入时实时更新验证状态
            input.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validateSignupForm();
                }
            });
        }
    });

    // 表单提交时的最终验证
    form.addEventListener('submit', function(e) {
        if (!validateSignupForm()) {
            e.preventDefault(); // 阻止表单提交
            // 滚动到错误提示位置（平滑滚动）
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});