"""
روت‌های مربوط به تحلیل هوش مصنوعی ارزهای دیجیتال

این ماژول شامل روت‌های مربوط به صفحه پرسش و پاسخ هوش مصنوعی برای تحلیل ارزهای دیجیتال است.
"""

import logging
from flask import render_template, request, jsonify
from crypto_bot.crypto_ai_analysis import (
    get_technical_analysis, 
    get_fundamental_analysis, 
    get_crypto_ai_answer, 
    extract_crypto_symbol
)
from replit_telegram_sender import send_message

# Setup logging
logger = logging.getLogger(__name__)

def register_routes(app):
    """
    Register AI analysis routes with the Flask application
    
    Args:
        app: The Flask application
    """
    
    @app.route('/ai-analysis')
    @app.route('/crypto-ai')
    @app.route('/crypto-ai-analysis')
    def crypto_ai_analysis():
        """AI-powered Cryptocurrency Analysis Page"""
        return render_template('crypto_ai_analysis.html')
    
    @app.route('/ai-analysis/submit', methods=['POST'])
    def crypto_ai_submit():
        """Handle AI analysis submission"""
        query = request.form.get('query', '').strip()
        
        if not query:
            return render_template('crypto_ai_analysis.html', 
                                error="Please enter a cryptocurrency symbol or question")
        
        # Determine the type of analysis based on the query
        query_lower = query.lower()
        
        # Check for explicit mentions of analysis types
        if 'technical' in query_lower or 'technicals' in query_lower or 'chart' in query_lower:
            query_type = 'technical'
            # Extract the symbol
            symbol = extract_crypto_symbol(query)
            if not symbol:
                # If we can't extract a symbol, try to find the first word that could be a symbol
                words = query.split()
                for word in words:
                    if word.upper() in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']:
                        symbol = word.upper()
                        break
                
                if not symbol:
                    # Default to BTC if we still can't find a symbol
                    symbol = 'BTC'
                    
            result = get_technical_analysis(symbol)
                    
        elif 'fundamental' in query_lower or 'fundamentals' in query_lower or 'tokenomics' in query_lower:
            query_type = 'fundamental'
            # Extract the symbol
            symbol = extract_crypto_symbol(query)
            if not symbol:
                # Same logic as above
                words = query.split()
                for word in words:
                    if word.upper() in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']:
                        symbol = word.upper()
                        break
                
                if not symbol:
                    symbol = 'ETH'
                    
            result = get_fundamental_analysis(symbol)
                    
        elif len(query.strip().split()) <= 2 and extract_crypto_symbol(query):
            # If query is just a symbol or very short with a symbol, do both analyses
            # But let's default to technical as it's more common
            query_type = 'technical'
            symbol = extract_crypto_symbol(query)
            result = get_technical_analysis(symbol)
        else:
            # General question
            query_type = 'general'
            result = get_crypto_ai_answer(query)
        
        return render_template('crypto_ai_analysis.html', 
                            result=result, 
                            query_type=query_type)
    
    @app.route('/api/telegram/send-analysis', methods=['POST'])
    def api_telegram_send_analysis():
        """Send AI analysis to Telegram"""
        try:
            data = request.json
            if not data:
                return jsonify({"success": False, "message": "No data provided"})
            
            analysis_type = data.get('type')
            query = data.get('query')
            
            if not analysis_type or not query:
                return jsonify({"success": False, "message": "Missing required parameters"})
            
            # Get the appropriate analysis
            if analysis_type == 'technical':
                symbol = extract_crypto_symbol(query) or 'BTC'
                analysis = get_technical_analysis(symbol)
                message = f"*Technical Analysis: {symbol}*\n\n"
                if analysis.get('price'):
                    message += f"Price: ${analysis.get('price', 0):,.2f}\n"
                if analysis.get('change_24h'):
                    message += f"24h Change: {analysis.get('change_24h', 0):+.2f}%\n\n"
                message += analysis.get('analysis', 'Analysis not available')
                
            elif analysis_type == 'fundamental':
                symbol = extract_crypto_symbol(query) or 'ETH'
                analysis = get_fundamental_analysis(symbol)
                message = f"*Fundamental Analysis: {analysis.get('full_name', symbol)}*\n\n"
                if analysis.get('price'):
                    message += f"Price: ${analysis.get('price', 0):,.2f}\n"
                if analysis.get('change_24h'):
                    message += f"24h Change: {analysis.get('change_24h', 0):+.2f}%\n\n"
                message += analysis.get('analysis', 'Analysis not available')
                
            else:  # general
                analysis = get_crypto_ai_answer(query)
                message = f"*Crypto Question:* {query}\n\n"
                message += analysis.get('answer', 'Answer not available')
            
            # Send to Telegram
            success = send_message(message, parse_mode="Markdown", message_type="ai_analysis")
            
            if success:
                return jsonify({"success": True, "message": "Analysis sent to Telegram successfully"})
            else:
                return jsonify({"success": False, "message": "Error sending analysis to Telegram"})
                
        except Exception as e:
            logger.error(f"Error sending analysis to Telegram: {str(e)}")
            return jsonify({"success": False, "message": f"Error: {str(e)}"})