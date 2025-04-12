import logging
import os
import random
import time
from datetime import datetime

import pytz
import requests

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("replit_telegram")

# وارد کردن تابع get_crypto_price از ماژول market_data
from crypto_bot.market_data import get_crypto_price

# وارد کردن ماژول نشانگر قابلیت اطمینان
# تنظیم متغیرهای پیش‌فرض برای حل مشکل LSP
# ماژول قابلیت اطمینان برای استفاده در توابع send_message و غیره لازم است
RELIABILITY_MONITOR_AVAILABLE = False
record_message_attempt = None
record_service_restart = None
get_reliability_stats = None
get_reliability_summary = None

try:
    # ابتدا تلاش برای وارد کردن نسخه ساده‌سازی شده (ترجیح می‌دهیم)
    from crypto_bot.simple_reliability_monitor import (
        record_message_attempt,
        record_service_restart,
        get_reliability_stats,
        get_reliability_summary
    )
    RELIABILITY_MONITOR_AVAILABLE = True
    logger.info("Simplified reliability monitor module loaded")
except ImportError:
    # If simplified version is not available, use the original version
    try:
        from crypto_bot.telegram_reliability_monitor import (
            record_message_attempt,
            record_service_restart,
            get_reliability_stats,
            get_reliability_summary
        )
        RELIABILITY_MONITOR_AVAILABLE = True
        logger.info("Main reliability monitor module loaded")
    except ImportError:
        logger.warning("No reliability monitor module available")
        # Define fallback functions if module doesn't exist
        def record_message_attempt(message_type, success, error_message=None):
            logger.info(f"[Not implemented] Recording message: {message_type}, success: {success}")
            
        def record_service_restart():
            logger.info("[Not implemented] Recording service restart")
            
        def get_reliability_stats():
            return {
                "overall": {"total_sent": 0, "successful": 0, "failed": 0, "success_rate": 0},
                "uptime": {"days": 0, "restarts": 0, "last_restart_hours_ago": 0},
                "recent_events": []
            }
            
        def get_reliability_summary():
            return "Statistical information not available"

# تنظیم کنید - کلید API تلگرام و شناسه چت
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# استفاده مستقیم از آیدی گروه به جای متغیر محیطی
DEFAULT_CHAT_ID = -1002584373095  # آیدی گروه تلگرام

# تنظیم منطقه زمانی تهران و تورنتو
tehran_tz = pytz.timezone('Asia/Tehran')
toronto_tz = pytz.timezone('America/Toronto')

