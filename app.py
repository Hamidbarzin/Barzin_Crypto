from flask import Flask, render_template_string
import requests
import json

app = Flask(__name__)

# Simple HTML template
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
            </div>
        </div>

        <div class="row" id="cryptoCards">
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="crypto-card p-4 h-100">
                    <div class="text-center">
                        <h5 class="fw-bold mb-3">BTC</h5>
                        <div class="fs-4 fw-bold mb-2" id="BTC-price">$0</div>
                        <div class="fs-6 mb-3" id="BTC-change">+0.00%</div>
                        <button class="btn btn-sm btn-primary" onclick="getAdvice('BTC')">
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
                        <button class="btn btn-sm btn-primary" onclick="getAdvice('ETH')">
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
                        <button class="btn btn-sm btn-primary" onclick="getAdvice('SOL')">
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
                        <button class="btn btn-sm btn-primary" onclick="getAdvice('XRP')">
                            <i class="fas fa-robot me-1"></i>مشاوره هوشمند
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="crypto-card p-4">
                    <h5 class="fw-bold mb-3">دستیار هوشمند</h5>
                    <div id="aiAdvice" class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        روی دکمه‌های مشاوره کلیک کنید تا تحلیل دریافت کنید.
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const coinIds = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'SOL': 'solana',
            'XRP': 'ripple'
        };

        async function fetchPrices() {
            try {
                const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd&include_24hr_change=true');
                const data = await response.json();
                
                for (const [symbol, coinId] of Object.entries(coinIds)) {
                    if (data[coinId]) {
                        updatePrice(symbol, data[coinId].usd, data[coinId].usd_24h_change);
                    }
                }
            } catch (error) {
                console.error('Error fetching prices:', error);
            }
        }

        function updatePrice(symbol, price, change) {
            const priceElement = document.getElementById(`${symbol}-price`);
            const changeElement = document.getElementById(`${symbol}-change`);
            
            if (priceElement) {
                priceElement.textContent = `$${formatPrice(price)}`;
                
                if (change >= 0) {
                    priceElement.classList.add('price-up');
                    changeElement.classList.add('text-success');
                    changeElement.classList.remove('text-danger');
                } else {
                    priceElement.classList.add('price-down');
                    changeElement.classList.add('text-danger');
                    changeElement.classList.remove('text-success');
                }
                
                setTimeout(() => {
                    priceElement.classList.remove('price-up', 'price-down');
                }, 1000);
            }
            
            if (changeElement) {
                const sign = change >= 0 ? '+' : '';
                changeElement.textContent = `${sign}${change.toFixed(2)}%`;
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

        function getAdvice(symbol) {
            const coinId = coinIds[symbol];
            const adviceElement = document.getElementById('aiAdvice');
            
            adviceElement.innerHTML = `
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                در حال تحلیل ${symbol}...
            `;
            
            fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true`)
                .then(response => response.json())
                .then(data => {
                    if (data[coinId]) {
                        const change = data[coinId].usd_24h_change;
                        const price = data[coinId].usd;
                        
                        let analysis, sentiment, prediction;
                        
                        if (change > 5) {
                            analysis = `قیمت ${symbol} در 24 ساعت گذشته ${change.toFixed(2)}% افزایش یافته است. روند قوی صعودی.`;
                            sentiment = "بسیار مثبت";
                            prediction = "احتمال ادامه روند صعودی در کوتاه‌مدت";
                        } else if (change > 0) {
                            analysis = `قیمت ${symbol} در 24 ساعت گذشته ${change.toFixed(2)}% افزایش یافته است. روند مثبت.`;
                            sentiment = "مثبت";
                            prediction = "احتمال افزایش قیمت در کوتاه‌مدت";
                        } else if (change > -5) {
                            analysis = `قیمت ${symbol} در 24 ساعت گذشته ${change.toFixed(2)}% تغییر کرده است. روند خنثی.`;
                            sentiment = "خنثی";
                            prediction = "احتمال نوسان در محدوده فعلی";
                        } else {
                            analysis = `قیمت ${symbol} در 24 ساعت گذشته ${change.toFixed(2)}% کاهش یافته است. روند نزولی.`;
                            sentiment = "منفی";
                            prediction = "احتمال ادامه روند نزولی در کوتاه‌مدت";
                        }
                        
                        adviceElement.innerHTML = `
                            <h6 class="fw-bold">مشاوره برای ${symbol}</h6>
                            <p><strong>تحلیل:</strong> ${analysis}</p>
                            <p><strong>احساسات بازار:</strong> ${sentiment}</p>
                            <p><strong>پیش‌بینی قیمت:</strong> ${prediction}</p>
                            <p><strong>قیمت فعلی:</strong> $${formatPrice(price)}</p>
                            <small class="text-muted">آخرین به‌روزرسانی: ${new Date().toLocaleString()}</small>
                        `;
                    }
                })
                .catch(error => {
                    adviceElement.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            خطا در دریافت داده‌ها. لطفاً دوباره تلاش کنید.
                        </div>
                    `;
                });
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))