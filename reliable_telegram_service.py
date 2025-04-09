#!/usr/bin/env python3
"""
سرویس تلگرام با قابلیت اطمینان بالا
این اسکریپت به طور خودکار پیام‌های دوره‌ای به تلگرام ارسال می‌کند
"""

import os
import time
import logging
import random
import sys
from datetime import datetime, timedelta

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reliable_telegram.log")
    ]
)
logger = logging.getLogger("reliable_telegram")

# واردسازی ماژول‌های مورد نیاز
try:
    import requests
    logger.info("ماژول requests با موفقیت بارگذاری شد")
except ImportError:
    logger.error("خطا در بارگذاری ماژول requests")
    sys.exit(1)

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

def send_telegram_message(text, parse_mode="HTML"):
    """
    ارسال پیام به تلگرام با استفاده از درخواست HTTP مستقیم
    
    Args:
        text (str): متن پیام
        parse_mode (str): نوع پارس متن (HTML, Markdown یا None)
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    # API endpoint
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # پارامترهای درخواست
    params = {
        "chat_id": DEFAULT_CHAT_ID,
        "text": text,
        "disable_notification": False
    }
    
    # اضافه کردن parse_mode اگر مشخص شده باشد
    if parse_mode in ["HTML", "Markdown", "MarkdownV2"]:
        params["parse_mode"] = parse_mode
    
    try:
        logger.info(f"ارسال پیام به چت آیدی {DEFAULT_CHAT_ID}")
        response = requests.post(url, params=params)
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"پیام با موفقیت ارسال شد. شناسه پیام: {message_id}")
                return True
            else:
                error = result.get("description", "خطای ناشناخته")
                logger.error(f"خطا در ارسال پیام: {error}")
                return False
        else:
            logger.error(f"خطا در ارسال پیام: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def send_photo(photo_path=None, caption=""):
    """
    ارسال تصویر به تلگرام با استفاده از درخواست HTTP مستقیم
    
    Args:
        photo_path (str): مسیر فایل تصویر محلی
        caption (str): توضیحات تصویر
        
    Returns:
        bool: موفقیت یا شکست ارسال تصویر
    """
    if not photo_path:
        logger.error("خطا: هیچ تصویری برای ارسال مشخص نشده است")
        return False
        
    # API endpoint
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    # پارامترهای درخواست
    params = {
        "chat_id": DEFAULT_CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    try:
        logger.info(f"ارسال تصویر به چت آیدی {DEFAULT_CHAT_ID}")
        
        # ارسال فایل محلی
        with open(photo_path, "rb") as photo_file:
            response = requests.post(url, params=params, files={"photo": photo_file})
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"تصویر با موفقیت ارسال شد. شناسه پیام: {message_id}")
                return True
            else:
                error = result.get("description", "خطای ناشناخته")
                logger.error(f"خطا در ارسال تصویر: {error}")
                return False
        else:
            logger.error(f"خطا در ارسال تصویر: کد وضعیت {response.status_code}")
            logger.error(f"پاسخ: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال تصویر: {str(e)}")
        return False

def send_test_message():
    """
    ارسال پیام تست ساده
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

سیستم اعلان‌های تلگرام فعال است.
این پیام با استفاده از روش ساده ارسال شده است.

⏰ <b>زمان:</b> {current_time}
    """
    
    return send_telegram_message(message, parse_mode="HTML")

def send_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # نمونه قیمت‌ها (در نسخه نهایی باید با داده‌های واقعی جایگزین شود)
    coins = [
        {"symbol": "BTC", "name": "بیت‌کوین", "price": random.uniform(60000, 70000), "change": random.uniform(-3, 5)},
        {"symbol": "ETH", "name": "اتریوم", "price": random.uniform(3000, 4000), "change": random.uniform(-3, 5)},
        {"symbol": "BNB", "name": "بایننس کوین", "price": random.uniform(500, 600), "change": random.uniform(-3, 5)},
        {"symbol": "SOL", "name": "سولانا", "price": random.uniform(130, 150), "change": random.uniform(-3, 5)},
        {"symbol": "XRP", "name": "ریپل", "price": random.uniform(0.50, 0.55), "change": random.uniform(-3, 5)}
    ]
    
    message = f"""
💰 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