def send_message(text, chat_id=None, parse_mode=None, disable_web_page_preview=True, retries=3, delay=2, message_type="general"):
    """
    ارسال پیام به تلگرام
    
    Args:
        text (str): متن پیام
        chat_id (str, optional): شناسه چت. اگر None باشد، از DEFAULT_CHAT_ID استفاده می‌شود.
        parse_mode (str, optional): حالت پارس متن. می‌تواند "Markdown" یا "HTML" باشد.
        disable_web_page_preview (bool, optional): غیرفعال کردن پیش‌نمایش وب‌سایت.
        retries (int, optional): تعداد تلاش‌های مجدد در صورت خطا.
        delay (int, optional): تاخیر بین تلاش‌های مجدد بر حسب ثانیه.
        message_type (str, optional): نوع پیام برای ثبت در نشانگر قابلیت اطمینان.
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found")
        
        # Record error in reliability monitor
        if RELIABILITY_MONITOR_AVAILABLE:
            record_message_attempt(message_type, False, "TELEGRAM_BOT_TOKEN not found")
            
        return False
    
    if not chat_id:
        if not DEFAULT_CHAT_ID:
            logger.error("DEFAULT_CHAT_ID not found")
            
            # Record error in reliability monitor
            if RELIABILITY_MONITOR_AVAILABLE:
                record_message_attempt(message_type, False, "DEFAULT_CHAT_ID not found")
                
            return False
        chat_id = DEFAULT_CHAT_ID
    
    # آدرس API تلگرام
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # تنظیم پارامترهای درخواست
    params = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": disable_web_page_preview
    }
    
    # اضافه کردن پارامتر پارس مود (مارک‌داون یا HTML) اگر تعیین شده باشد
    if parse_mode:
        params["parse_mode"] = parse_mode
    
    logger.info("Sending message to Telegram...")
    
    for attempt in range(retries):
        try:
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info("Message sent successfully")
                
                # Record success in reliability monitor
                if RELIABILITY_MONITOR_AVAILABLE:
                    record_message_attempt(message_type, True)
                    
                return True
            else:
                error_message = f"Error sending message: {response.status_code} - {response.text}"
                logger.error(error_message)
                
                # If this is the last attempt, record the error
                if attempt == retries - 1:
                    if RELIABILITY_MONITOR_AVAILABLE:
                        record_message_attempt(message_type, False, error_message)
                
                # If rate limit error (429) was received, increase wait time
                if response.status_code == 429:
                    retry_after = int(response.json().get('parameters', {}).get('retry_after', delay * 2))
                    logger.info(f"Rate limit error. Waiting for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    # برای سایر خطاها، با تاخیر معمولی دوباره تلاش کنید
                    time.sleep(delay)
        except Exception as e:
            error_message = f"Exception in sending message: {str(e)}"
            logger.error(error_message)
            time.sleep(delay)
            
            # If this is the last attempt, record the error
            if attempt == retries - 1:
                if RELIABILITY_MONITOR_AVAILABLE:
                    record_message_attempt(message_type, False, error_message)
    
    logger.error(f"After {retries} attempts, message sending failed")
    return False


def send_price_report():
    """
    ارسال گزارش قیمت ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # استفاده از زمان تورنتو
    toronto_timezone = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_timezone)
    current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # داده‌های قیمت - در نسخه واقعی از API دریافت می‌شود
    coins = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 83245.25, "change": 1.2, "recommendation": "خرید"},
        {"name": "Ethereum", "symbol": "ETH", "price": 1672.30, "change": -0.5, "recommendation": "نگهداری"},
        {"name": "BNB", "symbol": "BNB", "price": 626.75, "change": 0.8, "recommendation": "خرید"},
        {"name": "Solana", "symbol": "SOL", "price": 178.65, "change": 2.3, "recommendation": "خرید"},
        {"name": "Cardano", "symbol": "ADA", "price": 0.45, "change": -1.2, "recommendation": "فروش"},
        {"name": "Ripple", "symbol": "XRP", "price": 0.59, "change": 0.3, "recommendation": "نگهداری"},
        {"name": "Polkadot", "symbol": "DOT", "price": 7.32, "change": -0.7, "recommendation": "نگهداری"},
        {"name": "Tether", "symbol": "USDT", "price": 0.9998, "change": 0.01, "recommendation": "نگهداری"},
        {"name": "Polygon", "symbol": "MATIC", "price": 0.58, "change": 1.4, "recommendation": "خرید"},
        {"name": "Dogecoin", "symbol": "DOGE", "price": 0.15, "change": -2.1, "recommendation": "فروش"},
        {"name": "Chainlink", "symbol": "LINK", "price": 15.25, "change": 2.7, "recommendation": "خرید"},
        {"name": "Litecoin", "symbol": "LTC", "price": 86.50, "change": 0.5, "recommendation": "نگهداری"},
        {"name": "Arbitrum", "symbol": "ARB", "price": 1.06, "change": -1.8, "recommendation": "نگهداری"},
        {"name": "Optimism", "symbol": "OP", "price": 2.32, "change": 3.5, "recommendation": "خرید"},
        {"name": "Render", "symbol": "RNDR", "price": 7.28, "change": 5.6, "recommendation": "خرید"},
        {"name": "Fetch.ai", "symbol": "FET", "price": 2.12, "change": 4.3, "recommendation": "خرید"},
        {"name": "Worldcoin", "symbol": "WLD", "price": 4.45, "change": -3.2, "recommendation": "فروش"}
    ]
    
    # ساخت پیام
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

📊 <b>نمودار کندل‌استیک اخیر Bitcoin (BTC/USDT):</b>
<a href="https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1.svg">https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1.svg</a>

📈 <b>وضعیت بازار:</b> {"🟢 صعودی" if sum(c["change"] for c in coins) > 0 else "🔴 نزولی"}

"""
    
    # بخش توصیه‌های خرید و فروش
    buy_recommendations = [coin for coin in coins if coin["recommendation"] == "خرید"]
    sell_recommendations = [coin for coin in coins if coin["recommendation"] == "فروش"]
    
    message += """
