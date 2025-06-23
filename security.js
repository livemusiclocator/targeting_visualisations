document.addEventListener('DOMContentLoaded', () => {
    const isSecurePage = document.body.dataset.secure === 'true';
    if (!isSecurePage) {
        return; // Do nothing if the page is not marked as secure
    }

    const VIZ_TOKEN_KEY = 'viz_token_auth';
    const CORRECT_TOKEN = 'ntkttbmyhtltrd';

    function isTokenValid() {
        return sessionStorage.getItem(VIZ_TOKEN_KEY) === CORRECT_TOKEN;
    }

    function requestToken() {
        const enteredToken = prompt('Please enter your access token to view this page:', '');
        if (enteredToken === CORRECT_TOKEN) {
            sessionStorage.setItem(VIZ_TOKEN_KEY, enteredToken);
            document.body.style.display = 'block'; // Show the content
        } else {
            document.body.innerHTML = `
                <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>Access Denied</h1>
                    <p>Invalid token. Please refresh the page and try again.</p>
                </div>
            `;
            document.body.style.display = 'block';
        }
    }

    // Hide content by default on secure pages
    document.body.style.display = 'none';

    if (isTokenValid()) {
        document.body.style.display = 'block'; // Show content if already authenticated
    } else {
        requestToken(); // Otherwise, ask for the token
    }
});