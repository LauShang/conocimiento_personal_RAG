document.querySelector('.chat-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const question = e.target.value;
        const loadingIndicator = document.getElementById('loading-indicator');
        loadingIndicator.style.display = 'block';

        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';

                // Create a container div for the question and response
                const container = document.createElement('div');
                container.className = 'qa-container';

                // Add the question
                const questionElement = document.createElement('p');
                questionElement.className = 'question';
                questionElement.innerText = `Q: ${question}`;
                container.appendChild(questionElement);

                // Add the response
                const responseElement = document.createElement('p');
                responseElement.className = 'response';
                responseElement.innerText = `A: ${data.answer || data.error}`;
                container.appendChild(responseElement);

                // Append the container below the input box
                document.querySelector('.main').appendChild(container);

                // Clear the input box after the question is answered
                e.target.value = '';
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                console.error('Error:', error);
            });
    }
});
