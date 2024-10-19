document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('register-btn');
    const loginCodeDisplay = document.getElementById('login-code-display');
    const copyBtn = document.getElementById('copy-btn');
    const confirmCheckbox = document.getElementById('confirm-checkbox');
    const loginBtn = document.getElementById('login-btn');
    const loginForm = document.getElementById('login-form');

    if (registerBtn) {
        registerBtn.addEventListener('click', async function() {
            const response = await fetch('/register', { method: 'POST' });
            const data = await response.json();
            loginCodeDisplay.textContent = data.login_code;
            loginCodeDisplay.style.display = 'block';
            copyBtn.style.display = 'inline-block';
            confirmCheckbox.style.display = 'block';
        });
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const loginCode = loginCodeDisplay.textContent;
            navigator.clipboard.writeText(loginCode).then(function() {
                alert('Login code copied to clipboard!');
            });
        });
    }

    if (confirmCheckbox) {
        confirmCheckbox.addEventListener('change', function() {
            loginBtn.disabled = !this.checked;
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const loginCode = document.getElementById('login-code').value;
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `login_code=${encodeURIComponent(loginCode)}`,
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alert(data.error);
            }
        });
    }
});
