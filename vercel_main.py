import os
import logging
import random
from datetime import datetime
from crypto_bot.cache_manager import price_cache
from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, jsonify, send_file
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "crypto_bot_secret_key_default_for_development")

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
from crypto_bot.ai_routes import register_ai_routes
register_ai_routes(app)

# Register crypto quiz routes
from crypto_bot.crypto_quiz_routes import register_crypto_quiz_routes
register_crypto_quiz_routes(app)

# Register crypto analysis routes
from crypto_bot.crypto_analysis_routes import register_crypto_analysis_routes
register_crypto_analysis_routes(app)

# Import all routes from api_routes
from api_routes import *

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
