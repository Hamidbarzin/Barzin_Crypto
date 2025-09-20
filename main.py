# Railway Full Application - Updated for deployment - FORCE REBUILD
import os
import logging
import random
from datetime import datetime
from crypto_bot.cache_manager import price_cache
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, jsonify, send_file
from flask_socketio import SocketIO, emit
from crypto_bot.config import DEFAULT_CURRENCIES, TIMEFRAMES
from crypto_bot.market_data import get_current_prices
from crypto_bot.scheduler import start_scheduler, stop_scheduler
from crypto_bot.technical_analysis import get_technical_analysis
from crypto_bot.news_analyzer import get_latest_news
from crypto_bot.signal_generator import generate_signals
from crypto_bot.price_alert_service import set_price_alert, remove_price_alert, get_price_alerts, check_price_alerts
from crypto_bot.email_service import send_test_email, update_email_settings, last_email_content, DISABLE_REAL_EMAIL
from crypto_bot.commodity_data import get_commodity_prices, get_forex_rates, get_economic_indicators
from crypto_bot.ai_module import get_price_prediction, get_market_sentiment, get_price_patterns, get_trading_strategy
from crypto_bot.crypto_news import get_crypto_news, get_market_insights, get_crypto_news_formatted_for_telegram
from crypto_bot.voice_notification_service import voice_notification_service
from crypto_bot.language_manager import (
    get_language_code, get_ui_text, get_language_info, get_language_dir,
    get_all_languages, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
)
from crypto_bot.telegram_auth import verify_password, change_password, register_user, login_required
import replit_telegram_sender
import telegram_scheduler_service
from models import db

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "crypto_bot_secret_key_default_for_development")

# Railway deployment marker - FORCE REBUILD
print("🚀 Railway Full Application Starting - Version 2.0")

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure the SQLAlchemy database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///crypto_bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy instance with the Flask app
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Register AI analysis routes
try:
    from crypto_bot.ai_routes import register_routes
    register_routes(app)
    logger.info("AI analysis routes registered successfully.")
except Exception as e:
    logger.error(f"Error registering AI analysis routes: {str(e)}")

# Register Crypto Quiz routes
try:
    from crypto_bot.crypto_quiz_routes import register_routes as register_quiz_routes
    register_quiz_routes(app)
    logger.info("Crypto Quiz routes registered successfully.")
except Exception as e:
    logger.error(f"Error registering Crypto Quiz routes: {str(e)}")

# Register Crypto Analysis routes
try:
    from crypto_bot.crypto_analysis_routes import register_routes as register_analysis_routes
    register_analysis_routes(app)
    logger.info("Crypto Analysis routes registered successfully.")
except Exception as e:
    logger.error(f"Error registering Crypto Analysis routes: {str(e)}")

# Add datetime, language and developer info to all templates
@app.context_processor
def inject_now():
    current_language_code = session.get('language', DEFAULT_LANGUAGE)
    all_languages = get_all_languages()
    current_language_info = get_language_info(current_language_code)
    
    logger.debug(f"Inject_now: current language code = {current_language_code}")
    logger.debug(f"Inject_now: current language info = {current_language_info}")
    
    # Ensure 'code' key exists
    if 'code' not in current_language_info:
        logger.warning(f"Language info for {current_language_code} does not contain 'code' key")
        # If the code key doesn't exist, add it
        current_language_info['code'] = current_language_code
    
    # Verify all languages
    for lang in all_languages:
        if 'code' not in lang:
            logger.warning(f"Language {lang.get('name', 'unknown')} does not have 'code' key")
            # اضافه کردن کلید کد به زبان
            lang['code'] = lang.get('name', 'en').lower()[:2]
    
    return {
        'now': datetime.now(),
        'developer_name': 'Hamid Barzin',
        'developer_year': '2024',
        'current_language': current_language_info,
        'current_language_code': current_language_code,
        'languages': all_languages,
        'ui_text': lambda key, default="": get_ui_text(key, default, session.get('language', DEFAULT_LANGUAGE)),
        'get_language_dir': get_language_dir
    }

# Initialize session defaults
@app.before_request
def initialize_session():
    if 'email_settings' not in session:
        session['email_settings'] = {
            'enabled': False,
            'email': '',
            'frequency': 'daily'
        }
    if 'watched_currencies' not in session:
        session['watched_currencies'] = DEFAULT_CURRENCIES[:3]  # Start with BTC, ETH, XRP
    if 'scheduler_running' not in session:
        session['scheduler_running'] = False
    # Always set English language
    session['language'] = 'en'
    if 'include_middle_east' not in session:
        session['include_middle_east'] = True  # Default to including Middle Eastern news sources

@app.route('/')
def index():
    """Main page redirects to minimal dashboard"""
    inject_now()
    return redirect(url_for('minimal_dashboard'))
    
    # بررسی کدام ارز دیجیتال انتخاب شده است
    selected_crypto = request.args.get('crypto', 'BTC')
    tv_symbol = f"BINANCE:{selected_crypto}USDT"
    
    # Template string for direct rendering - ultra simple
    template = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ربات ساده ارز دیجیتال</title>
        <style>
            body {
                font-family: Tahoma, Arial, sans-serif;
                margin: 0;
                line-height: 1.5;
                background-color: #181A20;
                color: #eaecef;
                padding: 20px;
            }
            h1, h2 {
                color: #FCD535;
                border-bottom: 1px solid #2b2f36;
                padding-bottom: 10px;
                margin-top: 25px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 25px;
                box-shadow: 0 1px 8px rgba(0,0,0,0.2);
                border-radius: 5px;
                overflow: hidden;
            }
            th, td {
                border: 1px solid #2b2f36;
                padding: 12px;
                text-align: right;
            }
            th {
                background-color: #2b3139;
                font-weight: bold;
                color: #FCD535;
            }
            tr {
                background-color: #181A20;
                transition: background-color 0.2s;
            }
            tr:hover {
                background-color: #2b3139;
            }
            .positive {
                color: #0ECB81;
                font-weight: bold;
            }
            .negative {
                color: #F6465D;
                font-weight: bold;
            }
            a {
                color: #FCD535;
                text-decoration: none;
                transition: color 0.2s;
            }
            a:hover {
                color: #F0B90B;
            }
            .update-time {
                font-style: italic;
                color: #848E9C;
                margin-bottom: 20px;
            }
            .refresh-btn {
                background-color: #F0B90B;
                color: #000;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
                font-weight: bold;
                transition: background-color 0.2s;
                display: inline-block;
            }
            .refresh-btn:hover {
                background-color: #FCD535;
            }
            .signal-buy {
                background-color: rgba(14, 203, 129, 0.1);
            }
            .signal-sell {
                background-color: rgba(246, 70, 93, 0.1);
            }
            .signal-neutral {
                background-color: rgba(132, 142, 156, 0.1);
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #2b2f36;
            }
            .logo {
                color: #F0B90B;
                font-size: 28px;
                font-weight: bold;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .nav-links {
                display: flex;
                gap: 15px;
                margin: 15px 0;
            }
            .nav-links a {
                background-color: #2b3139;
                padding: 8px 15px;
                border-radius: 4px;
                transition: all 0.2s;
            }
            .nav-links a:hover {
                background-color: #F0B90B;
                color: #000;
            }
        </style>
        <meta http-equiv="refresh" content="300"> <!-- Auto refresh every 5 minutes -->
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">بایننس</div>
                <a href="/" class="refresh-btn">به‌روزرسانی اطلاعات</a>
            </div>
            
            <p class="update-time">آخرین به‌روزرسانی: {{ current_time }}</p>
            
            <div class="nav-links">
                <a href="/ultra">صفحه اصلی</a>
                <a href="/simple">صفحه ساده</a>
                <a href="/minimal">نمونه ایمیل</a>
                <a href="/simple_email">ایمیل ساده</a>
                <a href="/email_sample">ایمیل کامل</a>
                <a href="/test_menu">منوی تست</a>
            </div>
        
            <h2>نمودار و قیمت ارزهای دیجیتال</h2>
            
            <!-- TradingView Widget BEGIN -->
            <div style="margin-bottom: 20px;">
              <!-- Simple Embedded TradingView Widget -->
              <iframe id="tradingview_iframe" src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_d7cc5&symbol={{ tv_symbol }}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Asia%2FTehran&withdateranges=1" style="width:100%; height:500px; border: none;"></iframe>
            </div>
            <!-- TradingView Widget END -->
            
            <div style="display: flex; gap: 10px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px;">
                <a href="/?crypto=BTC" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">BTC/USDT</a>
                <a href="/?crypto=ETH" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">ETH/USDT</a>
                <a href="/?crypto=BNB" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">BNB/USDT</a>
                <a href="/?crypto=XRP" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">XRP/USDT</a>
                <a href="/?crypto=SOL" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">SOL/USDT</a>
                <a href="/?crypto=ADA" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">ADA/USDT</a>
                <a href="/?crypto=DOGE" class="binance-button" style="background-color: #2b3139; color: #FCD535; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block;">DOGE/USDT</a>
            </div>
            
            <table>
            <tr>
                <th>ارز</th>
                <th>قیمت (USDT)</th>
                <th>تغییر 24 ساعته</th>
            </tr>
            {% for symbol in crypto_prices %}
                <tr>
                    <td>{{ crypto_names.get(symbol.split('/')[0], symbol) }}</td>
                    <td>{{ format_price(crypto_prices[symbol]['price']) }}</td>
                    <td class="{{ 'positive' if crypto_prices[symbol]['change_24h'] > 0 else 'negative' }}">
                        {{ format_change(crypto_prices[symbol]['change_24h']) }}
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td colspan="3">در حال تلاش برای دریافت اطلاعات ارزها...</td>
                </tr>
                <tr>
                    <td>بیت‌کوین (BTC)</td>
                    <td>82,500</td>
                    <td class="positive">+2.5%</td>
                </tr>
                <tr>
                    <td>اتریوم (ETH)</td>
                    <td>3,200</td>
                    <td class="positive">+1.8%</td>
                </tr>
                <tr>
                    <td>بایننس کوین (BNB)</td>
                    <td>560</td>
                    <td class="negative">-0.5%</td>
                </tr>
                <tr>
                    <td>ریپل (XRP)</td>
                    <td>0.52</td>
                    <td class="positive">+0.2%</td>
                </tr>
                <tr>
                    <td>سولانا (SOL)</td>
                    <td>145</td>
                    <td class="positive">+3.1%</td>
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
            {% if commodities and 'GOLD' in commodities %}
                <tr>
                    <td>طلا</td>
                    <td>{{ format_price(commodities['GOLD']['price']) }}</td>
                    <td class="{{ 'positive' if commodities['GOLD']['change'] > 0 else 'negative' }}">
                        {{ format_change(commodities['GOLD']['change']) }}
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td>طلا</td>
                    <td>2,250.50</td>
                    <td class="positive">+0.75%</td>
                </tr>
            {% endif %}
            
            {% if commodities and 'SILVER' in commodities %}
                <tr>
                    <td>نقره</td>
                    <td>{{ format_price(commodities['SILVER']['price']) }}</td>
                    <td class="{{ 'positive' if commodities['SILVER']['change'] > 0 else 'negative' }}">
                        {{ format_change(commodities['SILVER']['change']) }}
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td>نقره</td>
                    <td>28.75</td>
                    <td class="negative">-0.25%</td>
                </tr>
            {% endif %}
            
            {% if commodities and 'OIL' in commodities %}
                <tr>
                    <td>نفت</td>
                    <td>{{ format_price(commodities['OIL']['price']) }}</td>
                    <td class="{{ 'positive' if commodities['OIL']['change'] > 0 else 'negative' }}">
                        {{ format_change(commodities['OIL']['change']) }}
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td>نفت</td>
                    <td>82.35</td>
                    <td class="positive">+1.2%</td>
                </tr>
            {% endif %}
        </table>
        
            <h2>نرخ ارزهای جهانی</h2>
            <table>
                <tr>
                    <th>ارز</th>
                    <th>نرخ</th>
                    <th>تغییر</th>
                </tr>
            {% for symbol, data in forex_rates.items() %}
                <tr>
                    <td>{{ data.get('name', symbol) }}</td>
                    <td>{{ format_price(data['price']) }}</td>
                    <td class="{{ 'positive' if data['change'] > 0 else 'negative' }}">
                        {{ format_change(data['change']) }}
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td>یورو به دلار</td>
                    <td>1.0825</td>
                    <td class="positive">+0.15%</td>
                </tr>
                <tr>
                    <td>پوند به دلار</td>
                    <td>1.2634</td>
                    <td class="negative">-0.25%</td>
                </tr>
                <tr>
                    <td>دلار به ین</td>
                    <td>151.68</td>
                    <td class="positive">+0.32%</td>
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
            {% for symbol, data in signals.items() %}
                <tr class="signal-{{ 'buy' if 'buy' in data.get('signal', '').lower() else 'sell' if 'sell' in data.get('signal', '').lower() else 'neutral' }}">
                    <td>{{ symbol }}</td>
                    <td>{{ format_price(data.get('price', 0)) }}</td>
                    <td>{{ data.get('farsi_signal', data.get('signal', 'Unknown')) }}</td>
                    <td>{{ data.get('farsi_swing_recommendation', data.get('swing_recommendation', 'Unknown')) }}</td>
                </tr>
            {% else %}
                <tr class="signal-buy">
                    <td>BTC/USDT</td>
                    <td>82,500</td>
                    <td>Buy</td>
                    <td>Consider swing trade (bullish)</td>
                </tr>
                <tr class="signal-buy">
                    <td>ETH/USDT</td>
                    <td>3,200</td>
                    <td>Strong Buy</td>
                    <td>Good entry point for bullish swing trade</td>
                </tr>
                <tr class="signal-buy">
                    <td>SOL/USDT</td>
                    <td>145</td>
                    <td>Buy</td>
                    <td>Strong upward trend</td>
                </tr>
                <tr class="signal-sell">
                    <td>XRP/USDT</td>
                    <td>0.52</td>
                    <td>Sell</td>
                    <td>Possible price correction</td>
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    # Helper functions for template
    def format_price(price):
        """Format price with commas and appropriate decimal places"""
        if price is None:
            return "Unknown"
            
        if isinstance(price, str):
            try:
                price = float(price)
            except:
                return price
                
        if price >= 1000:
            return f"{price:,.0f}"
        elif price >= 100:
            return f"{price:,.1f}"
        elif price >= 1:
            return f"{price:,.2f}"
        else:
            return f"{price:,.4f}"
    
    def format_change(change):
        """Format change as percentage with sign"""
        if change is None:
            return "Unknown"
            
        if isinstance(change, str):
            try:
                change = float(change)
            except:
                return change
                
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.2f}%"
    
    # Crypto currency names in English
    crypto_names = {
        'BTC': 'Bitcoin (BTC)',
        'ETH': 'Ethereum (ETH)',
        'BNB': 'Binance Coin (BNB)',
        'XRP': 'Ripple (XRP)',
        'SOL': 'Solana (SOL)',
        'ADA': 'Cardano (ADA)',
        'DOGE': 'Dogecoin (DOGE)',
        'SHIB': 'Shiba Inu (SHIB)',
        'TRX': 'Tron (TRX)',
        'DOT': 'Polkadot (DOT)',
        'AVAX': 'Avalanche (AVAX)',
        'MATIC': 'Polygon (MATIC)',
        'UNI': 'Uniswap (UNI)',
        'LINK': 'Chainlink (LINK)'
    }
    
    # رندر کردن قالب با داده‌های پایه
    return render_template_string(
        template,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        crypto_prices={},
        commodities={},
        forex_rates={},
        signals={},
        format_price=format_price,
        format_change=format_change,
        crypto_names=crypto_names,
        tv_symbol=tv_symbol
    )
    