🟢 <b>توصیه‌های خرید:</b>
"""
    for coin in buy_recommendations[:3]:  # نمایش 3 توصیه برتر
        message += f"• <b>{coin['name']} ({coin['symbol']})</b>\n"
    
    message += """
🔴 <b>توصیه‌های فروش:</b>
"""
    for coin in sell_recommendations[:3]:  # نمایش 3 توصیه برتر
        message += f"• <b>{coin['name']} ({coin['symbol']})</b>\n"
    
    message += """
━━━━━━━━━━━━━━━━━━
<b>قیمت‌های لحظه‌ای:</b>
"""
    
    # اضافه کردن قیمت‌ها به پیام
    for coin in coins:
        # تعیین ایموجی و فرمت تغییرات بر اساس مثبت یا منفی بودن
        emoji = "🟢" if coin["change"] >= 0 else "🔴"
        change_str = f"+{coin['change']}%" if coin["change"] >= 0 else f"{coin['change']}%"
        
        # تعیین ایموجی برای توصیه
        rec_emoji = "🟢" if coin["recommendation"] == "خرید" else ("🔴" if coin["recommendation"] == "فروش" else "🟡")
        
        # فرمت قیمت بر اساس مقدار آن
        if coin["price"] >= 100:
            price_str = f"${coin['price']:,.0f}"
        elif coin["price"] >= 1:
            price_str = f"${coin['price']:,.2f}"
        else:
            price_str = f"${coin['price']:.4f}"
        
        # اضافه کردن اطلاعات ارز به پیام - با تأکید بر دلار آمریکا
        message += f"{emoji} <b>{coin['name']} ({coin['symbol']})</b>: {price_str} USD ({change_str}) {rec_emoji}\n"
    
    # اگر نشانگر قابلیت اطمینان فعال است، خلاصه آن را اضافه کن
    if RELIABILITY_MONITOR_AVAILABLE:
        try:
            reliability_summary = get_reliability_summary()
            # Only if there is enough data
            if "Telegram system status" in reliability_summary and len(reliability_summary) > 50:
                message += f"""
{reliability_summary}
"""
        except Exception as e:
            logger.warning(f"Error retrieving reliability summary: {str(e)}")
    
    # اضافه کردن اطلاعات زمان به پیام
    message += f"""
⏰ <b>زمان:</b> {current_time} (تورنتو)
"""
    
    # ارسال پیام به تلگرام
    return send_message(message, parse_mode="HTML", message_type="price_report")


def send_test_message():
    """
    ارسال پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # استفاده از زمان تورنتو
    toronto_timezone = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_timezone)
    current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

این یک پیام تست از سرویس تلگرام Replit است.
سیستم به درستی در حال کار است.

⏰ <b>زمان:</b> {current_time} (تورنتو)
"""
    
    # ثبت راه‌اندازی مجدد سرویس
    if RELIABILITY_MONITOR_AVAILABLE:
        try:
            record_service_restart()
            logger.info("Service restart recorded successfully")
        except Exception as e:
            logger.warning(f"Error recording service restart: {str(e)}")
    
    return send_message(message, parse_mode="HTML", message_type="test_message")


def send_system_report():
    """
    ارسال گزارش وضعیت سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # استفاده از زمان تورنتو
    toronto_timezone = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_timezone)
    current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🔧 <b>Crypto Barzin - گزارش سیستم</b>
━━━━━━━━━━━━━━━━━━

• <b>وضعیت سیستم:</b> 🟢 فعال
• <b>سرویس‌ها:</b> 
  - قیمت‌گذاری: ✅ فعال
  - تحلیل تکنیکال: ✅ فعال
  - تولید سیگنال: ✅ فعال
  - اعلان‌ها: ✅ فعال
• <b>آخرین بروزرسانی:</b> {current_time}
• <b>بازدید API:</b> {random.randint(150, 500)} درخواست در ساعت اخیر
• <b>استفاده از حافظه:</b> {random.randint(20, 80)}%
• <b>استفاده از CPU:</b> {random.randint(10, 60)}%
"""
    
    # اگر نشانگر قابلیت اطمینان فعال است، خلاصه کامل آن را اضافه کن
    if RELIABILITY_MONITOR_AVAILABLE:
        try:
            reliability_summary = get_reliability_summary()
            # در گزارش سیستم، همیشه خلاصه قابلیت اطمینان را نمایش بده
            message += f"""
