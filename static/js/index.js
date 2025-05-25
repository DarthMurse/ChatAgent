// Global variables
let currentSessionId = null;
let isLoading = false;

// DOM loaded event
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadApiKeys();
    loadChatSessions();

    // Event listeners for form elements
    document.getElementById('provider-select').addEventListener('change', handleProviderSelect);
    document.getElementById('model-select').addEventListener('change', handleModelSelect);
});

// API Key Management
async function loadApiKeys() {
    try {
        const response = await fetch('/api/keys');
        const providers = await response.json();
        
        updateConfiguredProviders(providers);
        updateModelSelector(providers);
    } catch (error) {
        console.error('Error loading API keys:', error);
    }
}

async function saveApiKey() {
    const provider = document.getElementById('provider-select').value;
    const apiKey = document.getElementById('api-key-input').value;
    const modelsText = document.getElementById('models-input').value;
    
    if (!provider || !apiKey) {
        alert('Please select a provider and enter an API key');
        return;
    }
    
    const models = modelsText.split(',').map(m => m.trim()).filter(m => m);
    
    try {
        const response = await fetch('/api/keys', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider, api_key: apiKey, models})
        });
        
        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('provider-select').value = '';
            document.getElementById('api-key-input').value = '';
            document.getElementById('models-input').value = '';
            loadApiKeys();
        } else {
            alert(result.error);
        }
    } catch (error) {
        alert('Error saving API key: ' + error.message);
    }
}

async function deleteApiKey(provider) {
    if (confirm(`Delete API key for ${provider}?`)) {
        try {
            await fetch(`/api/keys?provider=${provider}`, {method: 'DELETE'});
            loadApiKeys();
        } catch (error) {
            alert('Error deleting API key: ' + error.message);
        }
    }
}

function updateConfiguredProviders(providers) {
    const list = document.getElementById('configured-providers-list');
    list.innerHTML = '';
    
    for (const [provider, info] of Object.entries(providers)) {
        const item = document.createElement('div');
        item.className = 'provider-item';
        item.innerHTML = `
            <span>${provider} (${info.models.length} models)</span>
            <button class="delete-btn" onclick="deleteApiKey('${provider}')">×</button>
        `;
        list.appendChild(item);
    }
}

function updateModelSelector(providers) {
    const select = document.getElementById('model-select');
    select.innerHTML = '<option value="">Select Model</option>';
    
    for (const [provider, info] of Object.entries(providers)) {
        for (const model of info.models) {
            const option = document.createElement('option');
            option.value = `${provider}:${model}`;
            option.textContent = `${provider}/${model}`;
            select.appendChild(option);
        }
    }
    
    // Enable/disable input based on model selection
    const hasModels = select.options.length > 1;
    document.getElementById('message-input').disabled = !hasModels || !currentSessionId;
    document.getElementById('send-btn').disabled = !hasModels || !currentSessionId;
}

// Chat Session Management
async function loadChatSessions() {
    try {
        const response = await fetch('/api/chat/sessions');
        const sessions = await response.json();
        
        const list = document.getElementById('chat-sessions-list');
        list.innerHTML = '';
        
        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = 'chat-session';
            if (session.id === currentSessionId) {
                item.classList.add('active');
            }
            item.innerHTML = `
                <div style="font-weight: 500;">${session.title}</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 11px; color: #a0aec0;">${session.message_count} messages</div>
                    <button class="delete-btn" onclick="deleteSession('${session.id}'); event.stopPropagation();">×</button>
                </div>
            `;
            item.onclick = () => loadChatSession(session.id);
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading chat sessions:', error);
    }
}

async function newChat() {
    try {
        const response = await fetch('/api/chat/new', {method: 'POST'});
        const result = await response.json();
        
        currentSessionId = result.session_id;
        document.getElementById('chat-title').textContent = 'New Chat';
        document.getElementById('chat-container').innerHTML = '';
        
        // Enable input if model is selected
        const modelSelect = document.getElementById('model-select');
        const hasModel = modelSelect.value !== '';
        document.getElementById('message-input').disabled = !hasModel;
        document.getElementById('send-btn').disabled = !hasModel;
        
        loadChatSessions();
    } catch (error) {
        alert('Error creating new chat: ' + error.message);
    }
}

async function loadChatSession(sessionId) {
    try {
        currentSessionId = sessionId;
        
        const response = await fetch(`/api/chat/${sessionId}/messages`);
        const messages = await response.json();
        
        displayMessages(messages);
        loadChatSessions(); // Refresh to update active state
        
        // Enable input if model is selected
        const modelSelect = document.getElementById('model-select');
        const hasModel = modelSelect.value !== '';
        document.getElementById('message-input').disabled = !hasModel;
        document.getElementById('send-btn').disabled = !hasModel;
        
    } catch (error) {
        console.error('Error loading chat session:', error);
    }
}