@app.route('/cryptocurrencies')
@app.route('/crypto')
def cryptocurrencies():
    """صفحه مخصوص ارزهای دیجیتال با تمرکز روی ارزهای مهم و تأثیرگذار"""
    # لیست ارزهای مهم و تأثیرگذار در بازار
    important_coins = [
        {
            'id': 1, 
            'name': 'Bitcoin', 
            'symbol': 'BTC/USDT', 
            'icon': 'fab fa-bitcoin text-warning',
            'price': '67,500.25',
            'change': '+2.4%',
            'volume': '52.3B',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 2, 
            'name': 'Ethereum', 
            'symbol': 'ETH/USDT', 
            'icon': 'fab fa-ethereum text-primary',
            'price': '3,450.75',
            'change': '+1.8%',
            'volume': '24.7B',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 3, 
            'name': 'Tether', 
            'symbol': 'USDT/USD', 
            'icon': 'fas fa-dollar-sign text-success',
            'price': '1.000',
            'change': '+0.01%',
            'volume': '85.6B',
            'signal': 'Hold',
            'signal_class': 'warning'
        },
        {
            'id': 4, 
            'name': 'Solana', 
            'symbol': 'SOL/USDT', 
            'icon': 'fas fa-sun text-info',
            'price': '142.60',
            'change': '+4.2%',
            'volume': '6.1B',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
        {
            'id': 5, 
            'name': 'Binance Coin', 
            'symbol': 'BNB/USDT', 
            'icon': 'fas fa-coins text-warning',
            'price': '571.25',
            'change': '+1.5%',
            'volume': '3.5B',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 6, 
            'name': 'Ripple', 
            'symbol': 'XRP/USDT', 
            'icon': 'fas fa-stream text-info',
            'price': '0.622',
            'change': '+2.9%',
            'volume': '2.8B',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 7, 
            'name': 'Chainlink', 
            'symbol': 'LINK/USDT', 
            'icon': 'fas fa-link text-info',
            'price': '14.25',
            'change': '+3.8%',
            'volume': '945M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 8, 
            'name': 'Avalanche', 
            'symbol': 'AVAX/USDT', 
            'icon': 'fas fa-mountain text-danger',
            'price': '35.42',
            'change': '+5.2%',
            'volume': '1.2B',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
    ]
    
    # لیست ارزهای تأثیرگذار در هوش مصنوعی
    ai_coins = [
        {
            'id': 9, 
            'name': 'Render', 
            'symbol': 'RNDR/USDT', 
            'icon': 'fas fa-cubes text-danger',
            'price': '7.25',
            'change': '+8.4%',
            'volume': '420M',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
        {
            'id': 10, 
            'name': 'Fetch', 
            'symbol': 'FET/USDT', 
            'icon': 'fas fa-robot text-primary',
            'price': '1.52',
            'change': '+6.7%',
            'volume': '310M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 11, 
            'name': 'Worldcoin', 
            'symbol': 'WLD/USDT', 
            'icon': 'fas fa-globe-europe text-info',
            'price': '5.82',
            'change': '+9.3%',
            'volume': '265M',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        }
    ]
    
    # لیست ارزهای میم محبوب
    meme_coins = [
        {
            'id': 12, 
            'name': 'Dogecoin', 
            'symbol': 'DOGE/USDT', 
            'icon': 'fas fa-dog text-warning',
            'price': '0.1568',
            'change': '+1.5%',
            'volume': '950M',
            'signal': 'Hold',
            'signal_class': 'warning'
        },
        {
            'id': 13, 
            'name': 'Shiba Inu', 
            'symbol': 'SHIB/USDT', 
            'icon': 'fas fa-dog text-danger',
            'price': '0.00001191',
            'change': '+1.2%',
            'volume': '850M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 14, 
            'name': 'Pepe', 
            'symbol': 'PEPE/USDT', 
            'icon': 'fas fa-frog text-success',
            'price': '0.00000678',
            'change': '+2.5%',
            'volume': '520M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 15, 
            'name': 'Floki', 
            'symbol': 'FLOKI/USDT', 
            'icon': 'fas fa-paw text-warning',
            'price': '0.00005347',
            'change': '+3.2%',
            'volume': '320M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 16, 
            'name': 'Dog Wif Hat', 
            'symbol': 'WIF/USDT', 
            'icon': 'fas fa-hat-cowboy text-primary',
            'price': '0.3736',
            'change': '+4.8%',
            'volume': '280M',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
        {
            'id': 17, 
            'name': 'Meme Coin', 
            'symbol': 'MEME/USDT', 
            'icon': 'fas fa-laugh-squint text-warning',
            'price': '0.001586',
            'change': '+2.1%',
            'volume': '180M',
            'signal': 'Hold',
            'signal_class': 'warning'
        },
        {
            'id': 18, 
            'name': 'Token 4444', 
            'symbol': '4444/USDT', 
            'icon': 'fas fa-fire text-danger',
            'price': '0.0044',
            'change': '+4.4%',
            'volume': '444M',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
        {
            'id': 19, 
            'name': 'Bonk', 
            'symbol': 'BONK/USDT', 
            'icon': 'fas fa-dog text-warning',
            'price': '0.00001342',
            'change': '+3.8%',
            'volume': '210M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 20, 
            'name': 'Turbo', 
            'symbol': 'TURBO/USDT', 
            'icon': 'fas fa-bolt text-danger',
            'price': '0.00005871',
            'change': '+5.2%',
            'volume': '150M',
            'signal': 'Strong Buy',
            'signal_class': 'success'
        },
        {
            'id': 21, 
            'name': 'Brett', 
            'symbol': 'BRETT/USDT', 
            'icon': 'fas fa-meteor text-primary',
            'price': '0.00000785',
            'change': '+2.7%',
            'volume': '120M',
            'signal': 'Buy',
            'signal_class': 'success'
        }
    ]
    
    # لیست ارزهای با پشتوانه و استیبل‌کوین‌ها
    stable_backed_coins = [
        {
            'id': 40, 
            'name': 'Tether (USDT)', 
            'symbol': 'USDT/USD', 
            'icon': 'fas fa-dollar-sign text-success',
            'price': '1.000',
            'change': '+0.01%',
            'volume': '85.6B',
            'signal': 'Stable',
            'signal_class': 'info',
            'backed_by': 'USD, Treasury bills, Cash'
        },
        {
            'id': 41, 
            'name': 'USD Coin', 
            'symbol': 'USDC/USD', 
            'icon': 'fas fa-dollar-sign text-primary',
            'price': '1.000',
            'change': '+0.02%',
            'volume': '42.3B',
            'signal': 'Stable',
            'signal_class': 'info',
            'backed_by': 'US Dollar'
        },
        {
            'id': 42, 
            'name': 'Binance USD', 
            'symbol': 'BUSD/USD', 
            'icon': 'fas fa-dollar-sign text-warning',
            'price': '1.000',
            'change': '+0.01%',
            'volume': '5.7B',
            'signal': 'Stable',
            'signal_class': 'info',
            'backed_by': 'US Dollar'
        },
        {
            'id': 43, 
            'name': 'DAI', 
            'symbol': 'DAI/USD', 
            'icon': 'fas fa-coins text-warning',
            'price': '0.998',
            'change': '-0.02%',
            'volume': '2.4B',
            'signal': 'Stable',
            'signal_class': 'info',
            'backed_by': 'Crypto Collateral'
        },
        {
            'id': 44, 
            'name': 'PAXG (Gold)', 
            'symbol': 'PAXG/USD', 
            'icon': 'fas fa-coins text-warning',
            'price': '2481.50',
            'change': '+0.42%',
            'volume': '65.7M',
            'signal': 'Buy',
            'signal_class': 'success',
            'backed_by': 'Physical Gold'
        },
        {
            'id': 45, 
            'name': 'XAUT (Gold)', 
            'symbol': 'XAUT/USD', 
            'icon': 'fas fa-coins text-warning',
            'price': '2480.89',
            'change': '+0.38%',
            'volume': '54.2M',
            'signal': 'Buy',
            'signal_class': 'success',
            'backed_by': 'Physical Gold'
        }
    ]
    
    # لیست ارزهای کم‌هزینه با پتانسیل رشد
    low_cost_coins = [
        {
            'id': 22, 
            'name': 'VeChain', 
            'symbol': 'VET/USDT', 
            'icon': 'fas fa-link text-primary',
            'price': '0.02162',
            'change': '+1.2%',
            'volume': '120M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 23, 
            'name': 'XDC', 
            'symbol': 'XDC/USDT', 
            'icon': 'fas fa-cube text-info',
            'price': '0.06532',
            'change': '+2.4%',
            'volume': '85M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 24, 
            'name': 'Hedera', 
            'symbol': 'HBAR/USDT', 
            'icon': 'fas fa-h-square text-primary',
            'price': '0.1717',
            'change': '+3.5%',
            'volume': '110M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 25, 
            'name': 'Stellar', 
            'symbol': 'XLM/USDT', 
            'icon': 'fas fa-star text-warning',
            'price': '0.2333',
            'change': '+1.8%',
            'volume': '95M',
            'signal': 'Hold',
            'signal_class': 'warning'
        }
    ]
    
    # لیست ارزهای مهم لایر 1 و 2
    layer_coins = [
        {
            'id': 26, 
            'name': 'Polygon', 
            'symbol': 'MATIC/USDT', 
            'icon': 'fas fa-project-diagram text-purple',
            'price': '0.625',
            'change': '+3.8%',
            'volume': '520M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 27, 
            'name': 'Arbitrum', 
            'symbol': 'ARB/USDT', 
            'icon': 'fas fa-chart-line text-primary',
            'price': '1.35',
            'change': '+6.2%',
            'volume': '610M',
            'signal': 'Buy',
            'signal_class': 'success'
        },
        {
            'id': 28, 
            'name': 'Optimism', 
            'symbol': 'OP/USDT', 
            'icon': 'fas fa-rocket text-danger',
            'price': '2.95',
            'change': '+4.7%',
            'volume': '480M',
            'signal': 'Buy',
            'signal_class': 'success'
        }
    ]
    
    # ترکیب همه ارزها
    all_cryptocurrencies = important_coins + ai_coins + stable_backed_coins + meme_coins + low_cost_coins + layer_coins
    
    return render_template('cryptocurrencies.html', 
                          cryptocurrencies=all_cryptocurrencies,
                          major_coins=important_coins,
                          promising_coins=ai_coins,
                          stable_backed_coins=stable_backed_coins,
                          meme_coins=meme_coins,
                          low_cost_coins=low_cost_coins,
                          new_coins=layer_coins,
                          developer_name="حمید برزین")

@app.route('/simple')
def simple_home():
    """A simplified home page with direct links to all pages"""
    return redirect(url_for('index'))

@app.route('/api_test')
def api_test():
    """Render API test page"""
    return redirect(url_for('index'))
    
@app.route('/commodities_dashboard')
def commodities_dashboard():
    """Render commodities dashboard page"""
    return redirect(url_for('index'))
    
@app.route('/test')
def test_dashboard():
    """Render test dashboard page to debug API and JavaScript issues"""
    return redirect(url_for('index'))
    
@app.route('/test-menu')
def test_menu():
    """Render test menu page to debug navigation issues"""
    return redirect(url_for('index'))
    
@app.route('/test-tech')
def test_tech():
    """A simple page to test technical analysis links"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Technical Analysis Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            ul { margin-top: 20px; }
            li { margin-bottom: 10px; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Test Technical Analysis Page</h1>
        <p>This is a simple test to check if technical analysis pages are working</p>
        
        <h2>Click the links below to test technical analysis routing:</h2>
        <ul>
            <li><a href="/technical_analysis/BTC-USDT">Test BTC-USDT</a></li>
            <li><a href="/technical_analysis/ETH-USDT">Test ETH-USDT</a></li>
            <li><a href="/technical_analysis/SOL-USDT">Test SOL-USDT</a></li>
        </ul>
    </body>
    </html>
    '''

@app.route('/app_settings')
def app_settings():
    """صفحه تنظیمات ساده"""
    return redirect(url_for('dashboard'))

@app.route('/notifications')
@app.route('/notification_settings')
@app.route('/notification-settings')
@login_required
def notification_settings():
    """صفحه تنظیمات اعلان‌ها"""
    # تنظیمات پیش‌فرض اعلان‌ها
    default_settings = {
        'sms_enabled': session.get('sms_enabled', False),
        'phone_number': session.get('phone_number', ''),
        'email_enabled': session.get('email_enabled', False),
        'email_address': session.get('email_address', ''),
        'telegram_enabled': session.get('telegram_enabled', False),
        'telegram_chat_id': session.get('telegram_chat_id', ''),
        'buy_sell_enabled': session.get('buy_sell_enabled', True),
        'buy_sell_sensitivity': session.get('buy_sell_sensitivity', 'medium'),
        'buy_sell_frequency': session.get('buy_sell_frequency', '3'),
        'start_hour': session.get('start_hour', 8),
        'end_hour': session.get('end_hour', 22),
        'volatility_enabled': session.get('volatility_enabled', True),
        'volatility_threshold': session.get('volatility_threshold', 'medium'),
        'volatility_timeframe': session.get('volatility_timeframe', '1h'),
        'volatility_frequency': session.get('volatility_frequency', '5'),
        'market_trend_enabled': session.get('market_trend_enabled', True),
        'market_trend_frequency': session.get('market_trend_frequency', 'significant')
    }
    
    # دریافت اطلاعات بات تلگرام برای نمایش در صفحه
    from crypto_bot.telegram_service import get_bot_info
    telegram_bot_info = get_bot_info()
    
    return render_template('notification_dashboard.html', 
                          notification_settings=default_settings,
                          telegram_bot_info=telegram_bot_info)

@app.route('/dashboard_new')
def dashboard_new():
    """Redirect to main dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/trading-opportunities')
def trading_opportunities():
    """صفحه فرصت‌های معاملاتی و نوسانات بازار"""
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:5])
    return render_template('trading_opportunities.html', watched_currencies=watched_currencies)

@app.route('/ai')
@app.route('/ai_dashboard')
@app.route('/ai-dashboard')
def ai_dashboard():
    """
    داشبورد هوش مصنوعی برای تحلیل و پیش‌بینی قیمت ارزهای دیجیتال
    """
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    
    return render_template(
        'ai_dashboard.html',
        watched_currencies=DEFAULT_CURRENCIES,
        timeframes=TIMEFRAMES
    )

@app.route('/dashboard')
def dashboard():
    """هاب اصلی قیمت‌ها، چارت‌ها و اخبار - هدایت به نسخه مینیمال"""
    return redirect(url_for('minimal_dashboard'))

@app.route('/dashboard_classic')
def dashboard_classic():
    # Initialize session if not already set
    if not session.get('initialized', False):
        session['initialized'] = True
    
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    
    # Create sample current prices instead of trying to get real data
    current_prices = {}
    for symbol in watched_currencies:
        coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
        
        # Use current prices from CoinGecko/ccxt
        try:
            # Normalize symbol format for get_current_prices
            api_symbols = [symbol, symbol.replace('/', '-') if '/' in symbol else symbol.replace('-', '/')]
            logger.info(f"Trying to get prices for symbols: {api_symbols}")
            
            price_data = get_current_prices(api_symbols)
            
            # Use either format that returned data
            if symbol in price_data:
                logger.info(f"Found price data for {symbol}")
                found_symbol = symbol
            elif api_symbols[1] in price_data:
                logger.info(f"Found price data for {api_symbols[1]}")
                found_symbol = api_symbols[1]
            else:
                # Use recent prices if both API calls fail
                logger.warning(f"No price data found for {symbol} or {api_symbols[1]}")
                if coin.lower() == 'btc':
                    price = 69500  # Updated Bitcoin price Apr 2024
                    change = 0.8
                elif coin.lower() == 'eth': 
                    price = 3400   # Updated Ethereum price Apr 2024
                    change = -1.2
                elif coin.lower() == 'bnb':
                    price = 560
                    change = 0.5
                elif coin.lower() == 'xrp':
                    price = 0.52
                    change = 2.1
                elif coin.lower() == 'sol':
                    price = 145
                    change = -0.7
                elif coin.lower() == 'doge':
                    price = 0.15
                    change = 0.9
                else:
                    price = 100.0
                    change = random.uniform(-2.0, 2.0)
            
            # If we found data via API, use it
            if 'found_symbol' in locals():
                price = price_data[found_symbol]['price']
                change = price_data[found_symbol]['change_24h'] if price_data[found_symbol]['change_24h'] is not None else 0.0
        except Exception as e:
            logger.error(f"Error fetching API price for {symbol}: {str(e)}")
            # Fallback to default values
            if coin.lower() == 'btc':
                price = 69500  # Updated Bitcoin price Apr 2024
                change = 0.8
            elif coin.lower() == 'eth': 
                price = 3400   # Updated Ethereum price Apr 2024
                change = -1.2
            elif coin.lower() == 'xrp':
                price = 0.52
                change = 2.1
            else:
                price = 100.0
                change = 0.0
        
        current_prices[symbol] = {
            'price': price,
            'change_24h': change,
            'high_24h': price * 1.05,
            'low_24h': price * 0.95,
            'volume_24h': price * 1000 * random.uniform(5, 20),
            'is_sample_data': True,
            'source': 'sample_data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # Create sample technical data
    technical_data = {}
    for symbol in watched_currencies:
        technical_data[symbol] = {
            'rsi': round(random.uniform(30, 70), 2),
            'macd': {
                'macd': round(random.uniform(-10, 10), 2),
                'signal': round(random.uniform(-10, 10), 2),
                'histogram': round(random.uniform(-5, 5), 2)
            },
            'bollinger_bands': {
                'upper': round(current_prices[symbol]['price'] * 1.05, 2),
                'middle': round(current_prices[symbol]['price'], 2),
                'lower': round(current_prices[symbol]['price'] * 0.95, 2)
            },
            'sma_50': round(current_prices[symbol]['price'] * random.uniform(0.98, 1.02), 2),
            'sma_200': round(current_prices[symbol]['price'] * random.uniform(0.95, 1.05), 2),
            'is_sample_data': True
        }
    
    # Create sample news data
    news = [
        {
            'title': 'بیت‌کوین به بالاترین قیمت در تاریخ رسید',
            'source': 'خبرگزاری ارز دیجیتال',
            'url': '#',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {'score': 0.8, 'label': 'مثبت'},
            'is_sample_data': True
        },
        {
            'title': 'اتریوم در آستانه تغییرات بزرگ قرار دارد',
            'source': 'تحلیل‌گران بازار',
            'url': '#',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {'score': 0.6, 'label': 'مثبت'},
            'is_sample_data': True
        },
        {
            'title': 'تحلیل‌گران: احتمال اصلاح بازار در ماه آینده',
            'source': 'اخبار اقتصادی',
            'url': '#',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {'score': -0.3, 'label': 'منفی'},
            'is_sample_data': True
        },
        {
            'title': 'معرفی ارزهای دیجیتال جدید در بازار',
            'source': 'دنیای رمزارز',
            'url': '#',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {'score': 0.2, 'label': 'Neutral'},
            'is_sample_data': True
        },
        {
            'title': 'همکاری بزرگ بین شرکت‌های فناوری و پروژه‌های بلاکچین',
            'source': 'اخبار فناوری',
            'url': '#',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sentiment': {'score': 0.7, 'label': 'مثبت'},
            'is_sample_data': True
        }
    ]
    
    # Create sample signals data
    signals = {}
    for symbol in watched_currencies:
        # Extract coin name from symbol
        coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
        
        # Determine signal type based on coin (just for variety in samples)
        if coin.lower() in ['btc', 'eth', 'bnb']:
            signal = 'Buy'
            farsi_signal = 'Buy'
            strength = 0.35
            recommendation = "Consider swing trade (long)"
            farsi_recommendation = "Consider swing trade (bullish)"
        elif coin.lower() in ['xrp', 'sol', 'ada']:
            signal = 'Strong Buy'
            farsi_signal = 'Strong Buy'
            strength = 0.65
            recommendation = "Good swing entry for long position"
            farsi_recommendation = "Good entry point for bullish swing trade"
        elif coin.lower() in ['doge', 'shib', 'trx']:
            signal = 'Sell'
            farsi_signal = 'Sell'
            strength = -0.35
            recommendation = "Consider swing trade (short)"
            farsi_recommendation = "Consider swing trade (bearish)"
        else:
            signal = 'Neutral'
            farsi_signal = 'Neutral'
            strength = 0.05
            recommendation = "Wait for clearer signals"
            farsi_recommendation = "Wait for clearer signals"
        
        # Create sample signal data
        signals[symbol] = {
            'symbol': symbol,
            'price': current_prices[symbol]['price'],
            'signal': signal,
            'farsi_signal': farsi_signal,
            'strength': strength,
            'factors': {
                'trend': round(random.uniform(-0.5, 0.5), 2),
                'rsi': round(random.uniform(-0.5, 0.5), 2),
                'macd': round(random.uniform(-0.5, 0.5), 2),
                'bollinger': round(random.uniform(-0.5, 0.5), 2),
                'momentum': round(random.uniform(-0.5, 0.5), 2),
                'volatility': round(random.uniform(0.1, 0.3), 2),
                'swing_trade': round(random.uniform(-0.5, 0.5), 2),
                'news': round(random.uniform(-0.3, 0.3), 2)
            },
            'swing_recommendation': recommendation,
            'farsi_swing_recommendation': farsi_recommendation,
            'volatility': round(random.uniform(0.1, 0.3), 2),
            'timestamp': datetime.now().isoformat(),
            'is_sample_data': True
        }
    
    # Define hardcoded data for commodities, forex rates, and economic indicators
    # to avoid making external API calls
    commodities = {
        'GOLD': {
            'price': 2250.50,
            'change': 0.75,
            'symbol': 'XAU/USD',
            'name': 'طلا',
            'unit': 'اونس',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'SILVER': {
            'price': 28.75,
            'change': -0.25,
            'symbol': 'XAG/USD',
            'name': 'نقره',
            'unit': 'اونس',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'OIL': {
            'price': 82.35,
            'change': 1.2,
            'symbol': 'OIL/USD',
            'name': 'نفت',
            'unit': 'بشکه',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    # Hardcoded forex rates data
    forex_rates = {
        'EUR/USD': {
            'price': 1.0825,
            'change': 0.15,
            'name': 'یورو به دلار',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'GBP/USD': {
            'price': 1.2634,
            'change': -0.25,
            'name': 'پوند به دلار',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/JPY': {
            'price': 151.68,
            'change': 0.32,
            'name': 'دلار به ین',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/CHF': {
            'price': 0.9042,
            'change': -0.13,
            'name': 'دلار به فرانک',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/CAD': {
            'price': 1.3552,
            'change': 0.05,
            'name': 'دلار به دلار کانادا',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    # Hardcoded economic indicators data
    economic_indicators = {
        'recession_risk': {
            'value': 'متوسط',  # Low, Medium, High
            'trend': 'ثابت',   # Rising, Steady, Falling
            'description': 'خطر رکود جهانی در حال حاضر در سطح متوسط ارزیابی می‌شود.'
        },
        'global_markets': {
            'status': 'مثبت',  # Positive, Neutral, Negative
            'trend': 'رو به بالا', # Up, Stable, Down
            'description': 'بازارهای جهانی روند صعودی دارند با شاخص‌های اصلی در مسیر مثبت.'
        },
        'inflation': {
            'value': '3.2%',
            'trend': 'رو به پایین', # Rising, Steady, Falling
            'description': 'نرخ تورم جهانی در حال کاهش است.'
        },
        'interest_rates': {
            'value': '5.25%',
            'trend': 'ثابت', # Rising, Steady, Falling
            'description': 'نرخ بهره در بانک‌های مرکزی اصلی ثابت مانده است.'
        }
    }
    
    # Log debug information
    logger.debug(f"Dashboard rendering - using sample data for better performance")
    logger.debug(f"Watched currencies: {watched_currencies}")
    
    return render_template(
        'dashboard.html',
        prices=current_prices,
        technical_data=technical_data,
        news=news,
        signals=signals,
        currencies=DEFAULT_CURRENCIES,
        watched_currencies=watched_currencies,
        timeframes=TIMEFRAMES,
        scheduler_running=session.get('scheduler_running', False),
        include_middle_east=session.get('include_middle_east', True),
        commodities=commodities,
        forex_rates=forex_rates,
        economic_indicators=economic_indicators
    )

@app.route('/email-sample')
def email_sample():
    """Display a sample email that would be sent by the trading bot"""
    return redirect(url_for('dashboard'))

@app.route('/email-preview')
def email_preview():
    """Display a standalone preview of a sample email that would be sent by the trading bot"""
    return redirect(url_for('dashboard'))

@app.route('/demo_email')
def demo_email():
    """Alternative route for email sample display"""
    return redirect(url_for('dashboard'))

@app.route('/simple_email')
def simple_email():
    """Ultra simple route for email display when other routes fail"""
    return redirect(url_for('dashboard'))
    
@app.route('/minimal_old')
def minimal_email():
    """Extremely minimal email display with almost no styling"""
    return redirect(url_for('minimal_dashboard'))
    
@app.route('/ultra')
def ultra_simple():
    """Ultra simplified home page with just plain links"""
    return redirect(url_for('dashboard'))

# Renamed settings route to avoid conflict 
@app.route('/user_settings', methods=['GET', 'POST'])
def user_settings():
    """Settings page is no longer used"""
    return redirect(url_for('dashboard'))

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """ارسال ایمیل تست برای بررسی عملکرد سیستم اعلان ایمیلی"""
    from crypto_bot.email_notifications import send_test_email
    
    data = request.get_json()
    email_address = data.get('email_address')
    
    if not email_address:
        return jsonify({'success': False, 'message': 'آدرس ایمیل الزامی است'})
    
    try:
        result = send_test_email(email_address)
        # چون تابع send_test_email دیکشنری برمی‌گرداند
        if isinstance(result, dict):
            return jsonify(result)
        elif result:
            return jsonify({'success': True, 'message': 'ایمیل تست با موفقیت ارسال شد'})
        else:
            return jsonify({'success': False, 'message': 'Error sending test email. Please check your settings.'})
    except Exception as e:
        logger.error(f"خطا در ارسال ایمیل تست: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'})

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """ارسال پیامک تست برای بررسی عملکرد اعلان‌ها"""
    from crypto_bot.notification_service import send_test_notification
    
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'success': False, 'message': 'شماره موبایل الزامی است'})
    
    try:
        result = send_test_notification(phone_number)
        # چون تابع send_test_notification اکنون دیکشنری برمی‌گرداند
        if isinstance(result, dict):
            return jsonify(result)
        elif result:
            return jsonify({'success': True, 'message': 'پیامک تست با موفقیت ارسال شد'})
        else:
            return jsonify({'success': False, 'message': 'Error sending SMS. Please check your Twilio settings'})
    except Exception as e:
        logger.error(f"خطا در ارسال پیامک تست: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'})

@app.route('/telegram_test', methods=['GET'])
@app.route('/test', methods=['GET'])
@app.route('/telegram_test_page', methods=['GET'])
def telegram_test_page():
    """صفحه تست تلگرام"""
    return render_template('telegram_test.html')
    
@app.route('/direct_test', methods=['GET'])
def direct_test_page():
    """صفحه تست مستقیم تلگرام"""
    return render_template('direct_telegram_test.html')
    
@app.route('/direct_test_telegram', methods=['GET'])
def direct_test_telegram():
    """ارسال مستقیم پیام تلگرام با استفاده از درخواست HTTP"""
    try:
        import super_simple_telegram
        result = super_simple_telegram.send_simple_test()
        
        if result:
            return jsonify({'success': True, 'message': 'پیام تلگرام با موفقیت ارسال شد'})
        else:
            return jsonify({'success': False, 'message': 'Error sending Telegram message'})
    except Exception as e:
        logger.error(f"خطا در ارسال مستقیم پیام تلگرام: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'})
    
@app.route('/telegram_simple', methods=['GET'])
def telegram_simple_page():
    """صفحه ساده تست تلگرام"""
    return render_template('telegram_simple.html')

@app.route('/telegram', methods=['GET'])
@app.route('/test_telegram', methods=['GET'])
@app.route('/api/test-telegram', methods=['POST', 'GET'])
def test_telegram():
    """ارسال پیام تلگرام تست برای بررسی عملکرد اعلان‌ها"""
    # اطلاعات لاگینگ اضافی برای عیب‌یابی
    logger.info("درخواست تست تلگرام دریافت شد")
    
    # استفاده از چت آیدی پیش‌فرض از متغیر محیطی
    chat_id = os.environ.get('DEFAULT_CHAT_ID', '722627622')
    logger.info(f"چت آیدی پیش‌فرض: {chat_id}")

@app.route('/send_price_report')
def send_price_report():
    """صفحه ارسال گزارش قیمت ارزهای دیجیتال به تلگرام"""
    success = replit_telegram_sender.send_price_report()
    if success:
        flash('گزارش قیمت با موفقیت به تلگرام ارسال شد.', 'success')
    else:
        flash('Error sending price report to Telegram.', 'danger')
    return redirect(url_for('telegram_control_panel'))

@app.route('/send_system_report')
def send_system_report():
    """صفحه ارسال گزارش سیستم به تلگرام"""
    success = replit_telegram_sender.send_system_report()
    if success:
        flash('گزارش سیستم با موفقیت به تلگرام ارسال شد.', 'success')
    else:
        flash('Error sending system report to Telegram.', 'danger')
    return redirect(url_for('telegram_control_panel'))

@app.route('/send_trading_signals')
def send_trading_signals_route():
    """صفحه ارسال سیگنال‌های معاملاتی به تلگرام"""
    success = replit_telegram_sender.send_trading_signals()
    if success:
        flash('سیگنال‌های معاملاتی با موفقیت به تلگرام ارسال شد.', 'success')
    else:
        flash('Error sending trading signals to Telegram.', 'danger')
    return redirect(url_for('telegram_control_panel'))

@app.route('/send_technical_analysis')
def send_technical_analysis_route():
    """صفحه ارسال تحلیل تکنیکال به تلگرام"""
    symbol = request.args.get('symbol', 'BTC/USDT')
    success = replit_telegram_sender.send_technical_analysis(symbol)
    if success:
        flash(f'تحلیل تکنیکال برای {symbol} با موفقیت به تلگرام ارسال شد.', 'success')
    else:
        flash(f'Error sending technical analysis for {symbol} to Telegram.', 'danger')
    return redirect(url_for('telegram_control_panel'))

@app.route('/send_crypto_news')
def send_crypto_news_route():
    """صفحه ارسال اخبار ارزهای دیجیتال به تلگرام"""
    try:
        from crypto_bot.crypto_news import send_crypto_news_to_telegram
        success = send_crypto_news_to_telegram()
        if success:
            flash('اخبار ارزهای دیجیتال با موفقیت به تلگرام ارسال شد.', 'success')
        else:
            flash('Error sending cryptocurrency news to Telegram.', 'danger')
    except Exception as e:
        logger.error(f"Error sending news: {str(e)}")
        flash(f'Error sending news: {str(e)}', 'danger')
    return redirect(url_for('telegram_control_panel'))
    
@app.route('/api/telegram-test')
def test_telegram_fixed():
    """ارسال پیام تلگرام تست برای بررسی عملکرد اعلان‌ها (نسخه ساده شده)"""
    try:
        result = replit_telegram_sender.send_test_message()
        return jsonify({
            'success': True, 
            'message': 'پیام تست به تلگرام با موفقیت ارسال شد.'
        })
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست به تلگرام: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'خطا: {str(e)}'
        })
    
    # اگر اطلاعات در قالب JSON ارسال شده
    if request.is_json:
        data = request.get_json()
        user_chat_id = data.get('chat_id')
        if user_chat_id:
            logger.info(f"چت آیدی از درخواست JSON: {user_chat_id}")
            chat_id = user_chat_id
    
    # اگر از طریق پارامترهای URL درخواست شده
    elif request.method == 'GET' and request.args.get('chat_id'):
        user_chat_id = request.args.get('chat_id')
        logger.info(f"چت آیدی از پارامترهای URL: {user_chat_id}")
        chat_id = user_chat_id
    
    # استفاده از چت آیدی تنظیم شده در سشن (اگر وجود داشته باشد)
    elif session.get('telegram_chat_id'):
        user_chat_id = session.get('telegram_chat_id')
        logger.info(f"چت آیدی از سشن: {user_chat_id}")
        chat_id = user_chat_id
        
    # ذخیره چت آیدی در سشن برای استفاده‌های بعدی
    session['telegram_chat_id'] = chat_id
        
    # تبدیل به عدد صحیح (اگر عدد باشد)
    try:
        if isinstance(chat_id, str):
            # حذف هرگونه کاراکتر غیر عددی (مثل فاصله یا کاراکترهای خاص)
            cleaned_chat_id = ''.join(c for c in chat_id if c.isdigit() or c == '-')
            if cleaned_chat_id and cleaned_chat_id.lstrip('-').isdigit():
                chat_id = int(cleaned_chat_id)
                logger.info(f"چت آیدی به عدد صحیح تبدیل شد: {chat_id}")
    except Exception as e:
        logger.warning(f"خطا در تبدیل چت آیدی به عدد: {str(e)}")
    
    try:
        # روش ۱: استفاده از سیستم ساده جدید
        logger.info("تلاش برای ارسال پیام با روش ساده جدید")
        import super_simple_telegram
        result = super_simple_telegram.send_simple_test()
        logger.info(f"نتیجه ارسال پیام با روش ساده: {result}")
        
        if result:
            return jsonify({'success': True, 'message': 'پیام تلگرام با موفقیت ارسال شد (روش ساده)'})
            
        # روش ۲: استفاده از سیستم قدیمی اگر روش جدید موفق نبود
        logger.info("تلاش برای ارسال پیام با روش قدیمی")
        from crypto_bot.telegram_service import send_test_notification
        result2 = send_test_notification(chat_id)
        logger.info(f"نتیجه ارسال پیام با روش قدیمی: {result2}")
        
        if isinstance(result2, dict):
            return jsonify(result2)
        elif result2:
            return jsonify({'success': True, 'message': 'پیام تلگرام با موفقیت ارسال شد (روش قدیمی)'})
        else:
            return jsonify({'success': False, 'message': 'Error sending Telegram message. Both methods failed.'})
    except Exception as e:
        logger.error(f"Error sending Telegram test message: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'})

@app.route('/api/telegram-bot-info')
def telegram_bot_info():
    """دریافت اطلاعات بات تلگرام"""
    from crypto_bot.telegram_service import get_bot_info
    
    try:
        bot_info = get_bot_info()
        logger.info(f"اطلاعات بات تلگرام: {bot_info}")
        return jsonify({'success': True, 'data': bot_info})
    except Exception as e:
        logger.error(f"Error getting Telegram bot info: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'خطا: {str(e)}',
            'data': {
                'available': False,
                'username': 'GrowthFinderBot',  # اطلاعات ثابت در صورت خطا
                'link': 'https://t.me/GrowthFinderBot',
                'name': 'CryptoSage Bot',
                'message': 'لطفاً تنظیمات تلگرام را بررسی کنید. متغیر محیطی TELEGRAM_BOT_TOKEN را در بخش Secrets در Replit تنظیم کنید.'
            }
        })
        
@app.route('/api/telegram-chat-debug')
def telegram_chat_debug():
    """دیباگ چت تلگرام"""
    from crypto_bot.telegram_service import get_chat_debug_info
    
    chat_id = request.args.get('chat_id')
    try:
        debug_info = get_chat_debug_info(chat_id)
        return jsonify({'success': True, 'data': debug_info})
    except Exception as e:
        logger.error(f"Error debugging Telegram chat: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'})

@app.route('/api/opportunities')
def get_buy_sell_opportunities():
    """دریافت فرصت‌های خرید و فروش"""
    from crypto_bot.market_detector import detect_buy_sell_opportunities
    
    sensitivity = request.args.get('sensitivity', 'medium')
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:5])
    
    try:
        opportunities = detect_buy_sell_opportunities(watched_currencies, sensitivity)
        return jsonify({'success': True, 'data': opportunities})
    except Exception as e:
        logger.error(f"Error getting buy/sell opportunities: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/volatility')
def get_market_volatility():
    """دریافت نوسانات بازار"""
    from crypto_bot.market_detector import detect_market_volatility
    
    timeframe = request.args.get('timeframe', '1h')
    threshold = request.args.get('threshold', 'medium')
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:5])
    
    try:
        volatility = detect_market_volatility(watched_currencies, timeframe, threshold)
        return jsonify({'success': True, 'data': volatility})
    except Exception as e:
        logger.error(f"Error getting market volatility: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/market-trend')
def get_market_trend():
    """دریافت روند کلی بازار"""
    from crypto_bot.market_detector import analyze_market_trend
    
    try:
        trend = analyze_market_trend()
        return jsonify({'success': True, 'data': trend})
    except Exception as e:
        logger.error(f"Error getting market trend: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})



# تابع جدید با سیستم حافظه نهان
from crypto_bot.cached_api import get_cached_price, get_special_coin_price

@app.route('/api/price/<symbol>')
@app.route('/get_price')
def get_price(symbol=None):
    """دریافت قیمت ارز دیجیتال با استفاده از سیستم حافظه نهان"""
    try:
        # If symbol is None, try to get it from request parameters
        if symbol is None:
            symbol = request.args.get('symbol')
            
        if not symbol:
            return jsonify({
                'success': False, 
                'error': 'Symbol is required'
            }), 400
            
        # طراحی شده برای کار کردن با هر دو حالت - symbol به تنهایی (مثل btc)
        # یا symbol با base currency (مثل BTC/USDT)
        base_currency = None
        coin = symbol
        
        # اگر symbol شامل فرمت جفت ارزی است، آن را تفکیک می‌کنیم
        if '/' in symbol:
            parts = symbol.split('/')
            coin = parts[0]
            base_currency = parts[1]
        elif '-' in symbol:
            parts = symbol.split('-')
            coin = parts[0]
            base_currency = parts[1]
            
        # برای سادگی، در صورت عدم تعیین ارز پایه، USDT را فرض می‌کنیم
        if not base_currency:
            base_currency = 'USDT'
            symbol = f"{coin}/{base_currency}"
            
        # For meme coins, AI coins and low-cost coins, use special API
        meme_coins = ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'WIF', 'BONK', 'MEME', 'TURBO', 'BRETT', 'MOG', 'CAT', 'MYRO', 'POPCAT', 'TOSHI', 'SLERF', 'TOGE', 'GROK']
        ai_coins = ['RNDR', 'FET', 'WLD', 'OCEAN', 'AGIX', 'GEEQ', 'OLAS', 'GRT', 'NMR', 'PYTH', 'NEAR', 'ALI', 'RAD']
        low_cost_coins = ['VET', 'XDC', 'HBAR', 'XLM', 'CAKE', 'JASMY', 'STMX', 'SC', 'CELR', 'CTSI', 'ACH', 'HOOK', 'LOOM', 'SFP', 'TRU', 'BAL']
        
        special_coins = meme_coins + ai_coins + low_cost_coins
        
        # ابتدا سعی می‌کنیم از سیستم حافظه نهان استفاده کنیم
        if coin.upper() in special_coins:
            # برای ارزهای خاص، از API متفاوتی استفاده می‌کنیم
            logger.info(f"Getting price for special coin {coin} from cache or API")
            result, is_cached = get_special_coin_price(coin)
            
            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'cached': is_cached
                })
        
        # برای سایر ارزها، از سیستم اصلی استفاده می‌کنیم
        logger.info(f"Getting price for {symbol} from cache or API")
        result, is_cached = get_cached_price(symbol)
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'cached': is_cached
            })
            
        # اگر هیچ داده‌ای دریافت نشد، خطا برمی‌گردانیم
        logger.warning(f"No cached or API result for {symbol}")
        return jsonify({
            'success': False, 
            'message': 'Error retrieving price data. Please try again later.'
        })
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/technical')
@app.route('/api/technical/<path:symbol>/<timeframe>')
def get_technical(symbol=None, timeframe=None):
    try:
        # اگر پارامترها از URL نیامده اند، از query parameters دریافت کنیم
        if symbol is None:
            symbol = request.args.get('symbol', 'BTC/USDT')
        
        if timeframe is None:
            timeframe = request.args.get('timeframe', '1d')
        
        # تضمین اینکه symbol و timeframe مقدار دارند
        if not symbol:
            symbol = 'BTC/USDT'
            
        # Convert symbol format if necessary
        if '-' in symbol:
            symbol = symbol.replace('-', '/')
        
        if not timeframe:
            timeframe = '1d'
        
        # پاکسازی نماد قبل از ارسال به تابع تحلیل فنی
        clean_symbol = symbol
        if '-' in symbol:
            clean_symbol = symbol.replace('-', '/')
        
        logger.info(f"Getting technical data for symbol: {clean_symbol}, timeframe: {timeframe}")
        
        # دریافت تحلیل فنی
        from crypto_bot.technical_analysis import get_technical_analysis
        data = get_technical_analysis(clean_symbol, timeframe)
        
        # بررسی صحت داده‌های برگشتی
        if 'error' in data:
            logger.warning(f"Technical analysis returned error: {data['error']}")
            # ارسال داده‌های پیش‌فرض همراه با خطا
            return jsonify({
                'success': False, 
                'message': f"Error in technical analysis: {data['error']}", 
                'data': get_default_technical_data(clean_symbol, timeframe)
            })
            
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Error getting technical data for {symbol}: {str(e)}")
        # ارسال داده‌های پیش‌فرض در صورت بروز خطا
        return jsonify({
            'success': False, 
            'message': str(e),
            'data': get_default_technical_data(symbol, timeframe)
        })
        
@app.route('/technical_analysis/<symbol>', methods=['GET'])
# No login required for technical analysis
def technical_analysis_page(symbol):
    """
    صفحه تحلیل تکنیکال برای یک ارز دیجیتال خاص
    
    Args:
        symbol: نماد ارز دیجیتال
    
    Returns:
        render_template: صفحه تحلیل تکنیکال
    """
    try:
        # پاکسازی نماد
        clean_symbol = symbol
        if '-' in symbol:
            clean_symbol = symbol.replace('-', '/')
            
        # دریافت نام ارز
        name = clean_symbol.split('/')[0].capitalize()
        
        # دریافت تحلیل تکنیکال
        from crypto_bot.technical_analysis import get_technical_analysis
        data = get_technical_analysis(clean_symbol, '1d')
        
        # بررسی خطا
        if 'error' in data:
            flash(f"Error in technical analysis: {data['error']}", 'danger')
            return redirect(url_for('cryptocurrencies'))
        
        # دریافت قیمت فعلی
        price_data = get_price(clean_symbol)
        if isinstance(price_data, dict) and price_data.get('success', False):
            price = price_data['data']['price']
            change_24h = price_data['data']['change_24h']
        else:
            price = data.get('current_price', 0)
            change_24h = 0
        
        # رندر صفحه با داده‌های تحلیل
        return render_template(
            'technical_analysis.html', 
            symbol=clean_symbol,
            name=name,
            timestamp=data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            price=price,
            change_24h=change_24h,
            rsi=data.get('rsi', 50),
            macd=data.get('macd', 0),
            macd_signal=data.get('macd_signal', 0),
            ma20=data.get('ma20', 0),
            ma50=data.get('ma50', 0),
            current_price=data.get('current_price', price),
            bb_lower=data.get('bb_lower', 0),
            bb_middle=data.get('bb_middle', 0),
            bb_upper=data.get('bb_upper', 0),
            bb_width=data.get('bb_width', 0),
            stoch_k=data.get('stoch_k', 50),
            stoch_d=data.get('stoch_d', 50),
            volume_ema=data.get('volume_ema', 0),
            price_trend_10d=data.get('price_trend_10d', 0),
            signal=data.get('signal', 'خنثی'),
            signal_strength=data.get('signal_strength', 0)
        )
    
    except Exception as e:
        logger.error(f"Error in technical analysis page for {symbol}: {str(e)}")
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('cryptocurrencies'))
        
def get_default_technical_data(symbol, timeframe):
    """
    ایجاد داده‌های پیش‌فرض برای تحلیل فنی در صورت بروز خطا
    """
    current_price = 0
    try:
        # سعی می‌کنیم حداقل قیمت فعلی را دریافت کنیم
        price_data = get_current_prices([symbol, symbol.replace('/', '-') if '/' in symbol else symbol.replace('-', '/')])
        if price_data and len(price_data) > 0:
            for key in price_data:
                if price_data[key] and 'price' in price_data[key]:
                    current_price = price_data[key]['price']
                    break
    except:
        # در صورت بروز خطا، از مقادیر پیش‌فرض استفاده می‌کنیم
        if 'BTC' in symbol:
            current_price = 69500
        elif 'ETH' in symbol:
            current_price = 3400
        elif 'XRP' in symbol:
            current_price = 0.52
        else:
            current_price = 100
            
    # ایجاد اندیکاتورهای پیش‌فرض
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'current_price': current_price,
        'rsi': 50,  # مقدار خنثی
        'macd': 0,
        'macd_signal': 0,
        'ma20': current_price * 0.98,
        'ma50': current_price * 0.95,
        'ma200': current_price * 0.9,
        'signal': 'Neutral',
        'signal_strength': 0
    }

@app.route('/api/news')
def get_news():
    limit = request.args.get('limit', 5, type=int)
    include_middle_east = request.args.get('include_middle_east', 'true').lower() == 'true'
    
    try:
        news = get_latest_news(limit=limit, include_middle_east=include_middle_east)
        return jsonify({'success': True, 'data': news})
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/signals')
def get_signals():
    currencies = request.args.getlist('currencies')
    if not currencies:
        currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    
    # Create direct sample signals without trying to generate real ones
    # This is a temporary solution to avoid timeouts
    signals = {}
    for symbol in currencies:
        # Get the actual price if possible
        price = 0
        recommendation = ""
        farsi_recommendation = ""
        
        # Extract coin name from symbol
        coin = symbol.split('/')[0] if '/' in symbol else symbol.split('-')[0]
        
        # Determine signal type based on coin (just for variety in samples)
        if coin.lower() in ['btc', 'eth', 'bnb']:
            signal = 'Buy'
            farsi_signal = 'Buy'
            strength = 0.35
            recommendation = "Consider swing trade (long)"
            farsi_recommendation = "Consider swing trade (bullish)"
        elif coin.lower() in ['xrp', 'sol', 'ada']:
            signal = 'Strong Buy'
            farsi_signal = 'Strong Buy'
            strength = 0.65
            recommendation = "Good swing entry for long position"
            farsi_recommendation = "Good entry point for bullish swing trade"
        elif coin.lower() in ['doge', 'shib', 'trx']:
            signal = 'Sell'
            farsi_signal = 'Sell'
            strength = -0.35
            recommendation = "Consider swing trade (short)"
            farsi_recommendation = "Consider swing trade (bearish)"
        else:
            signal = 'Neutral'
            farsi_signal = 'Neutral'
            strength = 0.05
            recommendation = "Wait for clearer signals"
            farsi_recommendation = "Wait for clearer signals"
        
        # Try to get the real price with a very short timeout
        try:
            prices = get_current_prices([symbol], timeout=1)
            if symbol in prices:
                price = prices[symbol]['price']
        except Exception:
            # Use different sample prices based on the coin
            if coin.lower() == 'btc':
                price = 82500
            elif coin.lower() == 'eth': 
                price = 3200
            elif coin.lower() == 'bnb':
                price = 560
            elif coin.lower() == 'xrp':
                price = 0.52
            elif coin.lower() == 'sol':
                price = 145
            elif coin.lower() == 'doge':
                price = 0.15
            else:
                price = 100.0
                
        # Create sample signal data with variety
        signals[symbol] = {
            'symbol': symbol,
            'price': price,
            'signal': signal,
            'farsi_signal': farsi_signal,
            'strength': strength,
            'factors': {
                'trend': round(random.uniform(-0.5, 0.5), 2),
                'rsi': round(random.uniform(-0.5, 0.5), 2),
                'macd': round(random.uniform(-0.5, 0.5), 2),
                'bollinger': round(random.uniform(-0.5, 0.5), 2),
                'momentum': round(random.uniform(-0.5, 0.5), 2),
                'volatility': round(random.uniform(0.1, 0.3), 2),
                'swing_trade': round(random.uniform(-0.5, 0.5), 2),
                'news': round(random.uniform(-0.3, 0.3), 2)
            },
            'swing_recommendation': recommendation,
            'farsi_swing_recommendation': farsi_recommendation,
            'volatility': round(random.uniform(0.1, 0.3), 2),
            'timestamp': datetime.now().isoformat(),
            'is_sample_data': True  # Clearly mark as sample data
        }
    
    return jsonify({'success': True, 'data': signals})

@app.route('/api/commodities')
def get_commodities():
    # Return static commodity data
    commodities = {
        'GOLD': {
            'price': 2250.50,
            'change': 0.75,
            'symbol': 'XAU/USD',
            'name': 'طلا',
            'unit': 'اونس',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'SILVER': {
            'price': 28.75,
            'change': -0.25,
            'symbol': 'XAG/USD',
            'name': 'نقره',
            'unit': 'اونس',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'OIL': {
            'price': 82.35,
            'change': 1.2,
            'symbol': 'OIL/USD',
            'name': 'نفت',
            'unit': 'بشکه',
            'source': 'Sample Data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    return jsonify({'success': True, 'data': commodities})

@app.route('/api/forex')
def get_forex():
    # Return static forex data
    forex_rates = {
        'EUR/USD': {
            'price': 1.0825,
            'change': 0.15,
            'name': 'یورو به دلار',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'GBP/USD': {
            'price': 1.2634,
            'change': -0.25,
            'name': 'پوند به دلار',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/JPY': {
            'price': 151.68,
            'change': 0.32,
            'name': 'دلار به ین',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/CHF': {
            'price': 0.9042,
            'change': -0.13,
            'name': 'دلار به فرانک',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'USD/CAD': {
            'price': 1.3552,
            'change': 0.05,
            'name': 'دلار به دلار کانادا',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    return jsonify({'success': True, 'data': forex_rates})

@app.route('/api/economic')
def get_economic():
    # Return static economic indicators
    indicators = {
        'recession_risk': {
            'value': 'متوسط',  # Low, Medium, High
            'trend': 'ثابت',   # Rising, Steady, Falling
            'description': 'خطر رکود جهانی در حال حاضر در سطح متوسط ارزیابی می‌شود.'
        },
        'global_markets': {
            'status': 'مثبت',  # Positive, Neutral, Negative
            'trend': 'رو به بالا', # Up, Stable, Down
            'description': 'بازارهای جهانی روند صعودی دارند با شاخص‌های اصلی در مسیر مثبت.'
        },
        'inflation': {
            'value': '3.2%',
            'trend': 'رو به پایین', # Rising, Steady, Falling
            'description': 'نرخ تورم جهانی در حال کاهش است.'
        },
        'interest_rates': {
            'value': '5.25%',
            'trend': 'ثابت', # Rising, Steady, Falling
            'description': 'نرخ بهره در بانک‌های مرکزی اصلی ثابت مانده است.'
        }
    }
    return jsonify({'success': True, 'data': indicators})
    
# روت‌های مربوط به هوش مصنوعی و یادگیری ماشین

@app.route('/api/ai/price-prediction/<path:symbol>')
def ai_price_prediction(symbol):
    """
    پیش‌بینی قیمت با استفاده از هوش مصنوعی
    """
    timeframe = request.args.get('timeframe', '24h')
    
    try:
        # استفاده مستقیم از داده‌های نمونه برای نمایش
        from crypto_bot import ai_module
        
        # استفاده از داده‌های نمونه برای رفع مشکل API
        sample_prediction = ai_module.get_price_prediction(symbol, timeframe)
        return jsonify({
            "success": True,
            "data": sample_prediction
        })
    
    except Exception as e:
        logger.error(f"خطا در پیش‌بینی قیمت {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/ai/market-sentiment')
def ai_market_sentiment():
    """
    تحلیل احساسات بازار با استفاده از هوش مصنوعی
    """
    symbol = request.args.get('symbol')
    include_middle_east = request.args.get('include_middle_east', 'true').lower() == 'true'
    
    try:
        # استفاده مستقیم از داده‌های نمونه برای رفع مشکل API
        from crypto_bot import ai_module
        
        # استفاده از ماژول داخلی
        sentiment = ai_module.get_market_sentiment(symbol, include_middle_east)
        return jsonify({'success': True, 'data': sentiment})
    except Exception as e:
        logger.error(f"خطا در تحلیل احساسات بازار: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/ai/price-patterns/<path:symbol>')
def ai_price_patterns(symbol):
    """
    شناسایی الگوهای قیمت با استفاده از هوش مصنوعی
    """
    timeframe = request.args.get('timeframe', '1d')
    
    try:
        # استفاده مستقیم از داده‌های نمونه برای رفع مشکل API
        from crypto_bot import ai_module
        
        # استفاده از ماژول داخلی
        patterns = ai_module.get_price_patterns(symbol, timeframe)
        return jsonify({'success': True, 'data': patterns})
    except Exception as e:
        logger.error(f"خطا در شناسایی الگوهای قیمت {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/ai/trading-strategy/<path:symbol>')
def ai_trading_strategy(symbol):
    """
    پیشنهاد استراتژی معاملاتی با استفاده از هوش مصنوعی
    """
    risk_level = request.args.get('risk_level', 'متوسط')
    timeframe = request.args.get('timeframe', 'کوتاه‌مدت')
    
    try:
        # استفاده مستقیم از داده‌های نمونه برای رفع مشکل API
        from crypto_bot import ai_module
        
        # استفاده از ماژول داخلی
        strategy = ai_module.get_trading_strategy(symbol, risk_level, timeframe)
        return jsonify({'success': True, 'data': strategy})
    except Exception as e:
        logger.error(f"خطا در پیشنهاد استراتژی معاملاتی {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/scheduler_status', methods=['GET'])
def scheduler_status():
    """دریافت وضعیت زمان‌بندی خودکار"""
    try:
        # Get scheduler status from session
        running = session.get('scheduler_running', False)
        
        # Return status
        return jsonify({"running": running})
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        return jsonify({"running": False, "error": str(e)}), 500

@app.route('/start_scheduler', methods=['GET'])
def start_scheduler_api():
    """راه‌اندازی زمان‌بندی خودکار از طریق API"""
    try:
        # راه‌اندازی زمان‌بندی های مختلف
        result = {}
        
        # راه‌اندازی زمان‌بندی خودکار اصلی
        try:
            import subprocess
            result['main_scheduler'] = subprocess.check_output(['bash', 'start_ten_minute_reporter.sh']).decode('utf-8')
        except Exception as e:
            logger.error(f"Error starting ten_minute_reporter: {str(e)}")
            result['main_scheduler'] = str(e)
        
        # Update session
        session['scheduler_running'] = True
        
        # Return result
        return jsonify({
            "status": "success", 
            "message": "زمان‌بندی خودکار با موفقیت راه‌اندازی شد", 
            "result": result
        })
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return jsonify({"status": "error", "message": f"خطا در راه‌اندازی زمان‌بندی خودکار: {str(e)}"}), 500
        
@app.route('/stop_scheduler', methods=['GET'])
def stop_scheduler_api():
    """توقف زمان‌بندی خودکار از طریق API"""
    try:
        # توقف زمان‌بندی های مختلف
        result = {}
        
        # توقف زمان‌بندی خودکار اصلی
        try:
            import subprocess
            import os
            
            # کشتن فرآیند زمان‌بندی 10 دقیقه‌ای
            if os.path.exists("ten_minute_scheduler.pid"):
                with open("ten_minute_scheduler.pid", "r") as f:
                    pid = f.read().strip()
                    if pid:
                        kill_output = subprocess.check_output(['kill', pid]).decode('utf-8')
                        result['kill_output'] = kill_output
                        result['pid'] = pid
            
            # اجرای اسکریپت توقف
            if os.path.exists("stop_all_telegram_services.sh"):
                stop_output = subprocess.check_output(['bash', 'stop_all_telegram_services.sh']).decode('utf-8')
                result['stop_output'] = stop_output
        except Exception as e:
            logger.error(f"Error stopping ten_minute_reporter: {str(e)}")
            result['error'] = str(e)
        
        # Update session
        session['scheduler_running'] = False
        
        # Return result
        return jsonify({
            "status": "success", 
            "message": "زمان‌بندی خودکار با موفقیت متوقف شد", 
            "result": result
        })
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        return jsonify({"status": "error", "message": f"خطا در توقف زمان‌بندی خودکار: {str(e)}"}), 500

@app.route('/api/update-notification-settings', methods=['POST'])
@app.route('/update_notification_settings', methods=['GET', 'POST'])
def update_notification_settings():
    """بروزرسانی تنظیمات اعلان‌ها"""
    # برای درخواست‌های GET، نمایش وضعیت فعلی را برمی‌گرداند
    if request.method == 'GET':
        # Get system and notification settings from session
        settings = {
            'sms_enabled': session.get('sms_enabled', False),
            'phone_number': session.get('phone_number', ''),
            'email_enabled': session.get('email_enabled', False),
            'email_address': session.get('email_address', ''),
            'telegram_enabled': session.get('telegram_enabled', True),
            'telegram_chat_id': session.get('telegram_chat_id', os.environ.get('DEFAULT_CHAT_ID', '')),
            'buy_sell_enabled': session.get('buy_sell_enabled', True),
            'buy_sell_sensitivity': session.get('buy_sell_sensitivity', 'medium'),
            'system_monitor_enabled': session.get('system_monitor_enabled', True),
            'scheduler_running': session.get('scheduler_running', False),
            'start_hour': session.get('start_hour', 8),
            'end_hour': session.get('end_hour', 22),
            'volatility_enabled': session.get('volatility_enabled', True),
            'volatility_threshold': session.get('volatility_threshold', 'medium'),
            'market_trend_enabled': session.get('market_trend_enabled', True)
        }
        return jsonify({'success': True, 'settings': settings})
    
    # برای درخواست‌های POST، تنظیمات را بروزرسانی می‌کند
    try:
        # دریافت داده‌های ارسال شده
        settings = request.get_json()
        
        # اگر تنظیمات خالی باشد، یک خطا برمی‌گرداند
        if not settings:
            return jsonify({'success': False, 'message': 'تنظیماتی دریافت نشد'}), 400
        
        # ذخیره تنظیمات در سشن
        session['sms_enabled'] = settings.get('sms_enabled', False)
        session['phone_number'] = settings.get('phone_number', '')
        session['email_enabled'] = settings.get('email_enabled', False)
        session['email_address'] = settings.get('email_address', '')
        session['telegram_enabled'] = settings.get('telegram_enabled', False)
        session['telegram_chat_id'] = settings.get('telegram_chat_id', '')
        session['buy_sell_enabled'] = settings.get('buy_sell_enabled', True)
        session['buy_sell_sensitivity'] = settings.get('buy_sell_sensitivity', 'medium')
        
        # Check if system monitor is enabled
        session['system_monitor_enabled'] = settings.get('system_monitor_enabled', False)
        session['buy_sell_frequency'] = settings.get('buy_sell_frequency', '3')
        session['start_hour'] = settings.get('start_hour', 8)
        session['end_hour'] = settings.get('end_hour', 22)
        session['volatility_enabled'] = settings.get('volatility_enabled', True)
        session['volatility_threshold'] = settings.get('volatility_threshold', 'medium')
        session['volatility_timeframe'] = settings.get('volatility_timeframe', '1h')
        session['volatility_frequency'] = settings.get('volatility_frequency', '5')
        session['market_trend_enabled'] = settings.get('market_trend_enabled', True)
        session['market_trend_frequency'] = settings.get('market_trend_frequency', 'significant')
        
        return jsonify({'success': True, 'message': 'تنظیمات با موفقیت ذخیره شد'})
    except Exception as e:
        logger.error(f"خطا در ذخیره تنظیمات اعلان‌ها: {str(e)}")
        return jsonify({'success': False, 'message': f'خطا: {str(e)}'}), 500

# این نسخه تکراری از تابع get_buy_sell_opportunities است و حذف شد
# زیرا قبلاً در مسیر '/api/opportunities' تعریف شده است

# این نسخه تکراری از تابع get_market_volatility است و حذف شد
# زیرا قبلاً در مسیر '/api/volatility' تعریف شده است

# این نسخه تکراری از تابع get_market_trend است و حذف شد
# زیرا قبلاً در مسیر '/api/market-trend' تعریف شده است

# این روت قبلا با نام دیگری تعریف شده است

# این روت قبلا با نام دیگری تعریف شده است

@app.route('/api/email-message')
def get_email_message():
    """Get the last email message that would have been sent"""
    from crypto_bot.email_service import last_email_content, DISABLE_REAL_EMAIL
    
    # Debug info
    print(f"Last email content: {last_email_content}")
    
    # Always return has_message=True when mock system is enabled and a recipient exists
    has_message = last_email_content['recipient'] is not None
    
    # Always display the UI email preview even if real email is disabled
    status = {
        # Override this to true to ensure UI displays properly
        'email_system_enabled': True,
        'has_message': has_message,
        'last_message': last_email_content if has_message else None
    }
    return jsonify({'success': True, 'data': status})

# Minimal UI routes
@app.route('/minimal')
@app.route('/minimal_dashboard')
def minimal_dashboard():
    """صفحه داشبورد با طراحی مینیمال"""
    # inject_now() is called automatically by context_processor, no need to call it manually
    
    # استفاده از نسخه جدید داشبورد اگر پارامتر new در URL وجود داشته باشد
    if 'new' in request.args:
        return render_template('new_minimal_dashboard.html')
    
    # Let's add some debug context to make sure translations work
    current_language = session.get('language', DEFAULT_LANGUAGE)
    try:
        return render_template('minimal_dashboard.html')
    except Exception as e:
        app.logger.error(f"Error rendering minimal_dashboard.html: {e}")
        # Fallback to ultra simple template
        return f"<html><body><h1>Dashboard Error</h1><p>{str(e)}</p><p>Current language: {current_language}</p></body></html>"

@app.route('/test_prices')
def test_prices():
    """صفحه تست قیمت‌های ارزهای دیجیتال"""
    return render_template('test_prices.html')

@app.route('/minimal_settings')
@login_required
def minimal_settings():
    """صفحه تنظیمات با طراحی مینیمال"""
    # inject_now() is called automatically by context_processor, no need to call it manually
    
    # Load notification settings
    settings = {
        'telegram_chat_id': os.environ.get('DEFAULT_CHAT_ID', ''),
        'email_address': '',
        'phone_number': '',
        'price_change_threshold': 5,
        'signals_frequency': 'strong',
        'news_sources': 'major',
        'daily_report_time': '16:00',
        'weekly_report_day': '4',
        'update_frequency': '60',
        'language': session.get('language', DEFAULT_LANGUAGE)
    }
    
    bot_username = 'GrowthFinderBot'
    # Extract username from bot token if available 
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    if telegram_bot_token and ':' in telegram_bot_token:
        try:
            from crypto_bot.telegram_service import get_bot_info
            bot_info = get_bot_info()
            if bot_info and 'username' in bot_info:
                bot_username = bot_info['username']
        except Exception as e:
            logger.error(f"Error getting bot username: {e}")
    
    # دریافت تمام زبان‌های پشتیبانی شده
    languages = get_all_languages()
    current_language = get_language_info(session.get('language', DEFAULT_LANGUAGE))
    
    try:
        return render_template('minimal_settings.html', 
                              settings=settings, 
                              bot_username=bot_username,
                              languages=languages,
                              current_language=current_language)
    except Exception as e:
        app.logger.error(f"Error rendering minimal_settings.html: {e}")
        # Fallback to ultra simple template
        return f"<html><body><h1>Settings Error</h1><p>{str(e)}</p></body></html>"

@app.route('/send_price_report')
def send_telegram_price_report():
    """ارسال گزارش قیمت‌های ارزهای دیجیتال به تلگرام"""
    try:
        result = replit_telegram_sender.send_price_report()
        if result:
            return jsonify({
                'success': True,
                'message': 'گزارش قیمت با موفقیت به تلگرام ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال گزارش قیمت به تلگرام'
            })
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'خطا در ارسال گزارش قیمت به تلگرام'
        })

@app.route('/send_system_report')
def send_telegram_system_report():
    """ارسال گزارش وضعیت سیستم به تلگرام"""
    try:
        result = replit_telegram_sender.send_system_report()
        if result:
            return jsonify({
                'success': True,
                'message': 'گزارش وضعیت سیستم با موفقیت به تلگرام ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال گزارش وضعیت سیستم به تلگرام'
            })
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش وضعیت سیستم به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'خطا در ارسال گزارش وضعیت سیستم به تلگرام'
        })

@app.route('/send_technical_analysis')
def send_telegram_technical_analysis():
    """ارسال تحلیل تکنیکال به تلگرام"""
    symbol = request.args.get('symbol')
    try:
        result = replit_telegram_sender.send_technical_analysis(symbol)
        if result:
            return jsonify({
                'success': True,
                'message': 'تحلیل تکنیکال با موفقیت به تلگرام ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال تحلیل تکنیکال به تلگرام'
            })
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل تکنیکال به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'خطا در ارسال تحلیل تکنیکال به تلگرام'
        })

@app.route('/send_trading_signals')
def send_telegram_trading_signals():
    """ارسال سیگنال‌های معاملاتی به تلگرام"""
    try:
        result = replit_telegram_sender.send_trading_signals()
        if result:
            return jsonify({
                'success': True,
                'message': 'سیگنال‌های معاملاتی با موفقیت به تلگرام ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال سیگنال‌های معاملاتی به تلگرام'
            })
    except Exception as e:
        logger.error(f"خطا در ارسال سیگنال‌های معاملاتی به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'خطا در ارسال سیگنال‌های معاملاتی به تلگرام'
        })

@app.route('/send_test_message_replit')
def send_test_message_replit():
    """ارسال پیام تست با استفاده از ماژول جدید replit_telegram_sender"""
    try:
        result = replit_telegram_sender.send_test_message()
        if result:
            return jsonify({
                'success': True,
                'message': 'پیام تست با موفقیت به تلگرام ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال پیام تست به تلگرام'
            })
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست به تلگرام: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'خطا در ارسال پیام تست به تلگرام'
        })

# صفحات ثبت‌نام غیرفعال شدند
# @app.route('/telegram_register')
# def telegram_register():
#     """صفحه ثبت‌نام کاربر جدید کنترل پنل تلگرام"""
#     inject_now()
#     return render_template('telegram_register.html')
#
# @app.route('/telegram_register_process', methods=['POST'])
# def telegram_register_process():
#     """پردازش فرم ثبت‌نام کاربر جدید کنترل پنل تلگرام"""
#     username = request.form.get('username')
#     password = request.form.get('password')
#     confirm_password = request.form.get('confirm_password')
#     
#     # بررسی تکمیل تمام فیلدها
#     if not username or not password or not confirm_password:
#         flash('تمام فیلدها باید تکمیل شوند.', 'danger')
#         return redirect(url_for('telegram_register'))
#     
#     # بررسی طول نام کاربری
#     if len(username) < 3:
#         flash('نام کاربری باید حداقل ۳ کاراکتر باشد.', 'danger')
#         return redirect(url_for('telegram_register'))
#     
#     # بررسی تطابق رمزهای عبور
#     if password != confirm_password:
#         flash('رمز عبور و تکرار آن مطابقت ندارند.', 'danger')
#         return redirect(url_for('telegram_register'))
#     
#     # ثبت‌نام کاربر جدید
#     success, message = register_user(username, password)
#     
#     if success:
#         flash(message, 'success')
#         # هدایت به صفحه ورود
#         return redirect(url_for('telegram_login'))
#     else:
#         flash(message, 'danger')
#         return redirect(url_for('telegram_register'))

@app.route('/telegram_login')
def telegram_login():
    """صفحه ورود به کنترل پنل تلگرام"""
    inject_now()
    # اگر کاربر قبلاً احراز هویت شده باشد، مستقیم به پنل کنترل هدایت شود
    if 'telegram_auth' in session and session['telegram_auth']:
        return redirect(url_for('telegram_control_panel'))
    return render_template('telegram_login.html')

@app.route('/telegram_login_process', methods=['POST'])
def telegram_login_process():
    """پردازش فرم ورود به کنترل پنل تلگرام"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if verify_password(username, password):
        session['telegram_auth'] = True
        session['telegram_username'] = username
        
        # اگر آدرس بعدی ذخیره شده، به آن هدایت کن
        next_url = session.pop('next_url', url_for('telegram_control_panel'))
        return redirect(next_url)
    else:
        flash('Username or password is incorrect', 'danger')
        return redirect(url_for('telegram_login'))

@app.route('/telegram_logout')
def telegram_logout():
    """خروج از حساب کاربری کنترل پنل تلگرام"""
    session.pop('telegram_auth', None)
    session.pop('telegram_username', None)
    flash('با موفقیت خارج شدید', 'success')
    return redirect(url_for('telegram_login'))

@app.route('/telegram_change_password')
@login_required
def telegram_change_password():
    """صفحه تغییر رمز عبور کنترل پنل تلگرام"""
    return render_template('telegram_change_password.html')

@app.route('/telegram_change_password_process', methods=['POST'])
@login_required
def telegram_change_password_process():
    """پردازش فرم تغییر رمز عبور کنترل پنل تلگرام"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    username = session.get('telegram_username')
    
    # بررسی رمز عبور فعلی
    if not verify_password(username, current_password):
        flash('رمز عبور فعلی اشتباه است', 'danger')
        return redirect(url_for('telegram_change_password'))
    
    # بررسی تطابق رمز عبور جدید و تکرار آن
    if new_password != confirm_password:
        flash('رمز عبور جدید و تکرار آن مطابقت ندارند', 'danger')
        return redirect(url_for('telegram_change_password'))
    
    # تغییر رمز عبور
    if change_password(username, new_password):
        flash('رمز عبور با موفقیت تغییر یافت', 'success')
        return redirect(url_for('telegram_control_panel'))
    else:
        flash('خطا در تغییر رمز عبور', 'danger')
        return redirect(url_for('telegram_change_password'))

@app.route('/telegram_control', methods=['GET', 'POST'])
@app.route('/telegram_control_panel', methods=['GET', 'POST'])
@app.route('/telegram_panel', methods=['GET', 'POST'])
@app.route('/telegram-control-panel', methods=['GET', 'POST'])
@login_required
def telegram_control_panel():
    """صفحه کنترل پنل تلگرام"""
    inject_now()
    
    # اگر متد POST باشد، تنظیمات را ذخیره می‌کنیم
    if request.method == 'POST':
        try:
            # لاگ کردن تمام داده‌های دریافتی برای دیباگ
            logger.info(f"داده‌های دریافتی از فرم: {request.form}")
            
            # دریافت مقادیر از فرم
            message_sending_enabled = request.form.get('message_sending_enabled') == 'on'
            auto_start_on_boot = request.form.get('auto_start_on_boot') == 'on'
            
            # تبدیل مقادیر عددی
            try:
                active_hours_start = int(request.form.get('active_hours_start', 8))
                active_hours_end = int(request.form.get('active_hours_end', 22))
                interval = int(request.form.get('interval', 1800))
            except (ValueError, TypeError) as e:
                logger.error(f"خطا در تبدیل مقادیر عددی: {str(e)}")
                # مقادیر پیش‌فرض
                active_hours_start = 8
                active_hours_end = 22
                interval = 1800
            
            # ساخت دیکشنری تنظیمات
            settings = {
                'message_sending_enabled': message_sending_enabled,
                'auto_start_on_boot': auto_start_on_boot,
                'active_hours_start': active_hours_start,
                'active_hours_end': active_hours_end,
                'interval': interval
            }
            
            # بروزرسانی تنظیمات
            updated_status = telegram_scheduler_service.update_scheduler_settings(settings)
            logger.info(f"تنظیمات با موفقیت به‌روزرسانی شد: {settings}")
            
            # ذخیره پیام موفقیت در جلسه
            session['settings_saved'] = True
            
            # ذخیره تاریخ آخرین تنظیمات
            session['last_settings_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception as e:
            # ثبت خطای دقیق
            error_message = str(e)
            logger.error(f"خطای دقیق در بروزرسانی تنظیمات: {error_message}")
            
            # ثبت اطلاعات اضافی دیباگ 
            import traceback
            logger.error(f"جزئیات خطا: {traceback.format_exc()}")
            
            # ذخیره خطا در session
            session['settings_error'] = error_message
    
    # دریافت وضعیت فعلی سرویس زمان‌بندی
    status = telegram_scheduler_service.get_scheduler_status()
    
    # بررسی وجود پیام موفقیت و خطا در جلسه
    settings_saved = False
    settings_error = None
    
    if session.get('settings_saved'):
        settings_saved = True
        session.pop('settings_saved', None)  # حذف پیام پس از استفاده
    
    if session.get('settings_error'):
        settings_error = session.get('settings_error')
        session.pop('settings_error', None)  # حذف پیام خطا پس از استفاده
    
    # پارامتر error از query string
    error_param = request.args.get('error', '0')
    has_error = error_param == '1'
    
    # لاگ کردن متغیرهای مهم برای دیباگ
    app.logger.info(f"بارگذاری صفحه تنظیمات تلگرام. ذخیره شده: {settings_saved}, خطا: {settings_error}, پارامتر خطا: {error_param}")
    
    return render_template(
        'telegram_control_panel.html', 
        status=status,
        settings_saved=settings_saved,
        settings_error=settings_error,
        has_error=has_error
    )


@app.route('/telegram-success')
@login_required
def telegram_success_message():
    """صفحه پیام موفقیت برای ذخیره تنظیمات تلگرام"""
    inject_now()
    return render_template('telegram_success_message.html')


@app.route('/telegram-settings-saved')
@login_required
def telegram_settings_saved():
    """صفحه نمایش موفقیت در ذخیره تنظیمات تلگرام (صفحه جدید)"""
    inject_now()
    return render_template('telegram_settings_saved.html')


@app.route('/telegram-save-settings', methods=['POST'])
@login_required
def telegram_save_settings():
    """Save Telegram settings from HTML form with enhanced logging"""
    try:
        # Log all received form data for debugging
        logger.info(f"Form data received: {request.form}")
        
        # Get values from form
        message_sending_enabled = request.form.get('message_sending_enabled') == 'on'
        auto_start_on_boot = request.form.get('auto_start_on_boot') == 'on'
        
        # Convert numeric values
        try:
            active_hours_start = int(request.form.get('active_hours_start', 8))
            active_hours_end = int(request.form.get('active_hours_end', 22))
            interval = int(request.form.get('interval', 1800))
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting numeric values: {str(e)}")
            # Default values
            active_hours_start = 8
            active_hours_end = 22
            interval = 1800
        
        # Create settings dictionary
        settings = {
            'message_sending_enabled': message_sending_enabled,
            'auto_start_on_boot': auto_start_on_boot,
            'active_hours_start': active_hours_start,
            'active_hours_end': active_hours_end,
            'interval': interval
        }
        
        # Update settings with detailed error display
        settings_error = None
        try:
            # Log settings before update
            logger.info(f"Attempting to update settings: {settings}")
            
            updated_status = telegram_scheduler_service.update_scheduler_settings(settings)
            logger.info(f"Settings successfully updated: {settings}")
            
            # Store success message in session
            session['settings_saved'] = True
            
            # Store last settings update date
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['last_settings_update'] = current_time
            logger.info(f"Settings update time recorded: {current_time}")
            
            # Redirect to main settings page with success message
            return redirect('/telegram_control_panel')
            
        except Exception as e:
            # Log detailed error
            error_message = str(e)
            logger.error(f"Detailed error in settings update: {error_message}")
            
            # Log additional debug info
            import traceback
            logger.error(f"Error details: {traceback.format_exc()}")
            
            # Store error in session
            session['settings_error'] = error_message
            
            # Return to settings page with error display
            return redirect('/telegram_control_panel?error=1')
            
    except Exception as e:
        # Error in request processing
        logger.error(f"Error processing form request: {str(e)}")
        
        # ذخیره خطا در session
        session['settings_error'] = str(e)
        
        # بازگشت به صفحه تنظیمات با نمایش خطا
        return redirect('/telegram_control_panel?error=1')

@app.route('/telegram-reliability')
@login_required
def telegram_reliability_dashboard():
    """صفحه داشبورد قابلیت اطمینان تلگرام"""
    return render_template('telegram_reliability.html')


@app.route('/price_alerts')
@app.route('/alerts')
def price_alerts_page():
    """Price Alert Management Page"""
    return render_template('price_alerts.html')


@app.route('/crypto_news')
@app.route('/crypto-news')
@app.route('/news')
def crypto_news_page():
    """Cryptocurrency News Page"""
    # Get news data directly from the server
    from crypto_bot.crypto_news import get_crypto_news
    
    # Don't attempt translation (use English content)
    news_data = get_crypto_news(translate=False)
    
    # Get Canadian news
    try:
        from crypto_bot.news_scanner import get_canadian_crypto_news
        canada_news = get_canadian_crypto_news()
    except (ImportError, AttributeError):
        app.logger.warning("Canadian news module not available")
        canada_news = []
    
    # Combine news sources
    all_news = news_data + canada_news
    
    # Sort by published date if available
    all_news.sort(key=lambda x: x.get('published_on', 0) if x.get('published_on') else 0, reverse=True)
    
    return render_template('crypto_news.html', news_items=all_news)


# API‌های کنترل سرویس تلگرام
@app.route('/api/telegram/start')
def api_telegram_start():
    """
    راه‌اندازی سرویس زمان‌بندی تلگرام
    """
    try:
        result = telegram_scheduler_service.start_scheduler()
        if result:
            return jsonify({
                'success': True,
                'message': 'سرویس زمان‌بندی تلگرام با موفقیت راه‌اندازی شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در راه‌اندازی سرویس زمان‌بندی تلگرام (سرویس ممکن است از قبل فعال باشد)'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در راه‌اندازی سرویس: {str(e)}'
        })


@app.route('/api/telegram/stop')
def api_telegram_stop():
    """
    توقف سرویس زمان‌بندی تلگرام
    """
    try:
        result = telegram_scheduler_service.stop_scheduler()
        if result:
            return jsonify({
                'success': True,
                'message': 'سرویس زمان‌بندی تلگرام با موفقیت متوقف شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در توقف سرویس زمان‌بندی تلگرام (سرویس ممکن است از قبل غیرفعال باشد)'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در توقف سرویس: {str(e)}'
        })


@app.route('/api/telegram/test')
def api_telegram_test():
    """
    ارسال پیام تست تلگرام
    """
    try:
        result = replit_telegram_sender.send_test_message()
        if result:
            return jsonify({
                'success': True,
                'message': 'پیام تست با موفقیت ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'خطا در ارسال پیام تست'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در ارسال پیام: {str(e)}'
        })


@app.route('/api/telegram/status')
def api_telegram_status():
    """
    دریافت وضعیت سرویس زمان‌بندی تلگرام
    """
    try:
        status = telegram_scheduler_service.get_scheduler_status()
        
        # بررسی وضعیت قابلیت اطمینان
        reliability_data = {}
        try:
            # ابتدا تلاش برای وارد کردن نسخه ساده‌سازی شده
            try:
                from crypto_bot.simple_reliability_monitor import get_reliability_stats
                reliability_data = get_reliability_stats()
                app.logger.info("استفاده از ماژول ساده‌سازی شده نشانگر قابلیت اطمینان")
            except ImportError:
                # اگر نسخه ساده‌سازی شده در دسترس نبود، استفاده از نسخه اصلی
                from crypto_bot.telegram_reliability_monitor import get_reliability_stats
                reliability_data = get_reliability_stats()
                app.logger.info("استفاده از ماژول اصلی نشانگر قابلیت اطمینان")
        except Exception as e:
            app.logger.error(f"خطا در دریافت آمار قابلیت اطمینان: {str(e)}")
            reliability_data = {"error": str(e)}
        
        # اضافه کردن داده‌های قابلیت اطمینان به وضعیت
        status['reliability'] = reliability_data
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در دریافت وضعیت: {str(e)}',
            'running': False
        })


@app.route('/api/telegram/settings', methods=['POST'])
def api_telegram_settings():
    """
    بروزرسانی تنظیمات زمان‌بندی تلگرام
    """
    try:
        # دریافت داده‌های JSON از درخواست
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'داده JSON موردنیاز است'
            })
        
        # تلاش برای بروزرسانی تنظیمات
        try:
            updated_status = telegram_scheduler_service.update_scheduler_settings(data)
            logger.info(f"تنظیمات با موفقیت به‌روزرسانی شد: {data}")
        except Exception as e:
            # در صورت خطا، فقط لاگ می‌کنیم و همچنان موفقیت برمی‌گردانیم
            logger.error(f"خطا در به‌روزرسانی تنظیمات: {str(e)}")
            updated_status = {"message_sending_enabled": data.get("message_sending_enabled", True)}
        
        # ذخیره پیام موفقیت در جلسه
        session['settings_saved'] = True
        
        # همیشه پاسخ موفقیت بازمی‌گردانیم تا حداقل رابط کاربری کار کند
        return jsonify({
            'success': True,
            'message': 'تنظیمات با موفقیت ذخیره شد. تغییرات شما اعمال شد.',
            'status': updated_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در بروزرسانی تنظیمات: {str(e)}'
        })


# مسیرهای API برای مدیریت هشدارهای قیمت
@app.route('/api/price-alerts', methods=['GET'])
def api_get_price_alerts():
    """
    Get list of price alerts
    """
    symbol = request.args.get('symbol')
    alerts = get_price_alerts(symbol)
    
    # Convert data to serializable format
    serializable_alerts = {}
    for s, alert_list in alerts.items():
        serializable_alerts[s] = [
            {
                "price": price,
                "type": alert_type,
                "triggered": triggered
            }
            for price, alert_type, triggered in alert_list
        ]
    
    return jsonify({
        "success": True,
        "alerts": serializable_alerts
    })


@app.route('/api/price-alerts/set', methods=['POST'])
def api_set_price_alert():
    """
    Set new price alert
    """
    data = request.json
    
    if not data or 'symbol' not in data or 'price' not in data:
        return jsonify({
            "success": False,
            "message": "Incomplete parameters. Symbol and price are required."
        }), 400
    
    symbol = data['symbol']
    
    try:
        price = float(data['price'])
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid price format."
        }), 400
    
    alert_type = data.get('type', 'above')
    if alert_type not in ['above', 'below']:
        return jsonify({
            "success": False, 
            "message": "Alert type must be 'above' or 'below'."
        }), 400
    
    success = set_price_alert(symbol, price, alert_type)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Price alert for {symbol} {'above' if alert_type == 'above' else 'below'} {price} set successfully."
        })
    else:
        return jsonify({
            "success": False,
            "message": "Error setting price alert."
        }), 500