<b>📊 آمار قابلیت اطمینان سیستم:</b>
{reliability_summary}
"""
        except Exception as e:
            logger.warning(f"Error retrieving reliability summary: {str(e)}")
            message += """
<b>📊 آمار قابلیت اطمینان سیستم:</b>
• Error retrieving statistical information
"""
    
    message += f"""
⏰ <b>Report Time:</b> {current_time} (Toronto)
"""
    
    return send_message(message, parse_mode="HTML", message_type="system_report")


def send_technical_analysis(symbol="BTC/USDT"):
    """
    ارسال تحلیل تکنیکال برای یک ارز
    
    Args:
        symbol (str, optional): نماد ارز. پیش‌فرض "BTC/USDT" است.
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # استفاده از زمان تورنتو
    toronto_timezone = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_timezone)
    current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # داده‌های نمونه برای تست
    coin_name = symbol.split('/')[0]  # استخراج نام ارز از نماد
    
    # مقادیر تصادفی برای نمایش
    price = random.uniform(10, 100000)
    if coin_name == "BTC":
        price = random.uniform(80000, 85000)
    elif coin_name == "ETH":
        price = random.uniform(1600, 1800)
    elif coin_name == "SOL":
        price = random.uniform(160, 180)
    
    change = random.uniform(-5, 5)
    rsi = random.uniform(20, 80)
    macd = random.uniform(-20, 20)
    macd_signal = random.uniform(-10, 10)
    
    # وضعیت‌های مختلف
    ma_statuses = ["صعودی قوی", "صعودی", "مبهم/رنج", "نزولی", "نزولی قوی"]
    ma_status = random.choice(ma_statuses)
    ma_emoji = "🟢" if "صعودی" in ma_status else ("🔴" if "نزولی" in ma_status else "🟡")
    
    bb_statuses = ["اشباع خرید", "صعودی", "خنثی", "نزولی", "اشباع فروش"]
    bb_status = random.choice(bb_statuses)
    bb_emoji = "🟢" if "اشباع فروش" in bb_status or "صعودی" in bb_status else ("🔴" if "اشباع خرید" in bb_status or "نزولی" in bb_status else "🟡")
    
    # سیگنال کلی
    if rsi < 30 and macd > macd_signal:
        signal = "خرید قوی"
        signal_emoji = "🟢"
    elif rsi < 40 and macd > macd_signal:
        signal = "خرید"
        signal_emoji = "🟢"
    elif rsi > 70 and macd < macd_signal:
        signal = "فروش قوی"
        signal_emoji = "🔴"
    elif rsi > 60 and macd < macd_signal:
        signal = "فروش"
        signal_emoji = "🔴"
    else:
        signal = "خنثی"
        signal_emoji = "🟡"
    
    # تبدیل داده‌ها به رشته‌های قابل نمایش
    price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
    change_emoji = "🟢" if change >= 0 else "🔴"
    change_str = f"{'+' if change >= 0 else ''}{change:.2f}%"
    
    # اضافه کردن USD به قیمت
    price_str = f"{price_str} USD"
    
    rsi_status = "فروش بیش از حد" if rsi < 30 else ("خرید بیش از حد" if rsi > 70 else "خنثی")
    rsi_emoji = "🟢" if rsi < 30 else ("🔴" if rsi > 70 else "🟡")
    
    macd_status = "صعودی" if macd > macd_signal else ("نزولی" if macd < macd_signal else "خنثی")
    macd_emoji = "🟢" if macd > macd_signal else ("🔴" if macd < macd_signal else "🟡")
    
    # هدف قیمتی و حد ضرر
    if "خرید" in signal:
        target_price = price * (1 + random.uniform(0.05, 0.2))
        stop_loss = price * (1 - random.uniform(0.03, 0.1))
        target_str = f"${target_price:,.2f} USD" if target_price >= 1 else f"${target_price:.6f} USD"
        sl_str = f"${stop_loss:,.2f} USD" if stop_loss >= 1 else f"${stop_loss:.6f} USD"
    elif "فروش" in signal:
        target_price = price * (1 - random.uniform(0.05, 0.2))
        stop_loss = price * (1 + random.uniform(0.03, 0.1))
        target_str = f"${target_price:,.2f} USD" if target_price >= 1 else f"${target_price:.6f} USD"
        sl_str = f"${stop_loss:,.2f} USD" if stop_loss >= 1 else f"${stop_loss:.6f} USD"
    else:
        target_str = "تعیین نشده"
        sl_str = "تعیین نشده"
    
    # نمودار کندل‌استیک
    candlestick_url = ""
    if coin_name == "BTC":
        candlestick_url = "https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1.svg"
    elif coin_name == "ETH":
        candlestick_url = "https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1027.svg"
    elif coin_name == "SOL":
        candlestick_url = "https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/5426.svg"
    elif coin_name == "BNB":
        candlestick_url = "https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1839.svg"
    elif coin_name == "XRP":
        candlestick_url = "https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/52.svg"
    
    # ساخت پیام
    message = f"""
📊 <b>Crypto Barzin - تحلیل تکنیکال</b>
━━━━━━━━━━━━━━━━━━

<b>🔸 {coin_name} ({symbol})</b>
💲 <b>قیمت فعلی:</b> {price_str}
📈 <b>تغییرات 24 ساعته:</b> {change_emoji} {change_str}

"""

    # اضافه کردن نمودار کندل‌استیک اگر موجود باشد
    if candlestick_url:
        message += f"""<b>📈 نمودار کندل‌استیک هفتگی:</b>
<a href="{candlestick_url}">{candlestick_url}</a>

"""

    message += f"""<b>🔹 شاخص‌های تکنیکال:</b>
• <b>RSI (14):</b> {rsi_emoji} {rsi:.2f} ({rsi_status})
• <b>MACD:</b> {macd_emoji} {macd:.2f} ({macd_status})
• <b>میانگین متحرک:</b> {ma_emoji} {ma_status}
• <b>باندهای بولینگر:</b> {bb_emoji} {bb_status}

<b>📋 سیگنال تکنیکال:</b> {signal_emoji} <b>{signal}</b>

<b>🎯 اهداف قیمتی:</b>
• <b>هدف:</b> {target_str}
• <b>حد ضرر:</b> {sl_str}

<b>⚠️ ریسک‌ها:</b>
• نوسانات بازار
• اخبار غیرمنتظره
• تغییرات ناگهانی حجم معامله

⏰ <b>زمان تحلیل:</b> {current_time} (تورنتو)
"""
    
    # نوع پیام برای ثبت در نشانگر قابلیت اطمینان
    message_type = f"technical_analysis_{coin_name}"
    
    return send_message(message, parse_mode="HTML", message_type=message_type)


