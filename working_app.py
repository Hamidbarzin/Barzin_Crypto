from flask import Flask, render_template_string, jsonify
import requests
import json
import os
from datetime import datetime
import time

app = Flask(__name__)

# Professional HTML template with backend API
template = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>برزین کریپتو - ربات معاملات حرفه‌ای</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .crypto-card { 
            background: rgba(255,255,255,0.95); 
            border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .crypto-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        .price-up { 
            color: #28a745; 
            animation: priceUp 1s ease-in-out; 
        }
        .price-down { 
            color: #dc3545; 
            animation: priceDown 1s ease-in-out; 
        }
        @keyframes priceUp { 
            0% { background-color: rgba(40, 167, 69, 0.3); transform: scale(1.05); } 
            100% { background-color: transparent; transform: scale(1); } 
        }
        @keyframes priceDown { 
            0% { background-color: rgba(220, 53, 69, 0.3); transform: scale(1.05); } 
            100% { background-color: transparent; transform: scale(1); } 
        }
        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 14px;
            z-index: 1000;
        }
        .ai-advice-panel {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .crypto-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .price-display {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .change-display {
            font-size: 1.1rem;
            font-weight: 600;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
        }
        .positive-change {
            background-color: rgba(40, 167, 69, 0.1);
            color: #28a745;
        }
        .negative-change {
            background-color: rgba(220, 53, 69, 0.1);
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="status-indicator" id="statusIndicator">
        <i class="fas fa-circle text-warning me-1"></i>در حال بارگذاری...
    </div>

    <div class="container py-5">
        <div class="row">
            <div class="col-12 text-center mb-5">
                <h1 class="text-white display-3 fw-bold mb-3">
                    <i class="fas fa-robot me-3"></i>برزین کریپتو
                </h1>
                <p class="text-white-50 fs-4 mb-4">ربات معاملات حرفه‌ای با دستیار هوشمند</p>
                <div class="d-flex justify-content-center align-items-center">
                    <button class="btn btn-outline-light btn-lg me-3" onclick="refreshPrices()">
                        <i class="fas fa-sync-alt me-2"></i>به‌روزرسانی
                    </button>
                    <span class="text-white-50">آخرین به‌روزرسانی: <span id="lastUpdate">-</span></span>
                </div>
            </div>
        </div>

        <div class="row" id="cryptoCards">
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100 text-center">
                    <div class="crypto-icon">₿</div>
                    <h4 class="fw-bold mb-3">بیت کوین</h4>
                    <div class="price-display" id="BTC-price">$0</div>
                    <div class="change-display" id="BTC-change">+0.00%</div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm me-2" onclick="getAdvice('BTC', 'bitcoin')">
                            <i class="fas fa-robot me-1"></i>مشاوره
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="showDetails('BTC')">
                            <i class="fas fa-chart-line me-1"></i>جزئیات
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100 text-center">
                    <div class="crypto-icon">Ξ</div>
                    <h4 class="fw-bold mb-3">اتریوم</h4>
                    <div class="price-display" id="ETH-price">$0</div>
                    <div class="change-display" id="ETH-change">+0.00%</div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm me-2" onclick="getAdvice('ETH', 'ethereum')">
                            <i class="fas fa-robot me-1"></i>مشاوره
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="showDetails('ETH')">
                            <i class="fas fa-chart-line me-1"></i>جزئیات
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100 text-center">
                    <div class="crypto-icon">◎</div>
                    <h4 class="fw-bold mb-3">سولانا</h4>
                    <div class="price-display" id="SOL-price">$0</div>
                    <div class="change-display" id="SOL-change">+0.00%</div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm me-2" onclick="getAdvice('SOL', 'solana')">
                            <i class="fas fa-robot me-1"></i>مشاوره
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="showDetails('SOL')">
                            <i class="fas fa-chart-line me-1"></i>جزئیات
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100 text-center">
                    <div class="crypto-icon">X</div>
                    <h4 class="fw-bold mb-3">ریپل</h4>
                    <div class="price-display" id="XRP-price">$0</div>
                    <div class="change-display" id="XRP-change">+0.00%</div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm me-2" onclick="getAdvice('XRP', 'ripple')">
                            <i class="fas fa-robot me-1"></i>مشاوره
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="showDetails('XRP')">
                            <i class="fas fa-chart-line me-1"></i>جزئیات
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="ai-advice-panel" id="aiAdvicePanel" style="display: none;">
                    <h5 class="fw-bold mb-3">
                        <i class="fas fa-robot me-2"></i>دستیار هوشمند
                    </h5>
                    <div id="aiAdviceContent">
                        <div class="text-center text-muted">
                            <i class="fas fa-info-circle me-2"></i>
                            روی دکمه‌های مشاوره کلیک کنید تا تحلیل حرفه‌ای دریافت کنید.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const coinData = {
            'BTC': { id: 'bitcoin', name: 'بیت کوین', symbol: '₿' },
            'ETH': { id: 'ethereum', name: 'اتریوم', symbol: 'Ξ' },
            'SOL': { id: 'solana', name: 'سولانا', symbol: '◎' },
            'XRP': { id: 'ripple', name: 'ریپل', symbol: 'X' }
        };

        let lastPrices = {};

        async function fetchPrices() {
            try {
                updateStatus('در حال دریافت داده‌ها...', 'warning');
                
                // Use backend API instead of direct CoinGecko
                const response = await fetch('/api/prices');
                const data = await response.json();
                
                if (data.success) {
                    for (const [symbol, coinInfo] of Object.entries(coinData)) {
                        if (data.prices[coinInfo.id]) {
                            updatePrice(symbol, data.prices[coinInfo.id]);
                        }
                    }
                    updateStatus('داده‌ها به‌روز شد', 'success');
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('fa-IR');
                } else {
                    throw new Error(data.message || 'خطا در دریافت داده‌ها');
                }
            } catch (error) {
                console.error('Error fetching prices:', error);
                updateStatus('خطا در دریافت داده‌ها', 'danger');
            }
        }

        function updatePrice(symbol, data) {
            const priceElement = document.getElementById(`${symbol}-price`);
            const changeElement = document.getElementById(`${symbol}-change`);
            
            if (priceElement && data.usd) {
                const newPrice = data.usd;
                const oldPrice = lastPrices[symbol] || 0;
                
                priceElement.textContent = `$${formatPrice(newPrice)}`;
                
                // Price change animation
                if (newPrice > oldPrice && oldPrice > 0) {
                    priceElement.classList.add('price-up');
                    setTimeout(() => priceElement.classList.remove('price-up'), 1000);
                } else if (newPrice < oldPrice && oldPrice > 0) {
                    priceElement.classList.add('price-down');
                    setTimeout(() => priceElement.classList.remove('price-down'), 1000);
                }
                
                lastPrices[symbol] = newPrice;
            }
            
            if (changeElement && data.usd_24h_change !== undefined) {
                const change = data.usd_24h_change;
                const sign = change >= 0 ? '+' : '';
                changeElement.textContent = `${sign}${change.toFixed(2)}%`;
                
                changeElement.className = 'change-display ' + (change >= 0 ? 'positive-change' : 'negative-change');
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

        function updateStatus(message, type) {
            const statusElement = document.getElementById('statusIndicator');
            const iconClass = type === 'success' ? 'text-success' : 
                            type === 'warning' ? 'text-warning' : 
                            type === 'danger' ? 'text-danger' : 'text-info';
            
            statusElement.innerHTML = `<i class="fas fa-circle ${iconClass} me-1"></i>${message}`;
        }

        function getAdvice(symbol, coinId) {
            const advicePanel = document.getElementById('aiAdvicePanel');
            const adviceContent = document.getElementById('aiAdviceContent');
            
            advicePanel.style.display = 'block';
            adviceContent.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner me-2"></div>
                    در حال تحلیل ${coinData[symbol].name}...
                </div>
            `;
            
            // Use backend API for advice
            fetch(`/api/advice/${coinId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        adviceContent.innerHTML = data.advice_html;
                    } else {
                        throw new Error(data.message || 'خطا در دریافت مشاوره');
                    }
                })
                .catch(error => {
                    adviceContent.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            خطا در دریافت داده‌ها. لطفاً دوباره تلاش کنید.
                        </div>
                    `;
                });
        }

        function showDetails(symbol) {
            alert(`جزئیات ${coinData[symbol].name} - این ویژگی در نسخه بعدی اضافه خواهد شد`);
        }

        function refreshPrices() {
            fetchPrices();
        }

        // Load prices on page load
        fetchPrices();
        
        // Update prices every 30 seconds
        setInterval(fetchPrices, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(template)

@app.route('/api/prices')
def get_prices():
    try:
        # Fetch from CoinGecko API
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true')
        data = response.json()
        
        return jsonify({
            'success': True,
            'prices': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت قیمت‌ها: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/advice/<coin_id>')
def get_advice(coin_id):
    try:
        # Fetch current data
        response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true')
        data = response.json()
        
        if coin_id in data:
            coin = data[coin_id]
            change = coin['usd_24h_change']
            price = coin['usd']
            market_cap = coin.get('usd_market_cap', 0)
            volume = coin.get('usd_24h_vol', 0)
            
            # Generate professional analysis
            if change > 10:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% افزایش یافته است. روند قوی صعودی با حجم معاملات بالا."
                sentiment = "بسیار مثبت"
                prediction = "احتمال ادامه روند صعودی در کوتاه‌مدت"
                recommendation = "خرید با احتیاط - مدیریت ریسک"
            elif change > 5:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% افزایش یافته است. روند مثبت با پتانسیل رشد."
                sentiment = "مثبت"
                prediction = "احتمال افزایش قیمت در کوتاه‌مدت"
                recommendation = "خرید با حجم کم"
            elif change > 0:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% افزایش یافته است. روند خنثی تا مثبت."
                sentiment = "خنثی تا مثبت"
                prediction = "احتمال نوسان در محدوده فعلی"
                recommendation = "منتظر سیگنال واضح‌تر"
            elif change > -5:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% کاهش یافته است. روند خنثی تا منفی."
                sentiment = "خنثی تا منفی"
                prediction = "احتمال نوسان در محدوده فعلی"
                recommendation = "منتظر سیگنال واضح‌تر"
            elif change > -10:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% کاهش یافته است. روند نزولی با فشار فروش."
                sentiment = "منفی"
                prediction = "احتمال ادامه روند نزولی در کوتاه‌مدت"
                recommendation = "فروش یا انتظار"
            else:
                analysis = f"قیمت {coin_id} در 24 ساعت گذشته {change:.2f}% کاهش یافته است. روند قوی نزولی."
                sentiment = "بسیار منفی"
                prediction = "احتمال ادامه روند نزولی"
                recommendation = "فروش یا انتظار برای ورود در قیمت پایین‌تر"
            
            advice_html = f"""
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="fw-bold text-primary">تحلیل تکنیکال {coin_id}</h6>
                        <p class="mb-3">{analysis}</p>
                        
                        <h6 class="fw-bold text-info">احساسات بازار</h6>
                        <p class="mb-3">{sentiment}</p>
                        
                        <h6 class="fw-bold text-warning">پیش‌بینی قیمت</h6>
                        <p class="mb-3">{prediction}</p>
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold text-success">توصیه معاملاتی</h6>
                        <p class="mb-3 text-success fw-bold">{recommendation}</p>
                        
                        <h6 class="fw-bold text-secondary">اطلاعات بازار</h6>
                        <ul class="list-unstyled">
                            <li><strong>قیمت فعلی:</strong> ${price:,.2f}</li>
                            <li><strong>تغییر 24h:</strong> {change:+.2f}%</li>
                            <li><strong>حجم معاملات:</strong> ${volume/1000000:,.1f}M</li>
                            <li><strong>ارزش بازار:</strong> ${market_cap/1000000000:,.1f}B</li>
                        </ul>
                    </div>
                </div>
                <div class="text-center mt-3">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        آخرین به‌روزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </small>
                </div>
            """
            
            return jsonify({
                'success': True,
                'advice_html': advice_html,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'ارز مورد نظر یافت نشد'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت مشاوره: {str(e)}'
        })

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'message': 'برزین کریپتو - ربات معاملات حرفه‌ای'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 برزین کریپتو - ربات معاملات حرفه‌ای")
    print(f"🌐 در حال اجرا روی پورت {port}")
    print(f"📊 داده‌های زنده از CoinGecko API")
    app.run(host='0.0.0.0', port=port, debug=False)
