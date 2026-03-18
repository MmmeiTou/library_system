document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const formFields = {
        username: form.querySelector('input[name="username"]'),      
        email: form.querySelector('input[name="email"]'),            
        librarian_id: form.querySelector('input[name="librarian_id"]'), 
        password1: form.querySelector('input[name="password1"]'),    
        password2: form.querySelector('input[name="password2"]')     
    };

    // Create a unified error message container
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
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * Core validation function for librarian registration form
     * @returns {Boolean} Returns true if validation passes, otherwise false
     */
    const validateLibrarianForm = function() {
        const errors = [];

        if (formFields.username) {
            const usernameVal = formFields.username.value.trim();
            if (!usernameVal) {
                errors.push('❌ Administrator account cannot be empty');
            } 
        }

        if (formFields.email && formFields.email.value.trim()) {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(formFields.email.value)) {
                errors.push('❌ Please enter a valid email address');
            }
        }

        if (formFields.librarian_id) {
            const idVal = formFields.librarian_id.value.trim();
            if (!idVal) {
                errors.push('❌ Librarian ID cannot be empty');
            } 
        }

        if (formFields.password1) {
            const pwdVal = formFields.password1.value.trim();
            if (!pwdVal) {
                errors.push('❌ Password cannot be empty');
            } else if (pwdVal.length < 4) {
                errors.push('❌ Password must be at least 4 characters long');
            } 
        }

        if (formFields.password2) {
            const pwd2Val = formFields.password2.value.trim();
            if (!pwd2Val) {
                errors.push('❌ Please confirm your password');
            } else if (formFields.password1 && pwd2Val !== formFields.password1.value) {
                errors.push('❌ The two passwords do not match');
            }
        }

        // Render error messages / clear messages
        if (errors.length > 0) {
            errorContainer.innerHTML = errors.join('<br>');
            errorContainer.style.display = 'block';
            return false;
        } else {
            errorContainer.style.display = 'none';
            return true;
        }
    };

    // Add real-time validation on blur for all input fields
    Object.values(formFields).forEach(field => {
        if (field) {
            field.addEventListener('blur', validateLibrarianForm);
            // Update validation status in real time while typing
            field.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validateLibrarianForm();
                }
            });
        }
    });

    // Final validation on form submission
    form.addEventListener('submit', function(e) {
        if (!validateLibrarianForm()) {
            e.preventDefault(); // Prevent form submission
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
});