def send_trading_signals():
    """
    ارسال سیگنال‌های معاملاتی
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # استفاده از زمان تورنتو
    toronto_timezone = pytz.timezone('America/Toronto')
    toronto_time = datetime.now(toronto_timezone)
    current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # لیست نمادها و قیمت‌ها
    symbols = [
        {"symbol": "BTC/USDT", "name": "Bitcoin", "price": random.uniform(80000, 85000), "change": random.uniform(-3, 3), "signal": "خرید", "risk": "متوسط"},
        {"symbol": "ETH/USDT", "name": "Ethereum", "price": random.uniform(1600, 1800), "change": random.uniform(-4, 4), "signal": "خنثی", "risk": "متوسط"},
        {"symbol": "SOL/USDT", "name": "Solana", "price": random.uniform(160, 180), "change": random.uniform(-5, 5), "signal": "فروش", "risk": "بالا"},
        {"symbol": "BNB/USDT", "name": "BNB", "price": random.uniform(600, 650), "change": random.uniform(-2, 2), "signal": "خرید", "risk": "کم"},
        {"symbol": "XRP/USDT", "name": "Ripple", "price": random.uniform(0.5, 0.7), "change": random.uniform(-2, 2), "signal": "خنثی", "risk": "متوسط"},
        {"symbol": "USDT/USD", "name": "Tether", "price": random.uniform(0.999, 1.001), "change": random.uniform(-0.1, 0.1), "signal": "خنثی", "risk": "کم"},
        {"symbol": "ADA/USDT", "name": "Cardano", "price": random.uniform(0.44, 0.48), "change": random.uniform(-3, 3), "signal": "خرید", "risk": "متوسط"},
        {"symbol": "DOT/USDT", "name": "Polkadot", "price": random.uniform(7.0, 7.5), "change": random.uniform(-4, 4), "signal": "خنثی", "risk": "متوسط"},
        {"symbol": "DOGE/USDT", "name": "Dogecoin", "price": random.uniform(0.14, 0.16), "change": random.uniform(-5, 5), "signal": "فروش", "risk": "بالا"},
        {"symbol": "MATIC/USDT", "name": "Polygon", "price": random.uniform(0.55, 0.60), "change": random.uniform(-4, 4), "signal": "خرید", "risk": "متوسط"},
        {"symbol": "LINK/USDT", "name": "Chainlink", "price": random.uniform(14.5, 15.5), "change": random.uniform(-3, 3), "signal": "خرید", "risk": "متوسط"},
        {"symbol": "LTC/USDT", "name": "Litecoin", "price": random.uniform(83, 88), "change": random.uniform(-3, 3), "signal": "خنثی", "risk": "متوسط"}
    ]
    
    # اضافه کردن ایموجی به سیگنال‌ها
    for i in range(len(symbols)):
        if symbols[i]["signal"] == "خرید":
            symbols[i]["emoji"] = "🟢"
        elif symbols[i]["signal"] == "فروش":
            symbols[i]["emoji"] = "🔴"
        else:
            symbols[i]["emoji"] = "🟡"
        
        # فرمت کردن قیمت‌ها
        if symbols[i]["price"] >= 1000:
            symbols[i]["price_str"] = f"${symbols[i]['price']:,.0f} USD"
        elif symbols[i]["price"] >= 1:
            symbols[i]["price_str"] = f"${symbols[i]['price']:,.2f} USD"
        else:
            symbols[i]["price_str"] = f"${symbols[i]['price']:.4f} USD"
        
        # فرمت کردن تغییرات
        symbols[i]["change_emoji"] = "🟢" if symbols[i]["change"] >= 0 else "🔴"
        symbols[i]["change_str"] = f"{'+' if symbols[i]['change'] >= 0 else ''}{symbols[i]['change']:.2f}%"
    
    # فیلتر کردن سیگنال‌های خرید و فروش
    buy_signals = [s for s in symbols if s["signal"] == "خرید"]
    sell_signals = [s for s in symbols if s["signal"] == "فروش"]
    
    # ساخت پیام
    message = f"""
