document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('register-btn');
    const loginCodeDisplay = document.getElementById('login-code-display');
    const copyBtn = document.getElementById('copy-btn');
    const confirmCheckbox = document.getElementById('confirm-checkbox');
    const loginBtn = document.getElementById('login-btn');
    const loginForm = document.getElementById('login-form');
    const completeRegistrationBtn = document.getElementById('complete-registration');
    const registrationInfo = document.getElementById('registration-info');
    const errorMessage = document.getElementById('error-message');

    if (registerBtn) {
        registerBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/register', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                loginCodeDisplay.textContent = data.login_code;
                registrationInfo.style.display = 'block';
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to generate login code. Please try again.');
            }
        });
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const loginCode = loginCodeDisplay.textContent;
            navigator.clipboard.writeText(loginCode).then(function() {
                alert('Login code copied to clipboard!');
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                alert('Failed to copy login code. Please try again.');
            });
        });
    }

    if (confirmCheckbox) {
        confirmCheckbox.addEventListener('change', function() {
            completeRegistrationBtn.disabled = !this.checked;
        });
    }

    if (completeRegistrationBtn) {
        completeRegistrationBtn.addEventListener('click', function() {
            registrationInfo.style.display = 'none';
            loginForm.style.display = 'block';
            document.getElementById('login-code').value = loginCodeDisplay.textContent;
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const loginCode = document.getElementById('login-code').value;
            
            if (!/^\d{8}$/.test(loginCode)) {
                showError('Please enter a valid 8-digit login code.');
                return;
            }

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `login_code=${encodeURIComponent(loginCode)}`,
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    showError(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to log in. Please try again.');
            }
        });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
});