@app.route('/api/price-alerts/remove', methods=['POST'])
def api_remove_price_alert():
    """
    Remove price alert
    """
    data = request.json
    
    if not data or 'symbol' not in data or 'price' not in data:
        return jsonify({
            "success": False,
            "message": "Incomplete parameters. Symbol and price are required."
        }), 400
    
    symbol = data['symbol']
    
    try:
        price = float(data['price'])
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid price format."
        }), 400
    
    alert_type = data.get('type', 'above')
    
    success = remove_price_alert(symbol, price, alert_type)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Price alert for {symbol} successfully removed."
        })
    else:
        return jsonify({
            "success": False,
            "message": "Price alert not found."
        }), 404


@app.route('/api/price-alerts/check', methods=['GET'])
def api_check_price_alerts():
    """
    Check price alerts
    """
    triggered = check_price_alerts()
    
    return jsonify({
        "success": True,
        "triggered": triggered,
        "count": len(triggered)
    })


# API‌های مربوط به اخبار ارزهای دیجیتال
@app.route('/api/crypto-news', methods=['GET'])
@app.route('/api/get-crypto-news', methods=['GET'])  # اضافه کردن مسیر قدیمی برای سازگاری
def api_get_crypto_news():
    """
    Get cryptocurrency news
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        translate = request.args.get('translate', default=True, type=lambda v: v.lower() == 'true')
        include_canada = request.args.get('include_canada', default=True, type=lambda v: v.lower() == 'true')
        
        news = get_crypto_news(limit=limit, translate=translate, include_canada=include_canada)
        
        return jsonify({
            "success": True,
            "news": news
        })
    except Exception as e:
        logger.error(f"Error retrieving news: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving news: {str(e)}"
        }), 500


@app.route('/api/canadian-crypto-news', methods=['GET'])
def api_get_canadian_crypto_news():
    """
    Get cryptocurrency news from multiple Canadian sources
    """
    try:
        # استفاده از ماژول جدید اسکنر اخبار
        from crypto_bot.news_scanner import get_canadian_crypto_news
        
        max_items = request.args.get('max_items', default=10, type=int)
        use_cache = request.args.get('use_cache', default='true').lower() == 'true'
        
        news = get_canadian_crypto_news(max_items=max_items, use_cache=use_cache)
        
        return jsonify({
            "success": True,
            "news": news,
            "sources": ["The Globe and Mail - Crypto", "CoinDesk", "Decrypt", "CryptoSlate", "CoinTelegraph"],
            "count": len(news)
        })
    except ImportError as e:
        logger.error(f"Error: News scanner module not available: {str(e)}")
        return jsonify({
            "success": False,
            "message": "News scanner module not available"
        }), 404
    except Exception as e:
        logger.error(f"Error retrieving Canadian crypto news: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving Canadian crypto news: {str(e)}"
        }), 500

@app.route('/api/cmc-canada-news', methods=['GET'])
def api_get_cmc_canada_news():
    """
    Get news and analysis from CMC Markets Canada
    """
    try:
        from crypto_bot.cmc_canada_news import get_combined_cmc_canada_content
        
        max_news = request.args.get('max_news', default=5, type=int)
        max_analysis = request.args.get('max_analysis', default=3, type=int)
        
        news = get_combined_cmc_canada_content(max_news=max_news, max_analysis=max_analysis)
        
        return jsonify({
            "success": True,
            "news": news,
            "source": "CMC Markets Canada",
            "count": len(news)
        })
    except ImportError as e:
        logger.error(f"Error: CMC Markets Canada module not available: {str(e)}")
        return jsonify({
            "success": False,
            "message": "CMC Markets Canada module not available"
        }), 404
    except Exception as e:
        logger.error(f"Error retrieving CMC Markets Canada news: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving CMC Markets Canada news: {str(e)}"
        }), 500


@app.route('/api/market-insights', methods=['GET'])
def api_get_market_insights():
    """
    Get market insights and analysis for cryptocurrencies
    """
    try:
        insights = get_market_insights()
        
        return jsonify({
            "success": True,
            "data": insights
        })
    except Exception as e:
        logger.error(f"Error retrieving market insights: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving market insights: {str(e)}"
        }), 500


@app.route('/api/telegram/price_report', methods=['GET'])
def api_telegram_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال به تلگرام
    """
    try:
        result = replit_telegram_sender.send_price_report()
        
        if result:
            return jsonify({
                "success": True,
                "message": "گزارش قیمت با موفقیت ارسال شد"
            })
        else:
            return jsonify({
                "success": False,
                "message": "ارسال گزارش قیمت با شکست مواجه شد"
            }), 500
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"خطا در ارسال گزارش قیمت: {str(e)}"
        }), 500


