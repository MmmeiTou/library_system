// 等待DOM完全加载后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取表单及所有密码输入框（适配Django form.as_p渲染的结构）
    const form = document.getElementById('passwordChangeForm');
    // Django默认的密码修改表单字段名：old_password, new_password1, new_password2
    const oldPasswordInput = form.querySelector('input[name="old_password"]');
    const newPassword1Input = form.querySelector('input[name="new_password1"]');
    const newPassword2Input = form.querySelector('input[name="new_password2"]');

    // 创建统一的错误提示容器（如果不存在）
    let errorContainer = form.querySelector('.password-error-container');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'password-error-container alert alert-danger mt-3';
        errorContainer.style.display = 'none'; // 默认隐藏
        errorContainer.role = 'alert';
        // 将错误提示插入到表单按钮上方
        const submitBtn = form.querySelector('.btn-warning');
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * 密码验证核心函数
     * @returns {Boolean} 验证通过返回true，否则false
     */
    const validatePasswordForm = function() {
        let errorMessages = [];

        // 1. 验证原密码不能为空
        if (!oldPasswordInput.value.trim()) {
            errorMessages.push('请输入原密码');
        }

        // 2. 验证新密码不能为空
        if (!newPassword1Input.value.trim()) {
            errorMessages.push('请输入新密码');
        } else {
            // 3. 验证新密码长度（至少4位）
            if (newPassword1Input.value.length < 4) {
                errorMessages.push('新密码长度不能少于4位');
            }
            // 4. 验证新密码不能与原密码相同
            if (newPassword1Input.value === oldPasswordInput.value) {
                errorMessages.push('新密码不能与原密码相同');
            }
        }

        // 6. 验证确认密码不能为空
        if (!newPassword2Input.value.trim()) {
            errorMessages.push('请确认新密码');
        } else {
            // 7. 验证两次新密码一致
            if (newPassword2Input.value !== newPassword1Input.value) {
                errorMessages.push('两次输入的新密码不一致');
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

    // 为每个输入框添加失去焦点时的实时验证
    [oldPasswordInput, newPassword1Input, newPassword2Input].forEach(input => {
        if (input) { // 防止字段不存在的情况
            input.addEventListener('blur', validatePasswordForm);
            // 输入时实时清除对应错误（提升体验）
            input.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validatePasswordForm();
                }
            });
        }
    });

    // 表单提交时的最终验证
    form.addEventListener('submit', function(e) {
        if (!validatePasswordForm()) {
            e.preventDefault(); // 阻止表单提交
            // 滚动到错误提示位置（平滑滚动）
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});