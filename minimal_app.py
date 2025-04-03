from flask import Flask, render_template_string
import requests
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # قالب HTML بسیار ساده
    html_template = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ربات ساده ارز دیجیتال</title>
        <style>
            body {
                font-family: Tahoma, Arial, sans-serif;
                margin: 20px;
                line-height: 1.5;
            }
            h1, h2 {
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: right;
            }
            th {
                background-color: #f2f2f2;
            }
            .positive {
                color: green;
            }
            .negative {
                color: red;
            }
        </style>
    </head>
    <body>
        <h1>ربات ساده ارز دیجیتال</h1>
        <p>آخرین به‌روزرسانی: {{ current_time }}</p>
        
        <h2>قیمت ارزهای دیجیتال</h2>
        <table>
            <tr>
                <th>ارز</th>
                <th>قیمت (USDT)</th>
                <th>تغییر 24 ساعته</th>
            </tr>
            {% for coin in crypto_prices %}
            <tr>
                <td>{{ coin.name }}</td>
                <td>{{ coin.price }}</td>
                <td class="{{ 'positive' if coin.change_24h > 0 else 'negative' if coin.change_24h < 0 else '' }}">
                    {{ coin.change_24h }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>قیمت کالاها</h2>
        <table>
            <tr>
                <th>کالا</th>
                <th>قیمت (USD)</th>
                <th>تغییر</th>
            </tr>
            {% for item in commodities %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.price }}</td>
                <td class="{{ 'positive' if item.change > 0 else 'negative' if item.change < 0 else '' }}">
                    {{ item.change }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>نرخ ارزهای جهانی</h2>
        <table>
            <tr>
                <th>ارز</th>
                <th>نرخ</th>
                <th>تغییر</th>
            </tr>
            {% for currency in forex %}
            <tr>
                <td>{{ currency.name }}</td>
                <td>{{ currency.price }}</td>
                <td class="{{ 'positive' if currency.change > 0 else 'negative' if currency.change < 0 else '' }}">
                    {{ currency.change }}%
                </td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>سیگنال‌های معاملاتی</h2>
        <table>
            <tr>
                <th>ارز</th>
                <th>قیمت</th>
                <th>سیگنال</th>
                <th>توصیه</th>
            </tr>
            {% for signal in signals %}
            <tr>
                <td>{{ signal.symbol }}</td>
                <td>{{ signal.price }}</td>
                <td>{{ signal.signal }}</td>
                <td>{{ signal.recommendation }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    # داده‌های نمونه برای ارزهای دیجیتال
    try:
        crypto_response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1', timeout=3)
        if crypto_response.status_code == 200:
            crypto_data = crypto_response.json()
            crypto_prices = [
                {
                    'name': item['name'],
                    'price': item['current_price'],
                    'change_24h': item['price_change_percentage_24h']
                } for item in crypto_data
            ]
        else:
            # داده‌های پیش‌فرض در صورت خطا
            crypto_prices = [
                {'name': 'بیت‌کوین', 'price': 82500, 'change_24h': 2.5},
                {'name': 'اتریوم', 'price': 3200, 'change_24h': 1.8},
                {'name': 'بایننس کوین', 'price': 560, 'change_24h': -0.5},
                {'name': 'ریپل', 'price': 0.52, 'change_24h': 0.2},
                {'name': 'سولانا', 'price': 145, 'change_24h': 3.1}
            ]
    except:
        # داده‌های پیش‌فرض در صورت خطا
        crypto_prices = [
            {'name': 'بیت‌کوین', 'price': 82500, 'change_24h': 2.5},
            {'name': 'اتریوم', 'price': 3200, 'change_24h': 1.8},
            {'name': 'بایننس کوین', 'price': 560, 'change_24h': -0.5},
            {'name': 'ریپل', 'price': 0.52, 'change_24h': 0.2},
            {'name': 'سولانا', 'price': 145, 'change_24h': 3.1}
        ]
    
    # داده‌های نمونه برای کالاها
    commodities = [
        {'name': 'طلا', 'price': 2250.50, 'change': 0.75},
        {'name': 'نقره', 'price': 28.75, 'change': -0.25},
        {'name': 'نفت', 'price': 82.35, 'change': 1.2}
    ]
    
    # داده‌های نمونه برای ارزهای جهانی
    forex = [
        {'name': 'یورو به دلار (EUR/USD)', 'price': 1.0825, 'change': 0.15},
        {'name': 'پوند به دلار (GBP/USD)', 'price': 1.2634, 'change': -0.25},
        {'name': 'دلار به ین (USD/JPY)', 'price': 151.68, 'change': 0.32}
    ]
    
    # داده‌های نمونه برای سیگنال‌های معاملاتی
    signals = [
        {'symbol': 'BTC/USDT', 'price': 82500, 'signal': 'خرید', 'recommendation': 'پیشنهاد معامله نوسانی (صعودی)'},
        {'symbol': 'ETH/USDT', 'price': 3200, 'signal': 'خرید قوی', 'recommendation': 'نقطه ورود مناسب برای معامله نوسانی صعودی'},
        {'symbol': 'BNB/USDT', 'price': 560, 'signal': 'خنثی', 'recommendation': 'صبر کنید'},
        {'symbol': 'SOL/USDT', 'price': 145, 'signal': 'خرید', 'recommendation': 'روند صعودی قوی'},
        {'symbol': 'XRP/USDT', 'price': 0.52, 'signal': 'فروش', 'recommendation': 'احتمال اصلاح قیمت'}
    ]
    
    # زمان فعلی
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # رندر کردن قالب با داده‌ها
    return render_template_string(
        html_template,
        current_time=current_time,
        crypto_prices=crypto_prices,
        commodities=commodities,
        forex=forex,
        signals=signals
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)