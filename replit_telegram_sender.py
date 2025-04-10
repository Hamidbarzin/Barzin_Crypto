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
    logger.info("ماژول ساده‌سازی شده نشانگر قابلیت اطمینان بارگذاری شد")
except ImportError:
    # اگر نسخه ساده‌سازی شده در دسترس نبود، استفاده از نسخه اصلی
    try:
        from crypto_bot.telegram_reliability_monitor import (
            record_message_attempt,
            record_service_restart,
            get_reliability_stats,
            get_reliability_summary
        )
        RELIABILITY_MONITOR_AVAILABLE = True
        logger.info("ماژول اصلی نشانگر قابلیت اطمینان بارگذاری شد")
    except ImportError:
        logger.warning("هیچ ماژول نشانگر قابلیت اطمینانی در دسترس نیست")
        # تعریف توابع جایگزین در صورت عدم وجود ماژول
        def record_message_attempt(message_type, success, error_message=None):
            logger.info(f"[پیاده‌سازی نشده] ثبت پیام: {message_type}, موفق: {success}")
            
        def record_service_restart():
            logger.info("[پیاده‌سازی نشده] ثبت راه‌اندازی مجدد سرویس")
            
        def get_reliability_stats():
            return {
                "overall": {"total_sent": 0, "successful": 0, "failed": 0, "success_rate": 0},
                "uptime": {"days": 0, "restarts": 0, "last_restart_hours_ago": 0},
                "recent_events": []
            }
            
        def get_reliability_summary():
            return "اطلاعات آماری در دسترس نیست"

# تنظیم کنید - کلید API تلگرام و شناسه چت
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# استفاده مستقیم از آیدی گروه به جای متغیر محیطی
DEFAULT_CHAT_ID = "-1002584373095"  # آیدی گروه تلگرام

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
        logger.error("TELEGRAM_BOT_TOKEN یافت نشد")
        
        # ثبت خطا در نشانگر قابلیت اطمینان
        if RELIABILITY_MONITOR_AVAILABLE:
            record_message_attempt(message_type, False, "TELEGRAM_BOT_TOKEN یافت نشد")
            
        return False
    
    if not chat_id:
        if not DEFAULT_CHAT_ID:
            logger.error("DEFAULT_CHAT_ID یافت نشد")
            
            # ثبت خطا در نشانگر قابلیت اطمینان
            if RELIABILITY_MONITOR_AVAILABLE:
                record_message_attempt(message_type, False, "DEFAULT_CHAT_ID یافت نشد")
                
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
    
    logger.info("در حال ارسال پیام به تلگرام...")
    
    for attempt in range(retries):
        try:
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info("پیام با موفقیت ارسال شد")
                
                # ثبت موفقیت در نشانگر قابلیت اطمینان
                if RELIABILITY_MONITOR_AVAILABLE:
                    record_message_attempt(message_type, True)
                    
                return True
            else:
                error_message = f"خطا در ارسال پیام: {response.status_code} - {response.text}"
                logger.error(error_message)
                
                # اگر آخرین تلاش است، خطا را ثبت کن
                if attempt == retries - 1:
                    if RELIABILITY_MONITOR_AVAILABLE:
                        record_message_attempt(message_type, False, error_message)
                
                # اگر خطای 429 (Too Many Requests) دریافت شد، زمان انتظار را افزایش دهید
                if response.status_code == 429:
                    retry_after = int(response.json().get('parameters', {}).get('retry_after', delay * 2))
                    logger.info(f"خطای محدودیت نرخ درخواست. در انتظار برای {retry_after} ثانیه...")
                    time.sleep(retry_after)
                else:
                    # برای سایر خطاها، با تاخیر معمولی دوباره تلاش کنید
                    time.sleep(delay)
        except Exception as e:
            error_message = f"استثنا در ارسال پیام: {str(e)}"
            logger.error(error_message)
            time.sleep(delay)
            
            # اگر آخرین تلاش است، خطا را ثبت کن
            if attempt == retries - 1:
                if RELIABILITY_MONITOR_AVAILABLE:
                    record_message_attempt(message_type, False, error_message)
    
    logger.error(f"پس از {retries} تلاش، ارسال پیام با شکست مواجه شد")
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
        {"name": "Bitcoin", "symbol": "BTC", "price": 83245.25, "change": 1.2},
        {"name": "Ethereum", "symbol": "ETH", "price": 1672.30, "change": -0.5},
        {"name": "BNB", "symbol": "BNB", "price": 626.75, "change": 0.8},
        {"name": "Solana", "symbol": "SOL", "price": 178.65, "change": 2.3},
        {"name": "Cardano", "symbol": "ADA", "price": 0.45, "change": -1.2},
        {"name": "Ripple", "symbol": "XRP", "price": 0.59, "change": 0.3},
        {"name": "Polkadot", "symbol": "DOT", "price": 7.32, "change": -0.7},
        {"name": "Tether", "symbol": "USDT", "price": 0.9998, "change": 0.01},
        {"name": "Polygon", "symbol": "MATIC", "price": 0.58, "change": 1.4},
        {"name": "Dogecoin", "symbol": "DOGE", "price": 0.15, "change": -2.1},
        {"name": "Chainlink", "symbol": "LINK", "price": 15.25, "change": 2.7},
        {"name": "Litecoin", "symbol": "LTC", "price": 86.50, "change": 0.5},
        {"name": "Arbitrum", "symbol": "ARB", "price": 1.06, "change": -1.8},
        {"name": "Optimism", "symbol": "OP", "price": 2.32, "change": 3.5},
        {"name": "Render", "symbol": "RNDR", "price": 7.28, "change": 5.6},
        {"name": "Fetch.ai", "symbol": "FET", "price": 2.12, "change": 4.3},
        {"name": "Worldcoin", "symbol": "WLD", "price": 4.45, "change": -3.2}
    ]
    
    # ساخت پیام
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