async function deleteSession(sessionId) {
    if (confirm('Delete this chat session?')) {
        try {
            const response = await fetch(`/api/chat/${sessionId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // If the deleted session was the current one, clear the content
                if (sessionId === currentSessionId) {
                    currentSessionId = null;
                    document.getElementById('chat-title').textContent = 'Chat Agent';
                    document.getElementById('chat-container').innerHTML = `
                        <div class="welcome">
                            <h2>Welcome to Chat Agent</h2>
                            <p>Configure your API keys and start a new chat to begin.</p>
                        </div>
                    `;
                    // Disable input
                    document.getElementById('message-input').disabled = true;
                    document.getElementById('send-btn').disabled = true;
                }
                
                // Refresh sessions list
                loadChatSessions();
            } else {
                alert('Error deleting chat session');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting chat session');
        }
    }
}

// Message Processing
function renderMarkdown(content) {
    // Define a custom renderer to preserve LaTeX formulas
    const renderer = new marked.Renderer();
    const originalCode = renderer.code;
    
    // Special handling for code blocks (don't process LaTeX in code blocks)
    renderer.code = function(code, language) {
        return originalCode.call(this, code, language);
    };
    
    // Configure marked options
    marked.setOptions({
        renderer: renderer,
        breaks: true,
        gfm: true,
        highlight: function(code, lang) {
            if (lang && Prism.languages[lang]) {
                return Prism.highlight(code, Prism.languages[lang], lang);
            }
            return code;
        }
    });
    
    // Process markdown while preserving LaTeX delimiters
    return marked.parse(content);
}

function renderMathAndHighlight(element) {
    // Trigger syntax highlighting
    if (window.Prism) {
        Prism.highlightAllUnder(element);
    }
    
    // Safely render LaTeX
    if (window.MathJax) {
        if (window.MathJax.typesetPromise) {
            try {
                window.MathJax.typesetPromise([element])
                    .then(() => {
                        console.log('MathJax rendering complete');
                    })
                    .catch(err => {
                        console.warn('MathJax error:', err);
                    });
            } catch (error) {
                console.error('Error rendering LaTeX:', error);
            }
        } else if (window.MathJax.typeset) {
            try {
                window.MathJax.typeset([element]);
            } catch (error) {
                console.error('Error rendering LaTeX:', error);
            }
        } else {
            console.warn('MathJax typesetting function not available');
        }
    } else {
        console.warn('MathJax not loaded yet');
    }
}

function displayMessages(messages) {
    const container = document.getElementById('chat-container');
    container.innerHTML = '';
    
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (message.role === 'assistant') {
            // Render markdown for assistant messages
            contentDiv.innerHTML = renderMarkdown(message.content);
            // Render math and syntax highlighting
            renderMathAndHighlight(contentDiv);
        } else {
            contentDiv.textContent = message.content;
        }
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'message-info';
        const time = new Date(message.timestamp).toLocaleTimeString();
        infoDiv.textContent = message.role === 'assistant' ? 
            `${time} • ${message.model || 'AI'}` : time;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(infoDiv);
        container.appendChild(messageDiv);
    });
    
    container.scrollTop = container.scrollHeight;
}

// Message sending
async function sendMessage(event) {
    event.preventDefault();
    
    if (isLoading || !currentSessionId) return;
    
    const messageInput = document.getElementById('message-input');
    const modelSelect = document.getElementById('model-select');
    const message = messageInput.value.trim();
    const modelValue = modelSelect.value;
    
    if (!message || !modelValue) return;
    
    const [provider, model] = modelValue.split(':');
    
    // Clear input and disable form
    messageInput.value = '';
    isLoading = true;
    document.getElementById('send-btn').disabled = true;
    messageInput.disabled = true;
    
    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Generating response...';
    document.getElementById('chat-container').appendChild(loadingDiv);
    document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
    
    try {
        // Add user message to UI
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user';
        userMessageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-info">${new Date().toLocaleTimeString()}</div>
        `;
        document.getElementById('chat-container').appendChild(userMessageDiv);
        
        // Remove loading indicator
        loadingDiv.remove();
        
        // Send to server - using regular endpoint instead of streaming
        const response = await fetch(`/api/chat/${currentSessionId}/messages`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message,
                model_provider: provider,
                model_name: model
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const assistantMessage = await response.json();
        
        // Display assistant message
        const assistantMessageDiv = document.createElement('div');
        assistantMessageDiv.className = 'message assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = renderMarkdown(assistantMessage.content);
        
        // Render LaTeX and syntax highlighting
        renderMathAndHighlight(contentDiv);
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'message-info';
        const time = new Date(assistantMessage.timestamp).toLocaleTimeString();
        infoDiv.textContent = `${time} • ${assistantMessage.model || 'AI'}`;
        
        assistantMessageDiv.appendChild(contentDiv);
        assistantMessageDiv.appendChild(infoDiv);
        document.getElementById('chat-container').appendChild(assistantMessageDiv);
        
        // Update chat title if needed
        const titleElement = document.getElementById('chat-title');
        if (titleElement.textContent === 'New Chat') {
            titleElement.textContent = message.substring(0, 50) + (message.length > 50 ? '...' : '');
        }
        
        loadChatSessions(); // Refresh sessions list
        
    } catch (error) {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = 'Error: ' + error.message;
        document.getElementById('chat-container').appendChild(errorDiv);
        loadingDiv.remove();
    } finally {
        // Re-enable form
        isLoading = false;
        messageInput.disabled = false;
        document.getElementById('send-btn').disabled = false;
        messageInput.focus();
        
        document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
    }
}

// Event handlers
function handleProviderSelect() {
    const provider = this.value;
    const examplesDiv = document.getElementById('model-examples');
    
    const examples = {
        'openai': 'Examples: gpt-4, gpt-3.5-turbo, gpt-4-turbo',
        'claude': 'Examples: claude-3-5-sonnet-20241022, claude-3-haiku-20240307, claude-3-opus-20240229',
        'deepseek': 'Examples: deepseek-chat, deepseek-coder'
    };
    
    if (provider && examples[provider]) {
        examplesDiv.textContent = examples[provider];
        examplesDiv.style.display = 'block';
    } else {
        examplesDiv.style.display = 'none';
    }
}

function handleModelSelect() {
    const hasModel = this.value !== '';
    document.getElementById('message-input').disabled = !hasModel || !currentSessionId;
    document.getElementById('send-btn').disabled = !hasModel || !currentSessionId;
}