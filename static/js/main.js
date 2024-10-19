document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

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
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ login_code: loginCode }),
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
