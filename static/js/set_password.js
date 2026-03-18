// 等待DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取表单元素
    const form = document.querySelector('form');
    const password1 = document.querySelector('input[name="new_password1"]');
    const password2 = document.querySelector('input[name="new_password2"]');
    
    // 自定义错误提示元素（如果不存在则创建）
    let errorElement = document.querySelector('.validation-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'validation-error';
        errorElement.style.color = 'red';
        errorElement.style.margin = '10px 0';
        errorElement.style.fontSize = '14px';
        // 将错误提示插入到提交按钮上方
        const submitBtn = document.querySelector('.btn-confirm');
        submitBtn.parentNode.insertBefore(errorElement, submitBtn);
    }

    // 密码验证规则
    const validatePassword = function() {
        let errorMsg = '';
        
        // 1. 检查密码长度
        if (password1.value.length < 4) {
            errorMsg = '密码长度不能少于4位';
        }
        
        // 2. 检查两次密码是否一致
        else if (password1.value !== password2.value) {
            errorMsg = '两次输入的密码不一致';
        }
        
        // 显示错误信息或清空
        errorElement.textContent = errorMsg;
        return errorMsg === ''; // 验证通过返回true，否则false
    };

    // 实时验证：输入框失去焦点时触发
    password1.addEventListener('blur', validatePassword);
    password2.addEventListener('blur', validatePassword);

    // 表单提交时的验证
    form.addEventListener('submit', function(e) {
        // 如果验证不通过，阻止表单提交
        if (!validatePassword()) {
            e.preventDefault(); // 阻止表单提交
            // 滚动到错误提示位置，提升用户体验
            errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    // 可选：输入时实时清除错误提示（提升体验）
    password1.addEventListener('input', function() {
        if (errorElement.textContent) {
            validatePassword(); // 实时更新验证状态
        }
    });
    password2.addEventListener('input', function() {
        if (errorElement.textContent) {
            validatePassword(); // 实时更新验证状态
        }
    });
});