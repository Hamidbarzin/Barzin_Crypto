// Real-time Dashboard with WebSocket and Smart Assistant
class RealtimeDashboard {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.priceUpdateInterval = null;
        this.assistantMessages = [];
        this.init();
    }

    init() {
        this.initializeWebSocket();
        this.setupEventListeners();
        this.createSmartAssistant();
        this.startPriceUpdates();
    }

    initializeWebSocket() {
        // Load Socket.IO client library
        const script = document.createElement('script');
        script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
        script.onload = () => {
            this.socket = io();
            this.setupSocketEvents();
        };
        document.head.appendChild(script);
    }

    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to real-time updates');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.socket.emit('request_price_update');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from real-time updates');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('price_update', (data) => {
            this.updatePrices(data.data);
        });

        this.socket.on('ai_advice', (data) => {
            this.displayAIAdvice(data);
        });

        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data.message);
            this.showNotification('خطا در دریافت داده‌ها: ' + data.message, 'error');
        });
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
                    <button class="btn-close" onclick="realtimeDashboard.toggleSmartAssistant()"></button>
                </div>
                <div class="assistant-body">
                    <div class="assistant-messages" id="assistantMessages"></div>
                    <div class="assistant-input">
                        <div class="input-group">
                            <input type="text" id="assistantInput" class="form-control" 
                                   placeholder="سوال خود را بپرسید...">
                            <button class="btn btn-primary" onclick="realtimeDashboard.sendMessage()">
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
            if (this.isConnected) {
                this.socket.emit('request_price_update');
            }
        }, 30000);
    }

    refreshAllData() {
        if (this.isConnected) {
            this.socket.emit('request_price_update');
            this.showNotification('در حال به‌روزرسانی داده‌ها...', 'info');
        } else {
            this.showNotification('اتصال برقرار نیست', 'error');
        }
    }

    toggleSmartAssistant() {
        const assistant = document.getElementById('smartAssistant');
        if (assistant) {
            assistant.style.display = assistant.style.display === 'none' ? 'block' : 'none';
        }
    }

    requestAIAdvice(symbol) {
        if (this.isConnected) {
            this.socket.emit('request_ai_advice', { symbol: symbol, timeframe: '1h' });
            this.showNotification('در حال دریافت مشاوره هوشمند...', 'info');
        } else {
            this.showNotification('اتصال برقرار نیست', 'error');
        }
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
            
            // Simulate AI response (in real implementation, this would call the backend)
            setTimeout(() => {
                this.addMessage(this.generateAIResponse(message), 'ai');
            }, 1000);
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

    generateAIResponse(message) {
        // Simple AI response generator (in real implementation, this would use OpenAI or similar)
        const responses = [
            'بر اساس تحلیل تکنیکال، پیشنهاد می‌کنم صبر کنید تا سیگنال‌های واضح‌تری دریافت کنید.',
            'احساسات بازار در حال حاضر مثبت است. می‌توانید با احتیاط وارد معامله شوید.',
            'RSI در حال حاضر در محدوده خنثی است. منتظر شکست سطح مقاومت باشید.',
            'MACD نشان‌دهنده سیگنال خرید است. می‌توانید با حجم کم وارد شوید.',
            'سطح حمایت قوی در این محدوده وجود دارد. ریسک کم است.'
        ];
        return responses[Math.floor(Math.random() * responses.length)];
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
    window.realtimeDashboard = new RealtimeDashboard();
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
