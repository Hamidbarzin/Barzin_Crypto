// Vercel-compatible Real-time Dashboard with Server-Sent Events
class VercelRealtimeDashboard {
    constructor() {
        this.isConnected = false;
        this.priceUpdateInterval = null;
        this.assistantMessages = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.createSmartAssistant();
        this.startPriceUpdates();
        this.setupServerSentEvents();
    }

    setupServerSentEvents() {
        // Use Server-Sent Events for real-time updates (Vercel compatible)
        this.eventSource = new EventSource('/api/stream');
        
        this.eventSource.onopen = () => {
            console.log('Connected to real-time updates');
            this.isConnected = true;
            this.updateConnectionStatus(true);
        };
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'price_update') {
                    this.updatePrices(data.data);
                } else if (data.type === 'ai_advice') {
                    this.displayAIAdvice(data.data);
                }
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };
        
        this.eventSource.onerror = () => {
            console.log('Disconnected from real-time updates');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        };
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshAllData();
            });
        }

        // Smart assistant toggle
        const assistantToggle = document.getElementById('assistantToggle');
        if (assistantToggle) {
            assistantToggle.addEventListener('click', () => {
                this.toggleSmartAssistant();
            });
        }

        // AI advice request buttons
        document.querySelectorAll('.ai-advice-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const symbol = e.target.dataset.symbol;
                this.requestAIAdvice(symbol);
            });
        });
    }

    createSmartAssistant() {
        // Create smart assistant panel
        const assistantHTML = `
            <div id="smartAssistant" class="smart-assistant-panel" style="display: none;">
                <div class="assistant-header">
                    <h5><i class="fas fa-robot me-2"></i>دستیار هوشمند معاملات</h5>
                    <button class="btn-close" onclick="vercelRealtimeDashboard.toggleSmartAssistant()"></button>
                </div>
                <div class="assistant-body">
                    <div class="assistant-messages" id="assistantMessages"></div>
                    <div class="assistant-input">
                        <div class="input-group">
                            <input type="text" id="assistantInput" class="form-control" 
                                   placeholder="سوال خود را بپرسید...">
                            <button class="btn btn-primary" onclick="vercelRealtimeDashboard.sendMessage()">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', assistantHTML);
        
        // Add enter key support
        document.getElementById('assistantInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.innerHTML = connected ? 
                '<i class="fas fa-circle text-success me-1"></i>متصل' : 
                '<i class="fas fa-circle text-danger me-1"></i>قطع';
        }
    }

    updatePrices(priceData) {
        Object.keys(priceData).forEach(symbol => {
            const data = priceData[symbol];
            const priceElement = document.getElementById(`${symbol}-USDT-price`);
            const changeElement = document.getElementById(`${symbol}-USDT-change`);
            
            if (priceElement && data.price) {
                const oldPrice = parseFloat(priceElement.textContent.replace(/,/g, ''));
                const newPrice = parseFloat(data.price);
                
                // Update price with animation
                priceElement.textContent = this.formatPrice(newPrice);
                
                // Add flash animation
                if (oldPrice && newPrice !== oldPrice) {
                    priceElement.classList.add(newPrice > oldPrice ? 'price-up-flash' : 'price-down-flash');
                    setTimeout(() => {
                        priceElement.classList.remove('price-up-flash', 'price-down-flash');
                    }, 1000);
                }
            }
            
            if (changeElement && data.change_24h !== undefined) {
                const change = parseFloat(data.change_24h);
                const sign = change >= 0 ? '+' : '';
                changeElement.textContent = `${sign}${change.toFixed(2)}%`;
                
                // Update color classes
                changeElement.classList.remove('positive-change', 'negative-change');
                changeElement.classList.add(change >= 0 ? 'positive-change' : 'negative-change');
            }
        });
    }

    formatPrice(price) {
        if (price >= 1000) {
            return price.toLocaleString('en-US', {maximumFractionDigits: 0});
        } else if (price >= 1) {
            return price.toLocaleString('en-US', {maximumFractionDigits: 2});
        } else if (price >= 0.01) {
            return price.toLocaleString('en-US', {maximumFractionDigits: 4});
        } else {
            return price.toLocaleString('en-US', {maximumFractionDigits: 8});
        }
    }

    startPriceUpdates() {
        // Request price updates every 30 seconds
        this.priceUpdateInterval = setInterval(() => {
            this.refreshAllData();
        }, 30000);
    }

    refreshAllData() {
        // Fetch current prices via API
        const symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT'];
        symbols.forEach(symbol => {
            fetch(`/api/price/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.data) {
                        this.updatePrices({[symbol]: data.data});
                    }
                })
                .catch(error => console.error('Error fetching price:', error));
        });
    }

    toggleSmartAssistant() {
        const assistant = document.getElementById('smartAssistant');
        if (assistant) {
            assistant.style.display = assistant.style.display === 'none' ? 'block' : 'none';
        }
    }

    requestAIAdvice(symbol) {
        fetch('/api/ai-advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol: symbol, timeframe: '1h' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.displayAIAdvice(data.data);
            }
        })
        .catch(error => {
            console.error('Error getting AI advice:', error);
            this.showNotification('خطا در دریافت مشاوره', 'error');
        });
    }

    displayAIAdvice(data) {
        const messagesContainer = document.getElementById('assistantMessages');
        if (messagesContainer) {
            const adviceHTML = `
                <div class="assistant-message ai-message">
                    <div class="message-header">
                        <i class="fas fa-robot me-2"></i>
                        <strong>تحلیل هوشمند ${data.symbol}</strong>
                        <small class="text-muted">${new Date(data.timestamp).toLocaleString('fa-IR')}</small>
                    </div>
                    <div class="message-content">
                        <p><strong>تحلیل تکنیکال:</strong> ${data.analysis || 'در حال تحلیل...'}</p>
                        <p><strong>احساسات بازار:</strong> ${data.sentiment || 'در حال بررسی...'}</p>
                        <p><strong>پیش‌بینی قیمت:</strong> ${data.prediction || 'در حال محاسبه...'}</p>
                    </div>
                </div>
            `;
            messagesContainer.insertAdjacentHTML('beforeend', adviceHTML);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    sendMessage() {
        const input = document.getElementById('assistantInput');
        const message = input.value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            input.value = '';
            
            // Send to AI API
            fetch('/api/ai-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.addMessage(data.response, 'ai');
                } else {
                    this.addMessage('متاسفانه خطایی رخ داده است.', 'ai');
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
                this.addMessage('خطا در ارتباط با سرور', 'ai');
            });
        }
    }

    addMessage(message, sender) {
        const messagesContainer = document.getElementById('assistantMessages');
        if (messagesContainer) {
            const messageHTML = `
                <div class="assistant-message ${sender}-message">
                    <div class="message-header">
                        <i class="fas fa-${sender === 'user' ? 'user' : 'robot'} me-2"></i>
                        <strong>${sender === 'user' ? 'شما' : 'دستیار هوشمند'}</strong>
                        <small class="text-muted">${new Date().toLocaleString('fa-IR')}</small>
                    </div>
                    <div class="message-content">${message}</div>
                </div>
            `;
            messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize real-time dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.vercelRealtimeDashboard = new VercelRealtimeDashboard();
});

