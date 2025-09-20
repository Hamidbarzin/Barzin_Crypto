import os
import logging
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import requests

# Basic Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "railway_secret_key")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Simple HTML template for the dashboard
template = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>برزین کریپتو - ربات معاملات کریپتو</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .crypto-card { background: rgba(255,255,255,0.95); border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .price-up { color: #28a745; animation: priceUp 1s ease-in-out; }
        .price-down { color: #dc3545; animation: priceDown 1s ease-in-out; }
        @keyframes priceUp { 0% { background-color: rgba(40, 167, 69, 0.2); } 100% { background-color: transparent; } }
        @keyframes priceDown { 0% { background-color: rgba(220, 53, 69, 0.2); } 100% { background-color: transparent; } }
        .connection-status { padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,0.2); }
        .ai-assistant { position: fixed; bottom: 20px; right: 20px; width: 350px; max-height: 400px; background: white; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); z-index: 1000; display: none; }
        .ai-messages { max-height: 250px; overflow-y: auto; padding: 15px; }
        .ai-input { border: none; border-top: 1px solid #eee; padding: 10px; width: 100%; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row">
            <div class="col-12 text-center mb-5">
                <h1 class="text-white display-4 fw-bold">
                    <i class="fas fa-robot me-3"></i>برزین کریپتو
                </h1>
                <p class="text-white-50 fs-5">ربات معاملات کریپتو با دستیار هوشمند</p>
                <div class="connection-status d-inline-block" id="connectionStatus">
                    <i class="fas fa-circle text-warning me-1"></i>در حال اتصال...
                </div>
            </div>
        </div>

        <div class="row mb-3">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <h4 class="mb-0 me-3 text-white">محبوب‌ترین ارزها</h4>
                    </div>
                    <div class="d-flex align-items-center">
                        <button class="btn btn-sm btn-outline-primary me-2" id="refreshBtn">
                            <i class="fas fa-sync-alt me-1"></i>به‌روزرسانی
                        </button>
                        <button class="btn btn-sm btn-success me-2" id="assistantToggle">
                            <i class="fas fa-robot me-1"></i>دستیار هوشمند
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" id="cryptoCards">
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100">
                    <div class="text-center">
                        <h5 class="fw-bold mb-3">BTC</h5>
                        <div class="fs-4 fw-bold mb-2" id="BTC-price">$0</div>
                        <div class="fs-6 mb-3" id="BTC-change">+0.00%</div>
                        <button class="btn btn-sm btn-primary ai-advice-btn" data-symbol="BTC-USDT">
                            <i class="fas fa-robot me-1"></i>مشاوره هوشمند
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100">
                    <div class="text-center">
                        <h5 class="fw-bold mb-3">ETH</h5>
                        <div class="fs-4 fw-bold mb-2" id="ETH-price">$0</div>
                        <div class="fs-6 mb-3" id="ETH-change">+0.00%</div>
                        <button class="btn btn-sm btn-primary ai-advice-btn" data-symbol="ETH-USDT">
                            <i class="fas fa-robot me-1"></i>مشاوره هوشمند
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100">
                    <div class="text-center">
                        <h5 class="fw-bold mb-3">SOL</h5>
                        <div class="fs-4 fw-bold mb-2" id="SOL-price">$0</div>
                        <div class="fs-6 mb-3" id="SOL-change">+0.00%</div>
                        <button class="btn btn-sm btn-primary ai-advice-btn" data-symbol="SOL-USDT">
                            <i class="fas fa-robot me-1"></i>مشاوره هوشمند
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100">
                    <div class="text-center">
                        <h5 class="fw-bold mb-3">XRP</h5>
                        <div class="fs-4 fw-bold mb-2" id="XRP-price">$0</div>
                        <div class="fs-6 mb-3" id="XRP-change">+0.00%</div>
                        <button class="btn btn-sm btn-primary ai-advice-btn" data-symbol="XRP-USDT">
                            <i class="fas fa-robot me-1"></i>مشاوره هوشمند
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AI Assistant Panel -->
    <div class="ai-assistant" id="aiAssistant">
        <div class="ai-messages" id="aiMessages">
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                دستیار هوشمند آماده است. روی دکمه‌های مشاوره کلیک کنید.
            </div>
        </div>
        <div class="d-flex">
            <input type="text" class="ai-input" id="aiInput" placeholder="سوال خود را بپرسید...">
            <button class="btn btn-success" id="aiSendBtn">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>

    <script>
        const socket = io();
        const symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT'];
        
        // WebSocket event handlers
        socket.on('connect', function() {
            console.log('Connected to WebSocket');
            document.getElementById('connectionStatus').innerHTML = '<i class="fas fa-circle text-success me-1"></i>متصل';
            socket.emit('request_price_update');
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from WebSocket');
            document.getElementById('connectionStatus').innerHTML = '<i class="fas fa-circle text-danger me-1"></i>قطع شد';
        });

        socket.on('price_update', function(data) {
            console.log('Real-time price update:', data.data);
            for (const symbol in data.data) {
                updatePriceDisplay(symbol, data.data[symbol]);
            }
        });

        socket.on('ai_advice', function(data) {
            console.log('AI Advice:', data);
            displayAiMessage(data);
        });

        socket.on('error', function(data) {
            console.error('WebSocket Error:', data.message);
            appendMessage('خطا', data.message, 'error');
        });

        function updatePriceDisplay(symbol, priceInfo) {
            const priceElement = document.getElementById(`${symbol}-price`);
            const changeElement = document.getElementById(`${symbol}-change`);

            if (priceElement && priceInfo.price) {
                const oldPrice = parseFloat(priceElement.textContent.replace(/[^0-9.-]+/g, ""));
                const newPrice = parseFloat(priceInfo.price);

                priceElement.textContent = `$${formatPrice(newPrice)}`;

                if (newPrice > oldPrice) {
                    priceElement.classList.add('price-up');
                    setTimeout(() => priceElement.classList.remove('price-up'), 1000);
                } else if (newPrice < oldPrice) {
                    priceElement.classList.add('price-down');
                    setTimeout(() => priceElement.classList.remove('price-down'), 1000);
                }
            }

            if (changeElement && priceInfo.change_24h !== undefined) {
                const change = parseFloat(priceInfo.change_24h);
                const sign = change >= 0 ? '+' : '';
                changeElement.textContent = `${sign}${change.toFixed(2)}%`;

                if (change >= 0) {
                    changeElement.classList.add('text-success');
                    changeElement.classList.remove('text-danger');
                } else {
                    changeElement.classList.add('text-danger');
                    changeElement.classList.remove('text-success');
                }
            }
        }

        function formatPrice(price) {
            price = parseFloat(price);
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

        function appendMessage(sender, message, type = 'text') {
            const messagesContainer = document.getElementById('aiMessages');
            const msgElement = document.createElement('div');
            msgElement.classList.add('alert', 'mb-2');
            
            if (type === 'error') {
                msgElement.classList.add('alert-danger');
            } else if (sender === 'شما') {
                msgElement.classList.add('alert-primary', 'text-end');
            } else {
                msgElement.classList.add('alert-info');
            }
            
            msgElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
            messagesContainer.appendChild(msgElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function displayAiMessage(advice) {
            let message = `<strong>مشاوره برای ${advice.symbol}:</strong><br>`;
            message += `تحلیل: ${advice.analysis}<br>`;
            message += `احساسات بازار: ${advice.sentiment}<br>`;
            message += `پیش‌بینی قیمت: ${advice.prediction}<br>`;
            message += `<small class="text-muted">(${new Date(advice.timestamp).toLocaleString()})</small>`;
            appendMessage('دستیار هوشمند', message);
        }

        // Event listeners
        document.getElementById('refreshBtn').addEventListener('click', function() {
            socket.emit('request_price_update');
        });

        document.getElementById('assistantToggle').addEventListener('click', function() {
            const assistant = document.getElementById('aiAssistant');
            assistant.style.display = assistant.style.display === 'none' ? 'block' : 'none';
        });

        document.getElementById('aiSendBtn').addEventListener('click', function() {
            const input = document.getElementById('aiInput');
            const message = input.value.trim();
            if (message) {
                appendMessage('شما', message);
                input.value = '';
                // Simple AI response
                setTimeout(() => {
                    appendMessage('دستیار هوشمند', 'متاسفم، من فقط می‌توانم مشاوره معاملاتی ارائه دهم. لطفاً روی دکمه "مشاوره هوشمند" کلیک کنید.');
                }, 1000);
            }
        });

        // AI advice buttons
        document.querySelectorAll('.ai-advice-btn').forEach(button => {
            button.addEventListener('click', function() {
                const symbol = this.dataset.symbol;
                appendMessage('شما', `درخواست مشاوره برای ${symbol}`);
                socket.emit('request_ai_advice', { symbol: symbol, timeframe: '1h' });
                document.getElementById('aiAssistant').style.display = 'block';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(template)

@app.route('/api/price/<coin_id>')
def get_price(coin_id):
    try:
        # Use CoinGecko API
        response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true')
        data = response.json()
        
        if coin_id in data:
            return {
                'price': data[coin_id]['usd'],
                'change_24h': data[coin_id]['usd_24h_change']
            }
        else:
            return {'error': 'Coin not found'}, 404
    except Exception as e:
        logger.error(f"Error getting price for {coin_id}: {e}")
        return {'error': str(e)}, 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to WebSocket')
    emit('status', {'message': 'Connected to real-time updates'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from WebSocket')

@socketio.on('request_price_update')
def handle_price_update_request():
    """Handle real-time price update requests"""
    try:
        # Get current prices for main cryptocurrencies
        symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT']
        price_data = {}

        for symbol in symbols:
            try:
                # Map symbols to CoinGecko IDs
                coin_id_map = {
                    'BTC-USDT': 'bitcoin',
                    'ETH-USDT': 'ethereum',
                    'SOL-USDT': 'solana',
                    'XRP-USDT': 'ripple'
                }
                
                coin_id = coin_id_map.get(symbol, 'bitcoin')
                response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true')
                data = response.json()
                
                if coin_id in data:
                    price_data[symbol] = {
                        'price': data[coin_id]['usd'],
                        'change_24h': data[coin_id]['usd_24h_change']
                    }
            except Exception as e:
                logger.error(f"Error getting price for {symbol}: {e}")

        emit('price_update', {'data': price_data})
    except Exception as e:
        logger.error(f"Error in price update handler: {e}")
        emit('error', {'message': 'Failed to update prices'})

@socketio.on('request_ai_advice')
def handle_ai_advice_request(data):
    """Handle AI trading advice requests"""
    try:
        symbol = data.get('symbol', 'BTC-USDT')
        timeframe = data.get('timeframe', '1h')

        # Simple AI analysis based on current price
        try:
            coin_id_map = {
                'BTC-USDT': 'bitcoin',
                'ETH-USDT': 'ethereum',
                'SOL-USDT': 'solana',
                'XRP-USDT': 'ripple'
            }
            
            coin_id = coin_id_map.get(symbol, 'bitcoin')
            response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true')
            data = response.json()
            
            if coin_id in data:
                change_24h = data[coin_id]['usd_24h_change']
                price = data[coin_id]['usd']
                
                # Generate advice based on price change
                if change_24h > 5:
                    analysis = f"قیمت {symbol} در 24 ساعت گذشته {change_24h:.2f}% افزایش یافته است. روند قوی صعودی."
                    sentiment = "بسیار مثبت"
                    prediction = "احتمال ادامه روند صعودی در کوتاه‌مدت"
                elif change_24h > 0:
                    analysis = f"قیمت {symbol} در 24 ساعت گذشته {change_24h:.2f}% افزایش یافته است. روند مثبت."
                    sentiment = "مثبت"
                    prediction = "احتمال افزایش قیمت در کوتاه‌مدت"
                elif change_24h > -5:
                    analysis = f"قیمت {symbol} در 24 ساعت گذشته {change_24h:.2f}% تغییر کرده است. روند خنثی."
                    sentiment = "خنثی"
                    prediction = "احتمال نوسان در محدوده فعلی"
                else:
                    analysis = f"قیمت {symbol} در 24 ساعت گذشته {change_24h:.2f}% کاهش یافته است. روند نزولی."
                    sentiment = "منفی"
                    prediction = "احتمال ادامه روند نزولی در کوتاه‌مدت"
            else:
                analysis = f"تحلیل تکنیکال {symbol} در حال بررسی است..."
                sentiment = "در حال بررسی"
                prediction = "لطفاً لحظاتی صبر کنید"
        except Exception as e:
            logger.error(f"Error getting price data for AI advice: {e}")
            analysis = f"تحلیل تکنیکال {symbol} در حال بررسی است..."
            sentiment = "در حال بررسی"
            prediction = "لطفاً لحظاتی صبر کنید"

        advice = {
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis': analysis,
            'sentiment': sentiment,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        }

        emit('ai_advice', advice)
    except Exception as e:
        logger.error(f"Error in AI advice handler: {e}")
        emit('error', {'message': 'Failed to get AI advice'})

# Background task for periodic price updates
def background_price_updates():
    """Background task to send periodic price updates to connected clients"""
    while True:
        try:
            time.sleep(30)  # Update every 30 seconds
            symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT']
            price_data = {}

            for symbol in symbols:
                try:
                    coin_id_map = {
                        'BTC-USDT': 'bitcoin',
                        'ETH-USDT': 'ethereum',
                        'SOL-USDT': 'solana',
                        'XRP-USDT': 'ripple'
                    }
                    
                    coin_id = coin_id_map.get(symbol, 'bitcoin')
                    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true')
                    data = response.json()
                    
                    if coin_id in data:
                        price_data[symbol] = {
                            'price': data[coin_id]['usd'],
                            'change_24h': data[coin_id]['usd_24h_change']
                        }
                except Exception as e:
                    logger.error(f"Error getting price for {symbol}: {e}")

            if price_data:
                socketio.emit('price_update', {'data': price_data})
        except Exception as e:
            logger.error(f"Error in background price updates: {e}")

# Start background task
import threading
price_thread = threading.Thread(target=background_price_updates, daemon=True)
price_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
