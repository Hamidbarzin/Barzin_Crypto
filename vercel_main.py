from flask import Flask, render_template_string, jsonify, request
import requests
import json
import os

app = Flask(__name__)

# Simple HTML template for Vercel
template = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>برزین کریپتو - ربات معاملات کریپتو</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .crypto-card { background: rgba(255,255,255,0.95); border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .price-up { color: #28a745; animation: priceUp 1s ease-in-out; }
        .price-down { color: #dc3545; animation: priceDown 1s ease-in-out; }
        @keyframes priceUp { 0% { background-color: rgba(40, 167, 69, 0.2); } 100% { background-color: transparent; } }
        @keyframes priceDown { 0% { background-color: rgba(220, 53, 69, 0.2); } 100% { background-color: transparent; } }
        .connection-status { padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,0.2); }
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
                <div class="connection-status d-inline-block">
                    <i class="fas fa-circle text-success me-1"></i>متصل - داده‌های زنده
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
                        <button class="btn btn-sm btn-primary" onclick="getPrice('bitcoin')">
                            <i class="fas fa-sync-alt me-1"></i>به‌روزرسانی
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
                        <button class="btn btn-sm btn-primary" onclick="getPrice('ethereum')">
                            <i class="fas fa-sync-alt me-1"></i>به‌روزرسانی
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
                        <button class="btn btn-sm btn-primary" onclick="getPrice('solana')">
                            <i class="fas fa-sync-alt me-1"></i>به‌روزرسانی
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
                        <button class="btn btn-sm btn-primary" onclick="getPrice('ripple')">
                            <i class="fas fa-sync-alt me-1"></i>به‌روزرسانی
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- AI Assistant Panel -->
        <div class="row mt-5">
            <div class="col-12">
                <div class="crypto-card p-4">
                    <h5 class="fw-bold mb-3">
                        <i class="fas fa-robot me-2"></i>دستیار هوشمند معاملات
                    </h5>
                    <div id="assistantMessages" class="mb-3" style="max-height: 300px; overflow-y: auto;">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            برای دریافت مشاوره معاملاتی، روی دکمه‌های "به‌روزرسانی" کلیک کنید تا قیمت‌های زنده دریافت شود.
                        </div>
                    </div>
                    <div class="d-flex">
                        <input type="text" class="form-control me-2" id="assistantInput" placeholder="سوال خود را بپرسید...">
                        <button class="btn btn-success" onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function getPrice(coinId) {
            try {
                const response = await fetch(`/api/price/${coinId}`);
                const data = await response.json();
                
                const symbol = coinId.toUpperCase();
                const priceElement = document.getElementById(`${symbol}-price`);
                const changeElement = document.getElementById(`${symbol}-change`);
                
                if (priceElement && data.price) {
                    priceElement.textContent = `$${formatPrice(data.price)}`;
                    priceElement.classList.add('price-up');
                    setTimeout(() => priceElement.classList.remove('price-up'), 1000);
                }
                
                if (changeElement && data.change_24h !== undefined) {
                    const change = data.change_24h;
                    const sign = change >= 0 ? '+' : '';
                    changeElement.textContent = `${sign}${change.toFixed(2)}%`;
                    changeElement.className = `fs-6 mb-3 ${change >= 0 ? 'text-success' : 'text-danger'}`;
                }

                // Add AI advice based on price change
                addAIAdvice(symbol, data.price, data.change_24h);
            } catch (error) {
                console.error('Error fetching price:', error);
            }
        }

        function addAIAdvice(symbol, price, change24h) {
            const messagesContainer = document.getElementById('assistantMessages');
            let advice = '';
            
            if (change24h > 5) {
                advice = `🚀 ${symbol} در حال رشد قوی است! (+${change24h.toFixed(2)}%) - سیگنال خرید قوی`;
            } else if (change24h > 0) {
                advice = `📈 ${symbol} روند مثبت دارد (+${change24h.toFixed(2)}%) - مناسب برای خرید`;
            } else if (change24h > -5) {
                advice = `⚖️ ${symbol} در محدوده خنثی (${change24h.toFixed(2)}%) - منتظر سیگنال باشید`;
            } else {
                advice = `📉 ${symbol} در حال کاهش است (${change24h.toFixed(2)}%) - احتیاط کنید`;
            }

            const adviceHTML = `
                <div class="alert alert-${change24h > 0 ? 'success' : change24h < -5 ? 'danger' : 'warning'} mb-2">
                    <strong>${symbol}:</strong> ${advice}
                </div>
            `;
            messagesContainer.insertAdjacentHTML('beforeend', adviceHTML);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function formatPrice(price) {
            if (price >= 1000) {
                return price.toLocaleString('en-US', {maximumFractionDigits: 0});
            } else if (price >= 1) {
                return price.toLocaleString('en-US', {maximumFractionDigits: 2});
            } else {
                return price.toLocaleString('en-US', {maximumFractionDigits: 4});
            }
        }

        function sendMessage() {
            const input = document.getElementById('assistantInput');
            const message = input.value.trim();
            if (message) {
                const messagesContainer = document.getElementById('assistantMessages');
                messagesContainer.insertAdjacentHTML('beforeend', 
                    `<div class="alert alert-primary mb-2 text-end">شما: ${message}</div>`
                );
                input.value = '';
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Simple AI response
                setTimeout(() => {
                    messagesContainer.insertAdjacentHTML('beforeend', 
                        `<div class="alert alert-info mb-2">دستیار: برای تحلیل دقیق‌تر، ابتدا قیمت‌های زنده را دریافت کنید.</div>`
                    );
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }, 1000);
            }
        }

        // Load prices on page load
        document.addEventListener('DOMContentLoaded', function() {
            getPrice('bitcoin');
            getPrice('ethereum');
            getPrice('solana');
            getPrice('ripple');
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
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
