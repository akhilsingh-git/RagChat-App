document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const loadingIndicator = document.getElementById('loading');

    // This function remains the same
    const appendMessage = (text, sender, elementId = null) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('flex', 'flex-col', sender === 'user' ? 'items-end' : 'items-start');
        
        const messageElement = document.createElement('div');
        if (elementId) {
            messageElement.id = elementId;
        }
        messageElement.classList.add('p-3', 'rounded-lg', 'max-w-lg');
        
        if (sender === 'user') {
            messageElement.classList.add('bg-slate-700', 'text-white');
        } else {
            messageElement.classList.add('bg-sky-100', 'text-sky-800');
        }
        
        messageElement.innerText = text;
        messageWrapper.appendChild(messageElement);
        chatContainer.appendChild(messageWrapper);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return messageElement;
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        userInput.value = '';
        loadingIndicator.classList.remove('hidden');
        chatForm.querySelector('button').disabled = true;

        // Create an empty message bubble for the bot's response
        const botMessageElement = appendMessage("", 'bot', 'bot-response-streaming');
        botMessageElement.innerHTML = '<span class="blinking-cursor"></span>'; // Add a cursor effect

        // Use EventSource to connect to the streaming endpoint
        const eventSource = new EventSource(`/api/query?query=${encodeURIComponent(query)}&k=3`);
        
        let fullResponse = "";

        eventSource.onmessage = function(event) {
            // Remove the cursor before appending new text
            const cursor = botMessageElement.querySelector('.blinking-cursor');
            if (cursor) {
                cursor.remove();
            }

            const token = event.data;
            fullResponse += token;
            botMessageElement.innerText = fullResponse; // Update the text
            botMessageElement.innerHTML += '<span class="blinking-cursor"></span>'; // Re-add cursor
            chatContainer.scrollTop = chatContainer.scrollHeight;
        };

        eventSource.onerror = function(err) {
            console.error("EventSource failed:", err);
            // Remove the cursor when the stream is done or fails
            const cursor = botMessageElement.querySelector('.blinking-cursor');
            if (cursor) {
                cursor.remove();
            }
            eventSource.close();
            loadingIndicator.classList.add('hidden');
            chatForm.querySelector('button').disabled = false;
            userInput.focus();
        };
    });
});