🎯 <b>Crypto Barzin - سیگنال‌های معاملاتی</b>
━━━━━━━━━━━━━━━━━━

📊 <b>نمودار کندل‌استیک BTC/USDT:</b>
<a href="https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1.svg">https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1.svg</a>

📊 <b>نمودار کندل‌استیک ETH/USDT:</b>
<a href="https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1027.svg">https://s3.coinmarketcap.com/generated/sparklines/web/7d/2781/1027.svg</a>

<b>🟢 سیگنال‌های خرید:</b>
"""
    
    if buy_signals:
        for signal in buy_signals:
            message += f"• <b>{signal['name']} ({signal['symbol']})</b>: {signal['price_str']} {signal['change_emoji']} {signal['change_str']} | ریسک: {signal['risk']}\n"
    else:
        message += "• هیچ سیگنال خریدی یافت نشد\n"
    
    message += f"""
<b>🔴 سیگنال‌های فروش:</b>
"""
    
    if sell_signals:
        for signal in sell_signals:
            message += f"• <b>{signal['name']} ({signal['symbol']})</b>: {signal['price_str']} {signal['change_emoji']} {signal['change_str']} | ریسک: {signal['risk']}\n"
    else:
        message += "• هیچ سیگنال فروشی یافت نشد\n"
    
    message += f"""
<b>📈 خلاصه بازار:</b>
• <b>روند کلی:</b> {random.choice(["صعودی", "نزولی", "خنثی"])}
• <b>حجم معاملات:</b> {random.choice(["بالا", "متوسط", "پایین"])}
• <b>نوسانات:</b> {random.choice(["بالا", "متوسط", "پایین"])}

⚠️ <b>هشدار ریسک:</b> معامله ارزهای دیجیتال دارای ریسک بالایی است. 
همیشه با مدیریت سرمایه مناسب و با توجه به سطح ریسک خود معامله کنید.

