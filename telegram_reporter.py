#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت ساده برای ارسال گزارش‌های دوره‌ای به تلگرام
این اسکریپت می‌تواند به طور مستقل اجرا شود و نیازی به اجرای scheduler.py ندارد
"""

import os
import sys
import time
import logging
from datetime import datetime
import traceback

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_reporter.log")
    ]
)
logger = logging.getLogger("telegram_reporter")

# وارد کردن ماژول تلگرام
try:
    # ابتدا سعی می‌کنیم از ماژول‌های پروژه استفاده کنیم
    from crypto_bot.telegram_service import send_telegram_message, get_current_persian_time
    logger.info("ماژول‌های تلگرام با موفقیت بارگذاری شدند")
except ImportError:
    logger.error("خطا در بارگذاری ماژول‌های تلگرام از پروژه")
    sys.exit(1)

# وارد کردن ماژول تحلیل تکنیکال
try:
    from crypto_bot.technical_analysis import get_latest_signals, get_technical_analysis, get_multi_timeframe_analysis
    logger.info("ماژول تحلیل تکنیکال با موفقیت بارگذاری شد")
except ImportError:
    logger.error("خطا در بارگذاری ماژول تحلیل تکنیکال")
    logger.error(traceback.format_exc())

def get_price_report():
    """
    تهیه گزارش قیمت ارزهای دیجیتال
    در این نسخه ساده، از داده‌های ثابت استفاده می‌کنیم
    """
    try:
        price_report = "🤖 *گزارش قیمت ارزهای دیجیتال*\n\n"
        
        # افزودن قیمت‌های نمونه (در نسخه‌های آینده می‌توان از API واقعی استفاده کرد)
        prices = [
            "BTC/USDT: $67,345.20 (🟢 +2.3%)",
            "ETH/USDT: $3,245.80 (🟢 +1.8%)",
            "XRP/USDT: $0.5423 (🔴 -0.7%)",
            "BNB/USDT: $532.40 (🟢 +0.5%)",
            "SOL/USDT: $143.21 (🟢 +3.2%)"
        ]
            
        price_report += "\n".join(prices)
        price_report += "\n\n⏰ زمان گزارش: " + get_current_persian_time()
        
        return price_report
    except Exception as e:
        logger.error(f"خطا در تهیه گزارش قیمت: {str(e)}")
        return None

def get_technical_report(symbol="BTC/USDT"):
    """
    تهیه گزارش تحلیل تکنیکال برای یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        str: گزارش تحلیل تکنیکال
    """
    try:
        logger.info(f"در حال تهیه گزارش تحلیل تکنیکال برای {symbol}...")
        
        # دریافت تحلیل تکنیکال
        analysis = get_technical_analysis(symbol)
        
        if 'error' in analysis:
            return f"❌ *خطا در تحلیل {symbol}*\n\n{analysis['error']}\n\n⏰ زمان: {get_current_persian_time()}"
        
        # ایجاد گزارش متنی
        report = f"📊 *تحلیل تکنیکال {symbol}*\n\n"
        
        # افزودن قیمت و سیگنال
        price_emoji = "🟢" if analysis.get('daily_change', 0) >= 0 else "🔴"
        report += f"*قیمت فعلی:* {analysis['last_price']} USDT {price_emoji}\n"
        report += f"*تغییر روزانه:* {analysis.get('daily_change', 0)}%\n"
        report += f"*تغییر هفتگی:* {analysis.get('weekly_change', 0)}%\n\n"
        
        # افزودن سیگنال معاملاتی
        signal_emoji = "🟢" if analysis['signal'] in ["خرید", "خرید قوی"] else "🔴" if analysis['signal'] in ["فروش", "فروش قوی"] else "⚪"
        report += f"*سیگنال معاملاتی:* {signal_emoji} {analysis['signal']} (قدرت: {analysis['signal_strength']}%)\n"
        report += f"*توصیه:* {analysis['recommendation']}\n"
        report += f"*روند:* {analysis['trend']}\n\n"
        
        # افزودن نقاط حمایت و مقاومت
        report += f"*سطح مقاومت:* {analysis['resistance_level']} USDT\n"
        report += f"*سطح حمایت:* {analysis['support_level']} USDT\n\n"
        
        # افزودن شاخص‌ها
        report += "*شاخص‌های کلیدی:*\n"
        
        # RSI
        rsi_value = analysis['indicators']['RSI']['value']
        rsi_emoji = "🟢" if rsi_value < 30 else "🔴" if rsi_value > 70 else "⚪"
        report += f"- RSI: {rsi_value} {rsi_emoji} ({analysis['indicators']['RSI']['interpretation']})\n"
        
        # MACD
        macd_emoji = "🟢" if analysis['indicators']['MACD']['interpretation'] == "صعودی" else "🔴"
        report += f"- MACD: {analysis['indicators']['MACD']['value']} {macd_emoji} ({analysis['indicators']['MACD']['interpretation']})\n"
        
        # Bollinger Bands
        bb_width = analysis['indicators']['Bollinger Bands']['width']
        bb_emoji = "🟢" if bb_width > 0.05 else "⚪"
        report += f"- پهنای باندهای بولینگر: {bb_width} {bb_emoji} ({analysis['indicators']['Bollinger Bands']['interpretation']})\n\n"
        
        # نوسانات
        vol_emoji = "⚠️" if analysis.get('volatility', {}).get('interpretation', "") == "بالا" else "⚪"
        report += f"*نوسانات:* {vol_emoji} {analysis.get('volatility', {}).get('daily', 0)}% ({analysis.get('volatility', {}).get('interpretation', 'نامشخص')})\n\n"
        
        report += f"⏰ زمان تحلیل: {analysis['updated_at']}"
        
        return report
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در تهیه گزارش تحلیل تکنیکال: {str(e)}\n{error_text}")
        return f"❌ *خطا در تهیه گزارش تحلیل تکنیکال*\n\n{str(e)}\n\n⏰ زمان: {get_current_persian_time()}"

def get_market_overview():
    """
    تهیه گزارش کلی بازار با تحلیل چند ارز اصلی
    
    Returns:
        str: گزارش کلی بازار
    """
    try:
        logger.info("در حال تهیه گزارش کلی بازار...")
        
        # ارزهای مورد نظر برای تحلیل
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT"]
        
        # ایجاد گزارش متنی
        report = "🌐 *گزارش کلی بازار ارزهای دیجیتال*\n\n"
        
        # تحلیل هر ارز و افزودن به گزارش
        for symbol in symbols:
            analysis = get_latest_signals(symbol)
            
            if 'error' in analysis:
                continue
                
            # افزودن خلاصه سیگنال
            signal_emoji = "🟢" if analysis['signal'] in ["خرید", "خرید قوی"] else "🔴" if analysis['signal'] in ["فروش", "فروش قوی"] else "⚪"
            price_emoji = "📈" if analysis.get('daily_change', 0) >= 0 else "📉"
            
            report += f"*{symbol}:* {price_emoji} {analysis['last_price']} USDT\n"
            report += f"سیگنال: {signal_emoji} {analysis['signal']}\n"
            report += f"روند: {analysis['trend']}\n\n"
        
        report += f"⏰ زمان گزارش: {get_current_persian_time()}"
        
        return report
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در تهیه گزارش کلی بازار: {str(e)}\n{error_text}")
        return f"❌ *خطا در تهیه گزارش کلی بازار*\n\n{str(e)}\n\n⏰ زمان: {get_current_persian_time()}"

def send_periodic_report():
    """
    ارسال گزارش دوره‌ای به تلگرام
    """
    try:
        logger.info("در حال تهیه و ارسال گزارش دوره‌ای...")
        
        # دریافت گزارش قیمت
        price_report = get_price_report()
        if not price_report:
            # در صورت خطا در دریافت گزارش، یک پیام ساده ارسال می‌کنیم
            price_report = "🤖 *گزارش دوره‌ای سیستم*\n\n"
            price_report += "سیستم در حال کار است اما در حال حاضر قادر به دریافت قیمت‌های دقیق نیست.\n"
            price_report += "وضعیت فعلی: در حال اجرا ✅\n\n"
            price_report += "⏰ زمان گزارش: " + get_current_persian_time()
        
        # دریافت گزارش کلی بازار
        market_report = get_market_overview()
        
        # ارسال گزارش به تلگرام
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        
        # ارسال گزارش قیمت
        result1 = send_telegram_message(chat_id, price_report)
        
        # ارسال گزارش کلی بازار
        result2 = send_telegram_message(chat_id, market_report)
        
        # ارسال تحلیل تکنیکال بیت‌کوین
        btc_report = get_technical_report("BTC/USDT")
        result3 = send_telegram_message(chat_id, btc_report)
        
        if result1 and result2 and result3:
            logger.info("گزارش‌های دوره‌ای با موفقیت ارسال شدند")
            return True
        else:
            logger.error("خطا در ارسال برخی از گزارش‌های دوره‌ای")
            return False
            
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در ارسال گزارش دوره‌ای: {str(e)}\n{error_text}")
        return False

def send_technical_analysis(symbol="BTC/USDT"):
    """
    ارسال تحلیل تکنیکال یک ارز به تلگرام
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        bool: نتیجه ارسال پیام
    """
    try:
        logger.info(f"در حال ارسال تحلیل تکنیکال {symbol}...")
        
        # دریافت گزارش تحلیل تکنیکال
        report = get_technical_report(symbol)
        
        # ارسال گزارش به تلگرام
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        result = send_telegram_message(chat_id, report)
        
        if result:
            logger.info(f"تحلیل تکنیکال {symbol} با موفقیت ارسال شد")
            return True
        else:
            logger.error(f"خطا در ارسال تحلیل تکنیکال {symbol}")
            return False
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در ارسال تحلیل تکنیکال: {str(e)}\n{error_text}")
        return False

def send_test_message():
    """
    ارسال پیام تست برای بررسی عملکرد سیستم
    """
    try:
        message = "🤖 *پیام تست ربات معامله ارز دیجیتال*\n\n"
        message += "این یک پیام تست است. سیستم گزارش‌دهی در حال کار است.\n\n"
        message += "⏰ زمان: " + get_current_persian_time()
        
        chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
        result = send_telegram_message(chat_id, message)
        
        if result:
            logger.info("پیام تست با موفقیت ارسال شد")
            return True
        else:
            logger.error("خطا در ارسال پیام تست")
            return False
    except Exception as e:
        error_text = traceback.format_exc()
        logger.error(f"خطا در ارسال پیام تست: {str(e)}\n{error_text}")
        return False

def main():
    """
    تابع اصلی برنامه
    با پارامتر 'test' یک پیام تست ارسال می‌کند
    با پارامتر 'technical' و نام ارز، تحلیل تکنیکال ارسال می‌کند
    با پارامتر 'market' گزارش کلی بازار ارسال می‌کند
    بدون پارامتر یک گزارش دوره‌ای ارسال می‌کند
    """
    logger.info("شروع اجرای برنامه گزارش‌دهی تلگرام")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # ارسال پیام تست
            send_test_message()
        elif sys.argv[1] == 'technical':
            # ارسال تحلیل تکنیکال
            symbol = sys.argv[2] if len(sys.argv) > 2 else "BTC/USDT"
            send_technical_analysis(symbol)
        elif sys.argv[1] == 'market':
            # ارسال گزارش کلی بازار
            market_report = get_market_overview()
            chat_id = int(os.environ.get("DEFAULT_CHAT_ID", "722627622"))
            send_telegram_message(chat_id, market_report)
    else:
        # ارسال گزارش دوره‌ای
        send_periodic_report()
    
    logger.info("پایان اجرای برنامه گزارش‌دهی تلگرام")

if __name__ == "__main__":
    main()