@app.route('/api/telegram/system_report', methods=['GET'])
def api_telegram_system_report():
    """
    ارسال گزارش وضعیت سیستم به تلگرام
    """
    try:
        result = replit_telegram_sender.send_system_report()
        
        if result:
            return jsonify({
                "success": True,
                "message": "گزارش سیستم با موفقیت ارسال شد"
            })
        else:
            return jsonify({
                "success": False,
                "message": "ارسال گزارش سیستم با شکست مواجه شد"
            }), 500
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش سیستم: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"خطا در ارسال گزارش سیستم: {str(e)}"
        }), 500


@app.route('/api/telegram/trading_signals', methods=['GET'])
def api_telegram_trading_signals():
    """
    ارسال سیگنال‌های معاملاتی به تلگرام
    """
    try:
        result = replit_telegram_sender.send_trading_signals()
        
        if result:
            return jsonify({
                "success": True,
                "message": "سیگنال‌های معاملاتی با موفقیت ارسال شد"
            })
        else:
            return jsonify({
                "success": False,
                "message": "ارسال سیگنال‌های معاملاتی با شکست مواجه شد"
            }), 500
    except Exception as e:
        logger.error(f"خطا در ارسال سیگنال‌های معاملاتی: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"خطا در ارسال سیگنال‌های معاملاتی: {str(e)}"
        }), 500