// Add CSS for animations and styling
const style = document.createElement('style');
style.textContent = `
    .price-up-flash {
        animation: priceUpFlash 1s ease-in-out;
        background-color: rgba(40, 167, 69, 0.2) !important;
    }
    
    .price-down-flash {
        animation: priceDownFlash 1s ease-in-out;
        background-color: rgba(220, 53, 69, 0.2) !important;
    }
    
    @keyframes priceUpFlash {
        0% { background-color: rgba(40, 167, 69, 0.2); }
        50% { background-color: rgba(40, 167, 69, 0.4); }
        100% { background-color: transparent; }
    }
    
    @keyframes priceDownFlash {
        0% { background-color: rgba(220, 53, 69, 0.2); }
        50% { background-color: rgba(220, 53, 69, 0.4); }
        100% { background-color: transparent; }
    }
    
    .smart-assistant-panel {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        height: 500px;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        z-index: 1000;
        display: flex;
        flex-direction: column;
    }
    
    .assistant-header {
        padding: 15px;
        border-bottom: 1px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .assistant-body {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .assistant-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        max-height: 350px;
    }
    
    .assistant-message {
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 8px;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        margin-left: 20px;
    }
    
    .ai-message {
        background: #28a745;
        color: white;
        margin-right: 20px;
    }
    
    .message-header {
        font-size: 0.8em;
        margin-bottom: 5px;
        opacity: 0.8;
    }
    
    .message-content {
        font-size: 0.9em;
        line-height: 1.4;
    }
    
    .assistant-input {
        padding: 15px;
        border-top: 1px solid #333;
    }
    
    .connection-status {
        position: fixed;
        top: 20px;
        left: 20px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-size: 0.9em;
        z-index: 1000;
    }
`;
document.head.appendChild(style);
