document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const password1 = document.querySelector('input[name="new_password1"]');
    const password2 = document.querySelector('input[name="new_password2"]');
    
    // Custom error message element (create if it does not exist)
    let errorElement = document.querySelector('.validation-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'validation-error';
        errorElement.style.color = 'red';
        errorElement.style.margin = '10px 0';
        errorElement.style.fontSize = '14px';
        const submitBtn = document.querySelector('.btn-confirm');
        submitBtn.parentNode.insertBefore(errorElement, submitBtn);
    }

    // Password validation rules
    const validatePassword = function() {
        let errorMsg = '';
        
        if (password1.value.length < 4) {
            errorMsg = 'Password must be at least 4 characters long';
        }
        
        else if (password1.value !== password2.value) {
            errorMsg = 'The two passwords do not match';
        }
        
        // Display error message or clear it
        errorElement.textContent = errorMsg;
        return errorMsg === ''; 
    };

    // Real-time validation: trigger on input blur
    password1.addEventListener('blur', validatePassword);
    password2.addEventListener('blur', validatePassword);

    // Validation on form submission
    form.addEventListener('submit', function(e) {
        if (!validatePassword()) {
            e.preventDefault(); // Prevent form submission
            errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    // Clear error message in real time when typing
    password1.addEventListener('input', function() {
        if (errorElement.textContent) {
            validatePassword(); 
        }
    });
    password2.addEventListener('input', function() {
        if (errorElement.textContent) {
            validatePassword(); 
        }
    });
});