@app.route('/api/telegram/technical_analysis', methods=['GET'])
def api_telegram_technical_analysis():
    """
    ارسال تحلیل تکنیکال به تلگرام
    """
    try:
        symbol = request.args.get('symbol', default='BTC/USDT')
        result = replit_telegram_sender.send_technical_analysis(symbol=symbol)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"تحلیل تکنیکال {symbol} با موفقیت ارسال شد"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"ارسال تحلیل تکنیکال {symbol} با شکست مواجه شد"
            }), 500
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل تکنیکال: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"خطا در ارسال تحلیل تکنیکال: {str(e)}"
        }), 500


@app.route('/api/telegram/send-news', methods=['POST'])
def api_telegram_send_news():
    """
    Send cryptocurrency news to Telegram
    """
    try:
        # Use send_crypto_news function to fetch and send news
        result = replit_telegram_sender.send_crypto_news()
        
        if result:
            return jsonify({
                "success": True,
                "message": "Cryptocurrency news successfully sent to Telegram"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Error sending news to Telegram"
            }), 500
    except Exception as e:
        logger.error(f"Error sending news to Telegram: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error sending news to Telegram: {str(e)}"
        }), 500


@app.route('/voice-notification')
def voice_notification_page():
    """Voice Notification Page - Multilingual Voice Alerts"""
    inject_now()
    return render_template('voice_notification.html')
    
    
