class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.charCount = document.getElementById('charCount');
        this.status = document.getElementById('status');
        
        this.initEventListeners();
        this.messageInput.focus();
    }
    
    initEventListeners() {
        // Enter to send, Shift+Enter for new line
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.autoResizeTextarea();
        });
        
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count} characters`;
        
        // Change color if approaching limit
        if (count > 1900) {
            this.charCount.style.color = count > 2000 ? '#dc3545' : '#ffc107';
        } else {
            this.charCount.style.color = '#6c757d';
        }
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>You:</strong> ${this.escapeHtml(message)}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotResponse(responseDetails) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        let content = '<strong>AI Assistant:</strong><br>';
        
        // Handle different response scenarios
        if (responseDetails.status === 'error') {
            content += this.formatErrorResponse(responseDetails);
        } else if (responseDetails.Answer || responseDetails.SQL) {
            content += this.formatSuccessResponse(responseDetails);
        } else {
            content += this.formatUnknownResponse(responseDetails);
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Apply syntax highlighting
        this.applySyntaxHighlighting();
    }
    
    formatSuccessResponse(responseDetails) {
        let content = '';
        
        // Format Answer (Natural Language Response)
        if (responseDetails.Answer) {
            content += this.formatAnswer(responseDetails.Answer);
        }
        
        // Format SQL Query
        if (responseDetails.SQL) {
            content += this.formatSQL(responseDetails.SQL);
        }
        
        // Format Metadata
        content += this.formatResponseMetadata(responseDetails);
        
        return content;
    }
    
    formatErrorResponse(responseDetails) {
        return `
            <div class="response-section">
                <div class="section-header" style="background: #f8d7da; color: #721c24;">❌ Error</div>
                <div class="section-content">
                    <div style="color: #dc3545;">
                        <strong>Error:</strong> ${responseDetails.error || 'Unknown error occurred'}
                    </div>
                    ${this.formatResponseMetadata(responseDetails)}
                </div>
            </div>
        `;
    }
    
    formatUnknownResponse(responseDetails) {
        return `
            <div class="response-section">
                <div class="section-header">⚠️ Unknown Response Format</div>
                <div class="section-content">
                    <div class="json-data">
                        ${this.formatJson(responseDetails)}
                    </div>
                    ${this.formatResponseMetadata(responseDetails)}
                </div>
            </div>
        `;
    }
    
    formatAnswer(answer) {
        // Convert markdown to HTML
        const formattedAnswer = marked.parse(answer);
        return `
            <div class="response-section">
                <div class="section-header">📊 Answer</div>
                <div class="section-content">
                    <div class="markdown-content">${formattedAnswer}</div>
                </div>
            </div>
        `;
    }
    
    formatSQL(sql) {
        // Format SQL with proper code blocks
        const escapedSQL = this.escapeHtml(sql);
        return `
            <div class="response-section">
                <div class="section-header">🗃️ SQL Query</div>
                <div class="section-content">
                    <div class="sql-code-block">
                        <pre><code class="language-sql">${escapedSQL}</code></pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatResponseMetadata(responseDetails) {
        const { token_usage, provider, model, status } = responseDetails;
        
        return `
            <div class="response-section">
                <div class="section-header">🔧 Response Details</div>
                <div class="section-content">
                    <div class="json-data">
                        <strong>Provider:</strong> <span class="json-string">${provider || 'N/A'}</span><br>
                        <strong>Model:</strong> <span class="json-string">${model || 'N/A'}</span><br>
                        <strong>Status:</strong> <span class="${status === 'ok' ? 'status-ok' : 'status-error'}">${status || 'unknown'}</span>
                        ${token_usage ? this.formatTokenUsage(token_usage) : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    formatTokenUsage(token_usage) {
        return `
            <div class="token-usage">
                <div class="token-item">
                    <div class="token-value">${token_usage.prompt_tokens || 0}</div>
                    <div class="token-label">Prompt</div>
                </div>
                <div class="token-item">
                    <div class="token-value">${token_usage.completion_tokens || 0}</div>
                    <div class="token-label">Completion</div>
                </div>
                <div class="token-item">
                    <div class="token-value">${token_usage.total_tokens || 0}</div>
                    <div class="token-label">Total</div>
                </div>
            </div>
        `;
    }
    
    formatJson(obj) {
        return JSON.stringify(obj, null, 2)
            .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, 
            function (match) {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
    }
    
    applySyntaxHighlighting() {
        // Apply Prism.js highlighting to all code blocks
        if (window.Prism) {
            Prism.highlightAllUnder(this.chatMessages);
        }
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-content typing-indicator">
                <strong>AI Assistant:</strong> Thinking
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            this.messageInput.focus();
            return;
        }
        
        // Prevent empty messages and very long messages
        if (message.length > 2000) {
            alert('Message too long. Please keep under 2000 characters.');
            return;
        }
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input and disable UI
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.sendButton.disabled = true;
        this.updateCharCount();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const responseData = await response.json();
            this.hideTypingIndicator();
            
            if (response.ok) {
                // EXPECTED RESPONSE FORMAT:
                // {
                //     "SQL": "<SQL Query>",
                //     "Answer": "<Natural Language Response>",
                //     "token_usage": { ... },
                //     "provider": "openai",
                //     "model": "gpt-3.5-turbo",
                //     "status": "ok"
                // }
                this.addBotResponse(responseData);
            } else {
                // Handle HTTP errors
                this.addBotResponse({
                    status: 'error',
                    error: responseData.error || `HTTP ${response.status}: ${response.statusText}`,
                    provider: 'server',
                    model: 'N/A'
                });
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addBotResponse({
                status: 'error',
                error: `Network error: ${error.message}`,
                provider: 'client',
                model: 'N/A'
            });
            console.error('Chat error:', error);
        } finally {
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    
    // Add collapsible section functionality
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('section-header')) {
            const content = e.target.nextElementSibling;
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
            e.target.classList.toggle('collapsed');
        }
    });
});