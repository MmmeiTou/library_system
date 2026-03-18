document.addEventListener('DOMContentLoaded', function() {
    // Get the form and all password input fields (adapted for Django's form.as_p rendering structure)
    const form = document.getElementById('passwordChangeForm');
    const oldPasswordInput = form.querySelector('input[name="old_password"]');
    const newPassword1Input = form.querySelector('input[name="new_password1"]');
    const newPassword2Input = form.querySelector('input[name="new_password2"]');

    // Create a unified error message container (if it does not exist)
    let errorContainer = form.querySelector('.password-error-container');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'password-error-container alert alert-danger mt-3';
        errorContainer.style.display = 'none'; 
        errorContainer.role = 'alert';
        const submitBtn = form.querySelector('.btn-warning');
        submitBtn.parentNode.insertBefore(errorContainer, submitBtn);
    }

    /**
     * Core password validation function
     * @returns {Boolean} Returns true if validation passes, otherwise false
     */
    const validatePasswordForm = function() {
        let errorMessages = [];

        if (!oldPasswordInput.value.trim()) {
            errorMessages.push('Please enter your current password');
        }

        if (!newPassword1Input.value.trim()) {
            errorMessages.push('Please enter a new password');
        } else {
            if (newPassword1Input.value.length < 4) {
                errorMessages.push('New password must be at least 4 characters long');
            }
            
            if (newPassword1Input.value === oldPasswordInput.value) {
                errorMessages.push('New password cannot be the same as the current password');
            }
        }

        
        if (!newPassword2Input.value.trim()) {
            errorMessages.push('Please confirm your new password');
        } else {
            
            if (newPassword2Input.value !== newPassword1Input.value) {
                errorMessages.push('The two new passwords do not match');
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

    // Add real-time validation on blur for each input field
    [oldPasswordInput, newPassword1Input, newPassword2Input].forEach(input => {
        if (input) { 
            input.addEventListener('blur', validatePasswordForm);
            // Clear corresponding errors in real time when typing
            input.addEventListener('input', function() {
                if (errorContainer.style.display === 'block') {
                    validatePasswordForm();
                }
            });
        }
    });

    // Final validation on form submission
    form.addEventListener('submit', function(e) {
        if (!validatePasswordForm()) {
            e.preventDefault(); // Prevent form submission
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
});