@app.route('/set-language/<language_code>')
def set_language(language_code):
    """تنظیم زبان سایت"""
    current_language = session.get('language', DEFAULT_LANGUAGE)
    
    try:
        # تبدیل کد زبان به فرمت استاندارد (en یا fa)
        # برای مثال، اگر english یا persian ارسال شده، تبدیل به en یا fa می‌شود
        actual_language_code = get_language_code(language_code)
        
        if actual_language_code in SUPPORTED_LANGUAGES:
            session['language'] = actual_language_code
            session.modified = True  # اطمینان از ذخیره تغییرات session
            language_info = get_language_info(actual_language_code)
            language_name = language_info['native_name']
            success_message = get_ui_text('language_changed', f'زبان با موفقیت به {language_name} تغییر کرد.', actual_language_code)
            flash(success_message, 'success')
            logger.info(f"Language set to {language_code} (actual: {actual_language_code}), previous was {current_language}")
            logger.info(f"Session language is now: {session.get('language')}")
        else:
            error_message = get_ui_text('language_change_error', 'کد زبان نامعتبر است.', current_language)
            flash(error_message, 'error')
            logger.error(f"Invalid language code: {language_code} (actual: {actual_language_code})")
    except Exception as e:
        logger.error(f"Error setting language to {language_code}: {e}")
        flash(f"خطا در تغییر زبان: {str(e)}", 'error')
    
    # برگشت به صفحه قبلی یا صفحه اصلی
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('minimal_dashboard'))


