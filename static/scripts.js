function startLoading(button) {
    const card = button.parentElement;
    const originalText = button.innerText;

    // Create a loading spinner
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    card.appendChild(spinner);

    // Disable the button
    button.disabled = true;
    button.innerText = 'Processing...';

    // Make a POST request to the /process endpoint
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        // Remove the spinner
        card.removeChild(spinner);

        // Re-enable the button and show success message
        button.disabled = false;
        button.innerText = originalText;

        const successMessage = document.createElement('p');
        successMessage.className = 'success-message';
        successMessage.innerText = data.message;
        card.appendChild(successMessage);

        // Remove the success message after 3 seconds
        setTimeout(() => {
            card.removeChild(successMessage);
        }, 3000);
    })
    .catch(error => {
        console.error('Error:', error);
        card.removeChild(spinner);
        button.disabled = false;
        button.innerText = originalText;
    });
}

function processYouTube() {
    const url = document.getElementById('youtube-url').value;
    const button = document.querySelector('#youtube-url').nextElementSibling;
    const card = button.parentElement;
    const originalText = button.innerText;

    if (!url) {
        alert('Please paste a YouTube URL.');
        return;
    }

    // Create a loading spinner
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    card.appendChild(spinner);

    // Disable the button
    button.disabled = true;
    button.innerText = 'Processing...';

    fetch('/process_youtube', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    })
        .then(response => response.json())
        .then(data => {
            // Remove the spinner
            card.removeChild(spinner);

            // Re-enable the button and show success message
            button.disabled = false;
            button.innerText = originalText;

            const successMessage = document.createElement('p');
            successMessage.className = 'success-message';
            successMessage.innerText = data.message || 'Processing complete!';
            card.appendChild(successMessage);

            // Remove the success message after 3 seconds
            setTimeout(() => {
                card.removeChild(successMessage);
            }, 3000);

            // Clear the input box
            document.getElementById('youtube-url').value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            card.removeChild(spinner);
            button.disabled = false;
            button.innerText = originalText;
        });
}