"""
    
    for coin in coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["price"]
        change = coin["change"]
        
        emoji = "🟢" if change >= 0 else "🔴"
        price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
        change_str = f"{change:+.2f}%"
        
        message += f"• {name} ({symbol}): {price_str} ({emoji} {change_str})\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return send_telegram_message(message, parse_mode="HTML")

def send_technical_analysis():
    """
    ارسال تحلیل تکنیکال یک ارز تصادفی
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # انتخاب یک ارز تصادفی
    coins = ["BTC", "ETH", "BNB", "SOL", "XRP"]
    coin = random.choice(coins)
    
    if coin == "BTC":
        name = "بیت‌کوین"
        price = random.uniform(60000, 70000)
    elif coin == "ETH":
        name = "اتریوم"
        price = random.uniform(3000, 4000)
    elif coin == "BNB":
        name = "بایننس کوین"
        price = random.uniform(500, 600)
    elif coin == "SOL":
        name = "سولانا"
        price = random.uniform(130, 150)
    else:  # XRP
        name = "ریپل"
        price = random.uniform(0.50, 0.55)
    
    # داده‌های تصادفی برای تحلیل
    change = random.uniform(-3, 5)
    rsi = random.uniform(20, 80)
    macd = random.uniform(-10, 10)
    macd_signal = random.uniform(-10, 10)
    
    # وضعیت‌های مختلف
    ma_statuses = ["صعودی قوی", "صعودی", "مبهم/رنج", "نزولی", "نزولی قوی"]
    ma_status = random.choice(ma_statuses)
    
    bb_statuses = ["اشباع خرید", "صعودی", "خنثی", "نزولی", "اشباع فروش"]
    bb_status = random.choice(bb_statuses)
    
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
    change_str = f"{change:+.2f}%"
    
    rsi_status = "فروش بیش از حد" if rsi < 30 else ("خرید بیش از حد" if rsi > 70 else "خنثی")
    rsi_emoji = "🟢" if rsi < 30 else ("🔴" if rsi > 70 else "🟡")
    
    macd_status = "صعودی" if macd > macd_signal else ("نزولی" if macd < macd_signal else "خنثی")
    macd_emoji = "🟢" if macd > macd_signal else ("🔴" if macd < macd_signal else "🟡")
    
    ma_emoji = "🟢" if "صعودی" in ma_status else ("🔴" if "نزولی" in ma_status else "🟡")
    bb_emoji = "🟢" if "اشباع فروش" in bb_status else ("🔴" if "اشباع خرید" in bb_status else "🟡")
    
    # هدف قیمتی و حد ضرر
    if "خرید" in signal:
        target = price * (1 + random.uniform(0.05, 0.2))
        target_str = f"${target:,.2f}" if target >= 1 else f"${target:.6f}"
        
        sl = price * (1 - random.uniform(0.03, 0.08))
        sl_str = f"${sl:,.2f}" if sl >= 1 else f"${sl:.6f}"
    else:
        target = None
        sl = None
    
    message = f"""
📊 <b>Crypto Barzin - تحلیل {name} ({coin})</b>
━━━━━━━━━━━━━━━━━━

💰 <b>قیمت فعلی:</b> {price_str} ({change_emoji} {change_str})

• <b>RSI:</b> {rsi:.2f} ({rsi_status} {rsi_emoji})
• <b>MACD:</b> {macd_status} {macd_emoji}
• <b>میانگین متحرک:</b> {ma_status} {ma_emoji}
• <b>باندهای بولینگر:</b> {bb_status} {bb_emoji}

🎯 <b>سیگنال کلی:</b> {signal} {signal_emoji}
"""
    
    if target is not None:
        message += f"🎯 <b>هدف قیمتی:</b> {target_str}\n"
        message += f"🛑 <b>حد ضرر:</b> {sl_str}\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return send_telegram_message(message, parse_mode="HTML")