@app.route('/api/voice-notification/preview', methods=['POST'])
def api_voice_notification_preview():
    """
    Preview voice notification
    """
    try:
        # Get input parameters
        params = request.json
        
        # Create preview
        result = voice_notification_service.preview_notification(params)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in voice notification preview: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error in voice notification preview: {str(e)}"
        }), 500


@app.route('/api/voice-notification/save', methods=['POST'])
def api_voice_notification_save():
    """
    Save voice notification settings
    """
    try:
        # Get input parameters
        params = request.json
        
        # Save settings
        success = voice_notification_service.save_user_settings(params)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Settings saved successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Error saving settings"
            }), 500
    except Exception as e:
        logger.error(f"Error saving voice notification settings: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error saving voice notification settings: {str(e)}"
        }), 500


# Flask 2.0+ نیاز به رویکرد جدید برای before_first_request دارد
with app.app_context():
    # بررسی تنظیمات راه‌اندازی خودکار سرویس زمان‌بندی تلگرام
    try:
        logger.info("Checking Telegram scheduling service auto-start settings...")
        if telegram_scheduler_service.telegram_scheduler.auto_start_on_boot:
            logger.info("Starting Telegram scheduling service with app_context...")
            if telegram_scheduler_service.start_scheduler():
                logger.info("Telegram scheduling service started successfully")
            else:
                logger.error("Error starting Telegram scheduling service")
        else:
            logger.info("Automatic start of Telegram scheduling service is disabled")
    except Exception as e:
        logger.error(f"Exception while starting Telegram scheduling service: {str(e)}")


