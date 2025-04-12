#!/usr/bin/env python3
"""
روت‌های مربوط به تحلیل ارزهای دیجیتال

این ماژول روت‌های مربوط به صفحات تحلیل ارزهای دیجیتال و پاسخگویی به سوالات را ارائه می‌دهد.
"""

import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from crypto_bot.crypto_analysis_service import (
    get_crypto_analysis,
    get_crypto_market_data,
    get_crypto_news
)

# تنظیم لاگ
logger = logging.getLogger(__name__)

def register_routes(app):
    """
    ثبت روت‌های تحلیل ارزها با برنامه فلسک
    
    Args:
        app: برنامه فلسک
    """
    
    @app.route('/crypto-analysis')
    def crypto_analysis_home():
        """صفحه اصلی تحلیل ارزهای دیجیتال"""
        
        # لیست ارزهای محبوب برای نمایش به عنوان پیشنهاد
        popular_cryptos = [
            {"name": "Bitcoin", "symbol": "BTC", "icon": "fab fa-bitcoin text-warning"},
            {"name": "Ethereum", "symbol": "ETH", "icon": "fab fa-ethereum text-primary"},
            {"name": "Solana", "symbol": "SOL", "icon": "fas fa-wave-square text-success"},
            {"name": "XRP", "symbol": "XRP", "icon": "fas fa-xs text-info"},
            {"name": "Cardano", "symbol": "ADA", "icon": "fas fa-atom text-primary"},
            {"name": "Dogecoin", "symbol": "DOGE", "icon": "fas fa-dog text-warning"},
            {"name": "Shiba Inu", "symbol": "SHIB", "icon": "fas fa-dog text-danger"},
            {"name": "Polkadot", "symbol": "DOT", "icon": "fas fa-dot-circle text-danger"},
            {"name": "Avalanche", "symbol": "AVAX", "icon": "fas fa-mountain text-danger"},
            {"name": "Chainlink", "symbol": "LINK", "icon": "fas fa-link text-primary"}
        ]
        
        # لیست انواع تحلیل
        analysis_types = [
            {"id": "general", "name": "General Analysis", "icon": "fas fa-chart-line", "description": "Overall analysis including technical, fundamental, and news"},
            {"id": "technical", "name": "Technical Analysis", "icon": "fas fa-chart-bar", "description": "Charts, patterns, and technical indicators"},
            {"id": "fundamental", "name": "Fundamental Analysis", "icon": "fas fa-project-diagram", "description": "Technology, team, use cases, and tokenomics"},
            {"id": "news", "name": "News Analysis", "icon": "fas fa-newspaper", "description": "Recent news and developments"},
            {"id": "price_prediction", "name": "Price Prediction", "icon": "fas fa-crystal-ball", "description": "Short, medium, and long term price forecasts"},
            {"id": "trading_strategy", "name": "Trading Strategy", "icon": "fas fa-exchange-alt", "description": "Trading strategies and recommendations"}
        ]
        
        # نمایش صفحه اصلی
        return render_template('crypto_analysis_home.html',
                              popular_cryptos=popular_cryptos,
                              analysis_types=analysis_types)
    
    @app.route('/crypto-analysis/result', methods=['GET', 'POST'])
    def crypto_analysis_result():
        """نمایش نتیجه تحلیل ارز دیجیتال"""
        if request.method == 'POST':
            # دریافت پارامترها از فرم
            crypto_name = request.form.get('crypto_name', '')
            analysis_type = request.form.get('analysis_type', 'general')
            
            if not crypto_name:
                flash('Please enter a cryptocurrency name', 'warning')
                return redirect(url_for('crypto_analysis_home'))
            
            # تنظیم کش session
            session['last_analysis_request'] = {
                'crypto_name': crypto_name,
                'analysis_type': analysis_type
            }
            
            # هدایت به صفحه نتیجه
            return redirect(url_for('crypto_analysis_result'))
        
        # بررسی اینکه آیا درخواستی وجود دارد
        if 'last_analysis_request' not in session:
            return redirect(url_for('crypto_analysis_home'))
        
        # دریافت پارامترها از session
        request_data = session['last_analysis_request']
        crypto_name = request_data.get('crypto_name', '')
        analysis_type = request_data.get('analysis_type', 'general')
        
        # دریافت تحلیل
        analysis_result = get_crypto_analysis(crypto_name, analysis_type)
        
        # تلاش برای دریافت داده‌های بازار
        market_data = None
        try:
            # تبدیل نام ارز به فرمت مناسب برای API
            crypto_id = crypto_name.lower().replace(' ', '-')
            market_data = get_crypto_market_data(crypto_id)
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
        
        # دریافت اخبار مرتبط
        news_data = None
        if analysis_type == 'news' or analysis_type == 'general':
            try:
                news_data = get_crypto_news(crypto_name)
            except Exception as e:
                logger.error(f"Error getting news data: {str(e)}")
        
        # نمایش صفحه نتیجه
        return render_template('crypto_analysis_result.html',
                              crypto_name=crypto_name,
                              analysis_type=analysis_type,
                              analysis_result=analysis_result,
                              market_data=market_data,
                              news_data=news_data)
    
    @app.route('/api/crypto-analysis', methods=['POST'])
    def api_crypto_analysis():
        """
        API برای دریافت تحلیل ارز دیجیتال
        """
        crypto_name = request.json.get('crypto_name', '')
        analysis_type = request.json.get('analysis_type', 'general')
        
        if not crypto_name:
            return jsonify({
                'success': False,
                'error': 'Cryptocurrency name is required'
            }), 400
        
        # دریافت تحلیل
        analysis_result = get_crypto_analysis(crypto_name, analysis_type)
        
        return jsonify(analysis_result)
    
    @app.route('/api/crypto-market-data/<crypto_symbol>')
    def api_crypto_market_data(crypto_symbol):
        """
        API برای دریافت داده‌های بازار یک ارز دیجیتال
        """
        market_data = get_crypto_market_data(crypto_symbol)
        
        return jsonify(market_data)
    
    @app.route('/api/crypto-news/<crypto_name>')
    def api_crypto_news(crypto_name):
        """
        API برای دریافت اخبار مرتبط با یک ارز دیجیتال
        """
        limit = request.args.get('limit', 5, type=int)
        news_data = get_crypto_news(crypto_name, limit)
        
        return jsonify(news_data)