def send_trading_signals():
    """
    ارسال سیگنال‌های معاملاتی
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
💰 <b>Crypto Barzin - سیگنال‌های معاملاتی</b>
━━━━━━━━━━━━━━━━━━

"""
    
    # تعداد تصادفی سیگنال (1 تا 3)
    signal_count = random.randint(1, 3)
    
    # لیست ارزها
    coins = [
        {"symbol": "BTC", "price": random.uniform(60000, 70000)},
        {"symbol": "ETH", "price": random.uniform(3000, 4000)},
        {"symbol": "BNB", "price": random.uniform(500, 600)},
        {"symbol": "SOL", "price": random.uniform(130, 150)},
        {"symbol": "XRP", "price": random.uniform(0.50, 0.55)}
    ]
    
    # انتخاب تصادفی ارزها برای سیگنال
    selected_coins = random.sample(coins, signal_count)
    
    for coin in selected_coins:
        symbol = coin["symbol"]
        price = coin["price"]
        
        # نوع سیگنال
        action = random.choice(["خرید", "فروش"])
        
        # هدف قیمتی و حد ضرر
        if action == "خرید":
            target = price * (1 + random.uniform(0.05, 0.2))
            stop_loss = price * (1 - random.uniform(0.03, 0.08))
            emoji = "🟢"
        else:
            target = price * (1 - random.uniform(0.05, 0.2))
            stop_loss = price * (1 + random.uniform(0.03, 0.08))
            emoji = "🔴"
        
        # تبدیل به رشته‌های قابل نمایش
        price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
        target_str = f"${target:,.2f}" if target >= 1 else f"${target:.6f}"
        stop_loss_str = f"${stop_loss:,.2f}" if stop_loss >= 1 else f"${stop_loss:.6f}"
        
        message += f"{emoji} <b>{action} {symbol}</b>\n"
        message += f"💲 قیمت ورود: {price_str}\n"
        message += f"🎯 هدف قیمتی: {target_str}\n"
        message += f"🛑 حد ضرر: {stop_loss_str}\n\n"
    
    message += f"⏰ <b>زمان:</b> {current_time}"
    
    return send_telegram_message(message, parse_mode="HTML")

def send_system_status():
    """
    ارسال گزارش وضعیت سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🤖 <b>Crypto Barzin - وضعیت سیستم</b>
━━━━━━━━━━━━━━━━━━

سیستم گزارش‌دهی تلگرام در حال اجرا است.
این پیام به صورت خودکار ارسال شده است.

گزارش‌های قیمت: هر ۳۰ دقیقه
تحلیل تکنیکال: هر ۱ ساعت
سیگنال‌های معاملاتی: هر ۴ ساعت

⏰ <b>زمان کنونی:</b> {current_time}
    """
    
    return send_telegram_message(message, parse_mode="HTML")

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع سرویس تلگرام قابل اطمینان")
    
    # ارسال پیام تست اولیه
    logger.info("ارسال پیام تست اولیه")
    test_result = send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # ارسال گزارش وضعیت سیستم
    logger.info("ارسال گزارش وضعیت سیستم")
    status_result = send_system_status()
    logger.info(f"نتیجه ارسال گزارش وضعیت: {status_result}")
    
    # ارسال گزارش اولیه برای آزمایش
    logger.info("ارسال گزارش قیمت اولیه")
    price_result = send_price_report()
    logger.info(f"نتیجه ارسال گزارش قیمت: {price_result}")
    
    # زمان آخرین ارسال گزارش‌ها
    last_price_report = datetime.now()
    last_technical_analysis = datetime.now()
    last_trading_signals = datetime.now()
    last_status_report = datetime.now()
    
    try:
        # حلقه اصلی برنامه
        logger.info("ورود به حلقه اصلی برنامه")
        while True:
            # زمان فعلی
            now = datetime.now()
            
            # بررسی زمان ارسال گزارش قیمت (هر ۳۰ دقیقه)
            if now - last_price_report >= timedelta(minutes=30):
                logger.info("ارسال گزارش قیمت")
                send_price_report()
                last_price_report = now
            
            # بررسی زمان ارسال تحلیل تکنیکال (هر ۱ ساعت)
            if now - last_technical_analysis >= timedelta(hours=1):
                logger.info("ارسال تحلیل تکنیکال")
                send_technical_analysis()
                last_technical_analysis = now
            
            # بررسی زمان ارسال سیگنال‌های معاملاتی (هر ۴ ساعت)
            if now - last_trading_signals >= timedelta(hours=4):
                logger.info("ارسال سیگنال‌های معاملاتی")
                send_trading_signals()
                last_trading_signals = now
            
            # بررسی زمان ارسال گزارش وضعیت سیستم (هر ۶ ساعت)
            if now - last_status_report >= timedelta(hours=6):
                logger.info("ارسال گزارش وضعیت سیستم")
                send_system_status()
                last_status_report = now
            
            # انتظار برای ۱ دقیقه
            logger.debug("انتظار برای دور بعدی...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
        # ارسال پیام خطا به تلگرام
        error_message = f"""
⚠️ <b>Crypto Barzin - خطا</b>
━━━━━━━━━━━━━━━━━━

خطایی در اجرای سیستم رخ داده است.
لطفاً لاگ‌ها را بررسی کنید.

خطا: {str(e)}

⏰ <b>زمان:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        send_telegram_message(error_message, parse_mode="HTML")
        raise

if __name__ == "__main__":
    main()