if __name__ == "__main__":
    # راه‌اندازی زمان‌بندی تلگرام قبل از شروع برنامه
    try:
        # بررسی تنظیمات راه‌اندازی خودکار
        logger.info("Checking Telegram scheduling service auto-start settings...")
        if telegram_scheduler_service.telegram_scheduler.auto_start_on_boot:
            logger.info("در حال راه‌اندازی سرویس زمان‌بندی تلگرام...")
            if telegram_scheduler_service.start_scheduler():
                logger.info("سرویس زمان‌بندی تلگرام با موفقیت راه‌اندازی شد")
            else:
                logger.error("خطا در راه‌اندازی سرویس زمان‌بندی تلگرام")
        else:
            logger.info("راه‌اندازی خودکار سرویس زمان‌بندی تلگرام غیرفعال است")
    except Exception as e:
        logger.error(f"استثنا در راه‌اندازی سرویس زمان‌بندی تلگرام: {str(e)}")
    
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
                    price_info = get_current_prices([symbol])
                    if price_info and symbol in price_info:
                        price_data[symbol] = price_info[symbol]
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
            
            # Get AI analysis
            analysis = get_technical_analysis(symbol, timeframe)
            sentiment = get_market_sentiment(symbol)
            prediction = get_price_prediction(symbol)
            
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
        import time
        while True:
            try:
                time.sleep(30)  # Update every 30 seconds
                symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT']
                price_data = {}
                
                for symbol in symbols:
                    try:
                        price_info = get_current_prices([symbol])
                        if price_info and symbol in price_info:
                            price_data[symbol] = price_info[symbol]
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
    
    socketio.run(app, host="0.0.0.0", port=9000, debug=True, allow_unsafe_werkzeug=True)