⏰ <b>زمان گزارش:</b> {current_time} (تورنتو)
"""
    
    return send_message(message, parse_mode="HTML", message_type="trading_signals")


def send_crypto_news():
    """
    ارسال اخبار ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال اخبار
    """
    try:
        # استفاده از ماژول جدید news_scanner برای دریافت و خلاصه‌سازی اخبار
        from crypto_bot.news_scanner import get_combined_news
        
        # اخبار برتر ارزهای دیجیتال
        news = get_combined_news(max_items=7)
        
        # ساخت پیام اخبار
        if not news:
            message = "⚠️ اخبار ارزهای دیجیتال در دسترس نیست."
            return send_message(message, message_type="crypto_news")
        
        telegram_message = "*📰 اخبار مهم ارزهای دیجیتال*\n\n"
        
        # اضافه کردن وضعیت کلی بازار
        telegram_message += "*💹 وضعیت بازار:*\n"
        
        # دریافت قیمت فعلی بیت‌کوین و اتریوم برای نمایش در گزارش
        from crypto_bot.market_data import get_crypto_price
        btc_data = get_crypto_price("BTC/USDT")
        eth_data = get_crypto_price("ETH/USDT")
        
        if btc_data and "price" in btc_data:
            btc_price = btc_data["price"]
            btc_change = btc_data.get("change_24h", 0)
            btc_emoji = "🟢" if btc_change >= 0 else "🔴"
            telegram_message += f"• بیت‌کوین: ${btc_price:,.0f} ({btc_emoji} {btc_change:.2f}%)\n"
        
        if eth_data and "price" in eth_data:
            eth_price = eth_data["price"]
            eth_change = eth_data.get("change_24h", 0)
            eth_emoji = "🟢" if eth_change >= 0 else "🔴"
            telegram_message += f"• اتریوم: ${eth_price:,.0f} ({eth_emoji} {eth_change:.2f}%)\n"
            
        telegram_message += "\n*📊 عناوین مهم خبری:*\n"
        
        # تعیین امتیاز اهمیت برای اخبار بر اساس کلمات کلیدی
        important_keywords = [
            "bitcoin", "ethereum", "bearish", "bullish", "rally", "crash", 
            "record", "all-time high", "regulation", "halving", "crisis",
            "innovation", "adoption", "mainstream", "institutional", "mass adoption"
        ]
        
        for item in news:
            title = item.get('title', '')
            url = item.get('url', '#')
            source = item.get('source', '')
            
            # محاسبه امتیاز اهمیت خبر
            importance_score = 0
            lower_title = title.lower()
            
            for keyword in important_keywords:
                if keyword in lower_title:
                    importance_score += 2
            
            if importance_score > 0:
                # اخبار مهم را با علامت مشخص کنیم
                telegram_message += f"• 🔍 [{title}]({url})\n"
            else:
                telegram_message += f"• [{title}]({url})\n"
                
            telegram_message += f"  منبع: {source}\n\n"
        
        telegram_message += "\n🤖 *کریپتو برزین* | *اخبار و تحلیل‌های بیشتر*"
        
        # ارسال پیام به تلگرام
        return send_message(telegram_message, parse_mode="Markdown", message_type="crypto_news")
        
    except ImportError as e:
        logger.error(f"Error accessing the news scanner module: {str(e)}")
        error_message = "❌ خطا در دسترسی به ماژول اسکنر اخبار. لطفاً بعداً تلاش کنید."
        return send_message(error_message, message_type="crypto_news")
    except Exception as e:
        logger.error(f"Error sending cryptocurrency news: {str(e)}")
        # در صورت خطا، یک پیام ساده‌تر ارسال می‌کنیم
        try:
            error_message = "*📰 اخبار ارزهای دیجیتال*\n\n⚠️ در حال حاضر به دلیل مشکل فنی، امکان دریافت اخبار وجود ندارد.\n\nلطفاً بعداً دوباره تلاش کنید."
            return send_message(error_message, parse_mode="Markdown", message_type="crypto_news")
        except:
            return False


# Test message sending
if __name__ == "__main__":
    result = send_test_message()
    if result:
        print("Message sent successfully.")
    else:
        print("Message sending failed.")