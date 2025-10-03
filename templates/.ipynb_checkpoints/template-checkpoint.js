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
    
    addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${isUser ? '<strong>You:</strong> ' : '<strong>AI Assistant:</strong> '}
                ${this.escapeHtml(content)}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
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
        this.addMessage(message, true);
        
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
            
            const data = await response.json();
            this.hideTypingIndicator();
            
            if (response.ok) {
                // Extract response from different possible fields
                let botResponse = 'I apologize, but I encountered an issue processing your request.';
                
                if (data.response) {
                    botResponse = data.response;
                } else if (data.answer) {
                    botResponse = data.answer;
                } else if (data.SQL) {
                    botResponse = `SQL Query: ${data.SQL}`;
                } else if (data.error) {
                    botResponse = `Error: ${data.error}`;
                } else if (typeof data === 'string') {
                    botResponse = data;
                }
                
                this.addMessage(botResponse, false);
            } else {
                this.addMessage(`Error: ${data.error || 'Unknown server error'}`, false);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage(`Network error: ${error.message}`, false);
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
