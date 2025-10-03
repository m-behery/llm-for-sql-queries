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
        } else {
            // FIXED: Handle SQL and Answer independently - both can be present
            content += this.formatSuccessResponse(responseDetails);
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
        
        // Make sections collapsible
        this.makeSectionsCollapsible(messageDiv);
    }
    
    formatSuccessResponse(responseDetails) {
        let content = '';
        
        // FIXED: Handle both SQL and Answer independently
        const hasAnswer = responseDetails.Answer && responseDetails.Answer.trim();
        const hasSQL = responseDetails.SQL && responseDetails.SQL.trim();
        
        if (hasAnswer) {
            content += this.formatAnswer(responseDetails.Answer);
        }
        
        if (hasSQL) {
            content += this.formatSQL(responseDetails.SQL);
        }
        
        // If neither Answer nor SQL, show raw response
        if (!hasAnswer && !hasSQL) {
            content += this.formatUnknownResponse(responseDetails);
        }
        
        // Always show metadata
        content += this.formatResponseMetadata(responseDetails);
        
        return content;
    }
    
    formatErrorResponse(responseDetails) {
        return `
            <div class="response-section">
                <div class="section-header error-header">
                    ❌ Error
                </div>
                <div class="section-content">
                    <div style="color: #dc3545;">
                        <strong>Error:</strong> ${this.escapeHtml(responseDetails.error || 'Unknown error occurred')}
                    </div>
                    ${this.formatResponseMetadata(responseDetails)}
                </div>
            </div>
        `;
    }
    
    formatUnknownResponse(responseDetails) {
        return `
            <div class="response-section">
                <div class="section-header warning-header">
                    ⚠️ Response Data
                </div>
                <div class="section-content">
                    <div class="json-data">
                        <pre>${this.formatJson(responseDetails)}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatAnswer(answer) {
        let formattedAnswer;
        
        // Use marked.js if available, otherwise escape HTML
        if (typeof marked !== 'undefined') {
            formattedAnswer = marked.parse(answer);
        } else {
            formattedAnswer = `<div class="plain-text">${this.escapeHtml(answer)}</div>`;
            console.warn('Marked.js not loaded - using plain text formatting');
        }
        
        return `
            <div class="response-section">
                <div class="section-header answer-header">
                    📊 Answer
                </div>
                <div class="section-content">
                    <div class="markdown-content">${formattedAnswer}</div>
                </div>
            </div>
        `;
    }
    
    formatSQL(sql) {
        const escapedSQL = this.escapeHtml(sql);
        return `
            <div class="response-section">
                <div class="section-header sql-header">
                    🗃️ SQL Query
                </div>
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
                <div class="section-header metadata-header">
                    🔧 Response Details
                </div>
                <div class="section-content">
                    <div class="metadata-content">
                        <strong>Provider:</strong> <span class="metadata-value">${provider || 'N/A'}</span><br>
                        <strong>Model:</strong> <span class="metadata-value">${model || 'N/A'}</span><br>
                        <strong>Status:</strong> <span class="status ${status === 'ok' ? 'status-ok' : 'status-error'}">${status || 'unknown'}</span>
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
        const jsonString = JSON.stringify(obj, null, 2);
        return this.escapeHtml(jsonString);
    }
    
    applySyntaxHighlighting() {
        // Apply Prism.js highlighting to all code blocks
        if (window.Prism) {
            Prism.highlightAllUnder(this.chatMessages);
        }
    }
    
    makeSectionsCollapsible(messageDiv) {
        const headers = messageDiv.querySelectorAll('.section-header');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                const isCollapsed = content.style.display === 'none';
                content.style.display = isCollapsed ? 'block' : 'none';
                header.classList.toggle('collapsed', !isCollapsed);
            });
        });
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
        
        if (message.length > 2000) {
            alert('Message too long. Please keep under 2000 characters.');
            return;
        }
        
        this.addUserMessage(message);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.sendButton.disabled = true;
        this.updateCharCount();
        
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
                this.addBotResponse(responseData);
            } else {
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
});