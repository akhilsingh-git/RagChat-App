document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const statusIndicator = document.getElementById('status-indicator'); // New element

    const appendMessage = (text, sender, elementId = null) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('flex', 'flex-col', sender === 'user' ? 'items-end' : 'items-start');
        
        const messageElement = document.createElement('div');
        if (elementId) messageElement.id = elementId;
        messageElement.classList.add('p-3', 'rounded-lg', 'max-w-lg', 'text-left');
        
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
        statusIndicator.classList.remove('hidden');
        chatForm.querySelector('button').disabled = true;

        const botMessageElement = appendMessage("", 'bot', 'bot-response-streaming');
        botMessageElement.innerHTML = '<span class="blinking-cursor"></span>';

        const eventSource = new EventSource(`/api/query?query=${encodeURIComponent(query)}`);
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);

                // Handle status updates
                if (data.status) {
                    statusIndicator.textContent = data.status;
                }

                // Handle token stream
                if (data.token) {
                    const cursor = botMessageElement.querySelector('.blinking-cursor');
                    if (cursor) cursor.remove();
                    botMessageElement.innerText += data.token;
                    botMessageElement.innerHTML += '<span class="blinking-cursor"></span>';
                }
                
                // Handle completion
                if (data.done) {
                    const cursor = botMessageElement.querySelector('.blinking-cursor');
                    if (cursor) cursor.remove();
                    statusIndicator.classList.add('hidden');
                    chatForm.querySelector('button').disabled = false;
                    userInput.focus();
                    eventSource.close();
                }

                // Handle errors
                if (data.error) {
                    botMessageElement.innerText = `Error: ${data.error}`;
                    botMessageElement.classList.remove('bg-sky-100', 'text-sky-800');
                    botMessageElement.classList.add('bg-red-100', 'text-red-800');
                }

            } catch (error) {
                console.error("Failed to parse stream data:", event.data, error);
            }
        };

        eventSource.onerror = function(err) {
            console.error("EventSource failed:", err);
            statusIndicator.textContent = 'Connection error.';
            setTimeout(() => statusIndicator.classList.add('hidden'), 3000);
            chatForm.querySelector('button').disabled = false;
            userInput.focus();
            eventSource.close();
        };
    });
});
