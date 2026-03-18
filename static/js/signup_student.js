document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const fieldSelectors = {
        username: form.querySelector('input[name="username"]'), 
        email: form.querySelector('input[name="email"]'),       
        student_id: form.querySelector('input[name="student_id"]'), 
        password1: form.querySelector('input[name="password1"]'),   
        password2: form.querySelector('input[name="password2"]')    
    };

    // Create a unified error message container
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
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * Core form validation function
     * @returns {Boolean} Returns true if validation passes, otherwise false
     */
    const validateSignupForm = function() {
        let errorMessages = [];

        if (fieldSelectors.username) {
            if (!fieldSelectors.username.value.trim()) {
                errorMessages.push('✖ Username cannot be empty');
            } 
        }

        if (fieldSelectors.email && fieldSelectors.email.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(fieldSelectors.email.value)) {
                errorMessages.push('✖ Please enter a valid email address');
            }
        }

        if (fieldSelectors.student_id) {
            if (!fieldSelectors.student_id.value.trim()) {
                errorMessages.push('✖ Student ID cannot be empty');
            } 
        }

        if (fieldSelectors.password1) {
            if (!fieldSelectors.password1.value.trim()) {
                errorMessages.push('✖ Password cannot be empty');
            } else {
                if (fieldSelectors.password1.value.length < 4) {
                    errorMessages.push('✖ Password must be at least 4 characters long');
                }
                
            }
        }

        if (fieldSelectors.password2) {
            if (!fieldSelectors.password2.value.trim()) {
                errorMessages.push('✖ Please confirm your password');
            } else if (fieldSelectors.password1 && fieldSelectors.password1.value !== fieldSelectors.password2.value) {
                errorMessages.push('✖ The two passwords do not match');
            }
        }

        // Show/hide error messages
        if (errorMessages.length > 0) {
            errorContainer.innerHTML = errorMessages.join('<br>');
            errorContainer.style.display = 'block';
            return false;
        } else {
            errorContainer.style.display = 'none';
            return true;
        }
    };

    // Add real-time validation for all input fields
    Object.values(fieldSelectors).forEach(input => {
        if (input) {
            input.addEventListener('blur', validateSignupForm);
            // Update validation status in real time while typing
            input.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validateSignupForm();
                }
            });
        }
    });

    // Final validation on form submission
    form.addEventListener('submit', function(e) {
        if (!validateSignupForm()) {
            e.preventDefault(); // Prevent form submission
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});