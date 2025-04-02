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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    watched_currencies = session.get('watched_currencies', DEFAULT_CURRENCIES[:3])
    current_prices = get_current_prices(watched_currencies)
    
    # Get technical indicators for display
    technical_data = {}
    for currency in watched_currencies:
        technical_data[currency] = get_technical_indicators(currency, '1d')
    
    # Get latest news
    news = get_latest_news(limit=5)
    
    # Generate signals
    signals = generate_signals(watched_currencies)
    
    return render_template(
        'dashboard.html',
        prices=current_prices,
        technical_data=technical_data,
        news=news,
        signals=signals,
        currencies=DEFAULT_CURRENCIES,
        watched_currencies=watched_currencies,
        timeframes=TIMEFRAMES,
        scheduler_running=session.get('scheduler_running', False)
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
        scheduler_running=session.get('scheduler_running', False)
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
        prices = get_current_prices([symbol])
        return jsonify({'success': True, 'data': prices})
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
    try:
        news = get_latest_news(limit=limit)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
