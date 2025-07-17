document.addEventListener('DOMContentLoaded', () => {
    // Only run this logic on pages that have the 'data-secure' attribute
    if (document.body.dataset.secure !== 'true') {
        return;
    }

    const VIZ_TOKEN_KEY = 'viz_token_auth';
    const CORRECT_TOKEN = 'ntkttbmyhtltrd';

    // Check if the user is already authenticated in this session
    if (sessionStorage.getItem(VIZ_TOKEN_KEY) === CORRECT_TOKEN) {
        return; // Token is valid, do nothing and let the page load
    }

    // --- If not authenticated, create and show the password overlay ---

    // 1. Create the overlay elements
    const overlay = document.createElement('div');
    overlay.id = 'security-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
    overlay.style.zIndex = '9999';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';

    const promptBox = document.createElement('div');
    promptBox.style.fontFamily = 'Arial, sans-serif';
    promptBox.style.textAlign = 'center';
    promptBox.style.padding = '40px';
    promptBox.style.border = '1px solid #ccc';
    promptBox.style.borderRadius = '8px';
    promptBox.style.backgroundColor = 'white';
    promptBox.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';

    const title = document.createElement('h2');
    title.textContent = 'Authentication Required';
    title.style.marginBottom = '20px';

    const instruction = document.createElement('p');
    instruction.textContent = 'Please enter the access token to view this content.';
    instruction.style.marginBottom = '25px';

    const tokenInput = document.createElement('input');
    tokenInput.type = 'password';
    tokenInput.id = 'token-input';
    tokenInput.style.padding = '10px';
    tokenInput.style.width = '250px';
    tokenInput.style.border = '1px solid #ccc';
    tokenInput.style.borderRadius = '4px';

    const submitButton = document.createElement('button');
    submitButton.textContent = 'Submit';
    submitButton.style.padding = '10px 20px';
    submitButton.style.marginLeft = '10px';
    submitButton.style.border = 'none';
    submitButton.style.borderRadius = '4px';
    submitButton.style.backgroundColor = '#007bff';
    submitButton.style.color = 'white';
    submitButton.style.cursor = 'pointer';

    const errorMessage = document.createElement('p');
    errorMessage.style.color = 'red';
    errorMessage.style.marginTop = '15px';
    errorMessage.style.display = 'none';
    errorMessage.textContent = 'Invalid token. Please try again.';

    // 2. Assemble the prompt box
    promptBox.appendChild(title);
    promptBox.appendChild(instruction);
    promptBox.appendChild(tokenInput);
    promptBox.appendChild(submitButton);
    promptBox.appendChild(errorMessage);
    overlay.appendChild(promptBox);

    // 3. Add the overlay to the page
    document.body.appendChild(overlay);
    tokenInput.focus();

    // 4. Create the validation function
    const validateToken = () => {
        if (tokenInput.value === CORRECT_TOKEN) {
            sessionStorage.setItem(VIZ_TOKEN_KEY, tokenInput.value);
            overlay.remove();
        } else {
            errorMessage.style.display = 'block';
            tokenInput.value = '';
            tokenInput.focus();
        }
    };

    // 5. Add event listeners
    submitButton.addEventListener('click', validateToken);
    tokenInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            validateToken();
        }
    });
});