import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from crypto_bot.config import DEFAULT_CURRENCIES, TIMEFRAMES
from crypto_bot.market_data import get_current_prices
from crypto_bot.scheduler import start_scheduler, stop_scheduler
from crypto_bot.technical_analysis import get_technical_indicators
from crypto_bot.news_analyzer import get_latest_news
from crypto_bot.signal_generator import generate_signals
from crypto_bot.email_service import send_test_email, update_email_settings
from crypto_bot.commodity_data import get_commodity_prices, get_forex_rates, get_economic_indicators

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "crypto_bot_secret_key")

# Add datetime to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

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
    if 'include_middle_east' not in session:
        session['include_middle_east'] = True  # Default to including Middle Eastern news sources

@app.route('/')
def index():
    return redirect(url_for('commodities_dashboard'))

@app.route('/api_test')
def api_test():
    """Render API test page"""
    return render_template('api_test.html')
    
@app.route('/commodities_dashboard')
def commodities_dashboard():
    """Render commodities dashboard page"""
    return render_template('commodities_dashboard.html')
    
@app.route('/test')
def test_dashboard():
    """Render test dashboard page to debug API and JavaScript issues"""
    return render_template('test_dashboard.html')

@app.route('/dashboard_new')
def dashboard_new():
    # Initialize session if not already set
    if not session.get('initialized', False):
        session['initialized'] = True
    
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    current_prices = get_current_prices(watched_currencies)
    
    # Get technical indicators for display
    technical_data = {}
    for currency in watched_currencies:
        technical_data[currency] = get_technical_indicators(currency, '1d')
    
    # Get latest news (use user's setting for Middle Eastern sources)
    include_middle_east = session.get('include_middle_east', True)
    news = get_latest_news(limit=5, include_middle_east=include_middle_east)
    
    # Generate signals
    signals = generate_signals(watched_currencies)
    
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
    logger.debug(f"Dashboard_new rendering - Session initialized: {session.get('initialized', False)}")
    logger.debug(f"Watched currencies: {watched_currencies}")
    
    return render_template(
        'dashboard_new.html',
        prices=current_prices,
        technical_data=technical_data,
        news=news,
        signals=signals,
        currencies=DEFAULT_CURRENCIES,
        watched_currencies=watched_currencies,
        timeframes=TIMEFRAMES,
        scheduler_running=session.get('scheduler_running', False),
        include_middle_east=include_middle_east,
        commodities=commodities,
        forex_rates=forex_rates,
        economic_indicators=economic_indicators
    )

@app.route('/dashboard')
def dashboard():
    # Initialize session if not already set
    if not session.get('initialized', False):
        session['initialized'] = True
    
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    current_prices = get_current_prices(watched_currencies)
    
    # Get technical indicators for display
    technical_data = {}
    for currency in watched_currencies:
        technical_data[currency] = get_technical_indicators(currency, '1d')
    
    # Get latest news (use user's setting for Middle Eastern sources)
    include_middle_east = session.get('include_middle_east', True)
    news = get_latest_news(limit=5, include_middle_east=include_middle_east)
    
    # Generate signals
    signals = generate_signals(watched_currencies)
    
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
    logger.debug(f"Dashboard rendering - Session initialized: {session.get('initialized', False)}")
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
        include_middle_east=include_middle_east,
        commodities=commodities,
        forex_rates=forex_rates,
        economic_indicators=economic_indicators
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update watched currencies
        watched_currencies = request.form.getlist('currencies')
        if watched_currencies:
            session['watched_currencies'] = watched_currencies
        
        # Update email settings
        email_enabled = 'email_enabled' in request.form
        email_address = request.form.get('email_address', '')
        email_frequency = request.form.get('email_frequency', 'daily')
        
        session['email_settings'] = {
            'enabled': email_enabled,
            'email': email_address,
            'frequency': email_frequency
        }
        
        # Update Middle Eastern news sources setting
        include_middle_east = 'include_middle_east' in request.form
        session['include_middle_east'] = include_middle_east
        
        # Update scheduler status
        scheduler_enabled = 'scheduler_enabled' in request.form
        
        if scheduler_enabled and not session.get('scheduler_running', False):
            start_scheduler(session['email_settings'], session['watched_currencies'])
            session['scheduler_running'] = True
            flash('Crypto bot scheduler started!', 'success')
        elif not scheduler_enabled and session.get('scheduler_running', False):
            stop_scheduler()
            session['scheduler_running'] = False
            flash('Crypto bot scheduler stopped!', 'warning')
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template(
        'settings.html',
        currencies=DEFAULT_CURRENCIES,
        watched_currencies=session.get('watched_currencies', []),
        email_settings=session.get('email_settings', {}),
        scheduler_running=session.get('scheduler_running', False),
        include_middle_east=session.get('include_middle_east', True)
    )

@app.route('/api/test-email', methods=['POST'])
def test_email():
    email_address = request.form.get('email_address')
    if not email_address:
        return jsonify({'success': False, 'message': 'Email address is required'})
    
    try:
        result = send_test_email(email_address)
        if result:
            return jsonify({'success': True, 'message': 'Test email sent successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send test email. Check your settings.'})
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/price/<symbol>')
def get_price(symbol):
    try:
        # Normalize symbol format - both BTC/USDT and BTC-USDT should work
        # Try with the symbol as provided first
        symbols_to_try = [symbol]
        
        # Add alternative symbol format if not already in the list
        if '/' in symbol:
            alt_symbol = symbol.replace('/', '-')
            symbols_to_try.append(alt_symbol)
        elif '-' in symbol:
            alt_symbol = symbol.replace('-', '/')
            symbols_to_try.append(alt_symbol)
            
        logger.info(f"Trying to get prices for symbols: {symbols_to_try}")
        
        # Try to get prices with a short timeout to prevent waiting
        result = get_current_prices(symbols_to_try, timeout=3)
        
        # Check if we got data for any of the symbol formats
        for sym in symbols_to_try:
            if sym in result:
                logger.info(f"Found price data for {sym}")
                return jsonify({'success': True, 'data': result[sym]})
        
        # If we didn't get data for any format, return a sample with clear marking
        logger.warning(f"No result for {symbol} or alternatives, providing sample data")
        
        # Create sample data that is clearly marked as such
        sample_data = {
            'price': 69420.50,
            'change_24h': 1.2,
            'high_24h': 70000.50,
            'low_24h': 68500.75,
            'volume_24h': 1245678.90,
            'is_sample_data': True,
            'source': 'sample_data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify({'success': True, 'data': sample_data, 'sample_data': True})
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/technical/<symbol>/<timeframe>')
def get_technical(symbol, timeframe):
    try:
        data = get_technical_indicators(symbol, timeframe)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Error getting technical data for {symbol}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

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
    
    try:
        signals = generate_signals(currencies)
        return jsonify({'success': True, 'data': signals})
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