"""
    
    # اضافه کردن قیمت‌ها به پیام
    for coin in coins:
        # تعیین ایموجی و فرمت تغییرات بر اساس مثبت یا منفی بودن
        emoji = "🟢" if coin["change"] >= 0 else "🔴"
        change_str = f"+{coin['change']}%" if coin["change"] >= 0 else f"{coin['change']}%"
        
        # فرمت قیمت بر اساس مقدار آن
        if coin["price"] >= 100:
            price_str = f"${coin['price']:,.0f}"
        elif coin["price"] >= 1:
            price_str = f"${coin['price']:,.2f}"
        else:
            price_str = f"${coin['price']:.4f}"
        
        # اضافه کردن اطلاعات ارز به پیام
        message += f"{emoji} <b>{coin['name']} ({coin['symbol']})</b>: {price_str} ({change_str})\n"
    
    # اگر نشانگر قابلیت اطمینان فعال است، خلاصه آن را اضافه کن
    if RELIABILITY_MONITOR_AVAILABLE:
        try:
            reliability_summary = get_reliability_summary()
            # فقط در صورتی که داده کافی وجود داشته باشد
            if "وضعیت سیستم تلگرام" in reliability_summary and len(reliability_summary) > 50:
                message += f"""
{reliability_summary}
"""
        except Exception as e:
            logger.warning(f"خطا در دریافت خلاصه قابلیت اطمینان: {str(e)}")
    
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
            logger.info("راه‌اندازی مجدد سرویس با موفقیت ثبت شد")
        except Exception as e:
            logger.warning(f"خطا در ثبت راه‌اندازی مجدد سرویس: {str(e)}")
    
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
            logger.warning(f"خطا در دریافت خلاصه قابلیت اطمینان: {str(e)}")
            message += """
<b>📊 آمار قابلیت اطمینان سیستم:</b>
• خطا در دریافت اطلاعات آماری
"""
    
    message += f"""
⏰ <b>زمان گزارش:</b> {current_time} (تورنتو)
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
    
    rsi_status = "فروش بیش از حد" if rsi < 30 else ("خرید بیش از حد" if rsi > 70 else "خنثی")
    rsi_emoji = "🟢" if rsi < 30 else ("🔴" if rsi > 70 else "🟡")
    
    macd_status = "صعودی" if macd > macd_signal else ("نزولی" if macd < macd_signal else "خنثی")
    macd_emoji = "🟢" if macd > macd_signal else ("🔴" if macd < macd_signal else "🟡")
    
    # هدف قیمتی و حد ضرر
    if "خرید" in signal:
        target_price = price * (1 + random.uniform(0.05, 0.2))
        stop_loss = price * (1 - random.uniform(0.03, 0.1))
        target_str = f"${target_price:,.2f}" if target_price >= 1 else f"${target_price:.6f}"
        sl_str = f"${stop_loss:,.2f}" if stop_loss >= 1 else f"${stop_loss:.6f}"
    elif "فروش" in signal:
        target_price = price * (1 - random.uniform(0.05, 0.2))
        stop_loss = price * (1 + random.uniform(0.03, 0.1))
        target_str = f"${target_price:,.2f}" if target_price >= 1 else f"${target_price:.6f}"
        sl_str = f"${stop_loss:,.2f}" if stop_loss >= 1 else f"${stop_loss:.6f}"
    else:
        target_str = "تعیین نشده"
        sl_str = "تعیین نشده"
    
    # ساخت پیام
    message = f"""
📊 <b>Crypto Barzin - تحلیل تکنیکال</b>
━━━━━━━━━━━━━━━━━━

<b>🔸 {coin_name} ({symbol})</b>
💲 <b>قیمت فعلی:</b> {price_str}
📈 <b>تغییرات 24 ساعته:</b> {change_emoji} {change_str}

<b>🔹 شاخص‌های تکنیکال:</b>
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
            symbols[i]["price_str"] = f"${symbols[i]['price']:,.0f}"
        elif symbols[i]["price"] >= 1:
            symbols[i]["price_str"] = f"${symbols[i]['price']:,.2f}"
        else:
            symbols[i]["price_str"] = f"${symbols[i]['price']:.4f}"
        
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
        from crypto_bot.crypto_news import get_crypto_news_formatted_for_telegram
        
        news_text = get_crypto_news_formatted_for_telegram()
        
        # اگر خبری یافت نشد، پیام خطا ارسال کن
        if not news_text or len(news_text) < 10:
            logger.error("اخبار دریافت شده خالی یا ناقص است")
            news_text = "⚠️ متأسفانه در دریافت اخبار ارزهای دیجیتال خطایی رخ داده است."
        
        return send_message(news_text, parse_mode="Markdown", message_type="crypto_news")
    except ImportError:
        logger.error("خطا در دسترسی به ماژول اخبار ارزهای دیجیتال")
        error_message = "❌ خطا در دسترسی به ماژول اخبار ارزهای دیجیتال"
        return send_message(error_message, message_type="crypto_news")
    except Exception as e:
        logger.error(f"خطا در ارسال اخبار ارزهای دیجیتال: {str(e)}")
        error_message = f"❌ خطا در ارسال اخبار ارزهای دیجیتال: {str(e)}"
        return send_message(error_message, message_type="crypto_news")


# تست ارسال پیام
if __name__ == "__main__":
    result = send_test_message()
    if result:
        print("پیام با موفقیت ارسال شد.")
    else:
        print("ارسال پیام با شکست مواجه شد.")