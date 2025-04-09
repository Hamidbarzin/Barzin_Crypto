#!/usr/bin/env python3
"""
گزارش‌دهنده ۱۰ دقیقه‌ای تلگرام با استفاده از روش HTTP مستقیم

این اسکریپت هر ۱۰ دقیقه یک گزارش از قیمت‌ها و وضعیت بازار را به تلگرام ارسال می‌کند،
با استفاده از ماژول‌های ساده ارسال پیام و قالب‌بندی.

اجرا به‌صورت مستقل:
python new_ten_minute_reporter.py

اجرا به‌عنوان سرویس در پس‌زمینه:
nohup python new_ten_minute_reporter.py > new_ten_minute_reporter.log 2>&1 &
"""

import os
import time
import logging
import random
import atexit
import signal
import sys
from datetime import datetime, timedelta

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("new_ten_minute_reporter.log")
    ]
)
logger = logging.getLogger("new_ten_minute_reporter")

# تلاش برای واردسازی ماژول‌های ساده
try:
    import simple_telegram_sender as telegram
    import simple_telegram_formatter as formatter
    logger.info("ماژول‌های تلگرام با موفقیت بارگذاری شدند")
except ImportError as e:
    logger.error(f"خطا در بارگذاری ماژول‌های تلگرام: {str(e)}")
    sys.exit(1)

def get_random_price_data():
    """
    تولید داده‌های قیمت تصادفی برای تست (در نسخه نهایی باید با داده‌های واقعی جایگزین شود)
    
    Returns:
        dict: دیکشنری قیمت‌های تصادفی
    """
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT"]
    prices = {}
    
    for symbol in symbols:
        if "BTC" in symbol:
            base_price = random.uniform(60000, 70000)
        elif "ETH" in symbol:
            base_price = random.uniform(3000, 4000)
        elif "BNB" in symbol:
            base_price = random.uniform(500, 600)
        elif "XRP" in symbol:
            base_price = random.uniform(0.45, 0.55)
        elif "SOL" in symbol:
            base_price = random.uniform(130, 150)
        else:
            base_price = random.uniform(1, 100)
            
        change = random.uniform(-5, 5)
        
        prices[symbol] = {
            'price': base_price,
            'change_24h': change
        }
    
    return prices

def get_random_technical_data(symbol="BTC/USDT"):
    """
    تولید داده‌های تحلیل تکنیکال تصادفی برای تست
    
    Args:
        symbol (str): نماد ارز
        
    Returns:
        dict: دیکشنری داده‌های تحلیل تکنیکال
    """
    # قیمت تصادفی بر اساس نماد
    if "BTC" in symbol:
        price = random.uniform(60000, 70000)
    elif "ETH" in symbol:
        price = random.uniform(3000, 4000)
    elif "BNB" in symbol:
        price = random.uniform(500, 600)
    elif "XRP" in symbol:
        price = random.uniform(0.45, 0.55)
    elif "SOL" in symbol:
        price = random.uniform(130, 150)
    else:
        price = random.uniform(1, 100)
        
    change = random.uniform(-5, 5)
    rsi = random.uniform(20, 80)
    macd = random.uniform(-10, 10)
    macd_signal = random.uniform(-10, 10)
    
    # وضعیت میانگین‌های متحرک
    ma_statuses = ["صعودی قوی", "صعودی", "مبهم/رنج", "نزولی", "نزولی قوی"]
    ma_status = random.choice(ma_statuses)
    
    # وضعیت باندهای بولینگر
    bb_statuses = ["اشباع خرید", "صعودی", "خنثی", "نزولی", "اشباع فروش"]
    bb_status = random.choice(bb_statuses)
    
    # سیگنال کلی
    if rsi < 30 and macd > macd_signal:
        signal = "خرید قوی"
    elif rsi < 40 and macd > macd_signal:
        signal = "خرید"
    elif rsi > 70 and macd < macd_signal:
        signal = "فروش قوی"
    elif rsi > 60 and macd < macd_signal:
        signal = "فروش"
    else:
        signal = "خنثی"
    
    return {
        'price': price,
        'change_24h': change,
        'rsi': rsi,
        'macd': macd,
        'macd_signal': macd_signal,
        'ma_status': ma_status,
        'bb_status': bb_status,
        'signal': signal
    }

def get_random_signals():
    """
    تولید سیگنال‌های معاملاتی تصادفی برای تست
    
    Returns:
        list: لیست سیگنال‌ها
    """
    signals = []
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT"]
    selected_symbols = random.sample(symbols, random.randint(1, 3))
    
    for symbol in selected_symbols:
        # قیمت تصادفی بر اساس نماد
        if "BTC" in symbol:
            price = random.uniform(60000, 70000)
        elif "ETH" in symbol:
            price = random.uniform(3000, 4000)
        elif "BNB" in symbol:
            price = random.uniform(500, 600)
        elif "XRP" in symbol:
            price = random.uniform(0.45, 0.55)
        elif "SOL" in symbol:
            price = random.uniform(130, 150)
        else:
            price = random.uniform(1, 100)
            
        # نوع سیگنال
        action = random.choice(["خرید", "فروش"])
        
        # هدف قیمتی و حد ضرر
        if action == "خرید":
            target = price * (1 + random.uniform(0.05, 0.2))
            stop_loss = price * (1 - random.uniform(0.03, 0.08))
        else:
            target = price * (1 - random.uniform(0.05, 0.2))
            stop_loss = price * (1 + random.uniform(0.03, 0.08))
        
        signals.append({
            'symbol': symbol,
            'action': action,
            'price': price,
            'target': target,
            'stop_loss': stop_loss
        })
    
    return signals

def send_periodic_report():
    """
    ارسال گزارش دوره‌ای به تلگرام
    
    Returns:
        bool: موفقیت یا شکست ارسال گزارش
    """
    logger.info("ارسال گزارش دوره‌ای")
    
    try:
        # دریافت داده‌ها (در این نسخه از داده‌های تصادفی استفاده می‌کنیم)
        prices = get_random_price_data()
        
        # ارسال گزارش بازار
        logger.info("ارسال گزارش کلی بازار")
        market_result = formatter.send_market_overview(prices)
        logger.info(f"نتیجه ارسال گزارش بازار: {market_result}")
        
        # انتخاب یک ارز تصادفی برای تحلیل
        symbol = random.choice(list(prices.keys()))
        technical_data = get_random_technical_data(symbol)
        
        # ارسال تحلیل تکنیکال
        logger.info(f"ارسال تحلیل تکنیکال برای {symbol}")
        analysis_result = formatter.send_coin_analysis(symbol, technical_data)
        logger.info(f"نتیجه ارسال تحلیل تکنیکال: {analysis_result}")
        
        # ارسال سیگنال‌های معاملاتی
        logger.info("ارسال سیگنال‌های معاملاتی")
        signals = get_random_signals()
        signals_result = formatter.send_trading_signals(signals)
        logger.info(f"نتیجه ارسال سیگنال‌های معاملاتی: {signals_result}")
        
        return market_result and analysis_result and signals_result
        
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش دوره‌ای: {str(e)}")
        return False

def send_alive_message():
    """
    ارسال پیام زنده بودن سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    logger.info("ارسال پیام زنده بودن سیستم")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🤖 <b>وضعیت سیستم</b>
━━━━━━━━━━━━━━━━━━

سیستم گزارش‌دهی ۱۰ دقیقه‌ای در حال اجرا است.
نسخه جدید با روش HTTP مستقیم

⏰ <b>زمان کنونی:</b> {current_time}

این پیام به صورت خودکار هر 6 ساعت ارسال می‌شود.
گزارش‌های اصلی هر ۱۰ دقیقه یکبار ارسال می‌شوند.
        """
        
        result = telegram.send_message(text=message, parse_mode="HTML")
        logger.info(f"نتیجه ارسال پیام زنده بودن: {result}")
        return result
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام زنده بودن: {str(e)}")
        return False

def save_pid():
    """
    ذخیره شناسه فرآیند برای کنترل اجرا
    """
    with open("new_ten_minute_reporter.pid", "w") as f:
        f.write(str(os.getpid()))
    logger.info(f"شناسه فرآیند ذخیره شد: {os.getpid()}")

def cleanup_pid():
    """
    پاکسازی فایل PID هنگام خروج
    """
    try:
        os.remove("new_ten_minute_reporter.pid")
        logger.info("فایل PID پاکسازی شد")
    except Exception as e:
        logger.warning(f"خطا در پاکسازی فایل PID: {str(e)}")

def exit_handler():
    """
    مدیریت خروج از برنامه
    """
    logger.info("خروج از برنامه...")
    cleanup_pid()

def signal_handler(sig, frame):
    """
    مدیریت سیگنال‌های سیستم عامل
    """
    logger.info(f"سیگنال {sig} دریافت شد")
    sys.exit(0)

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع گزارش‌دهنده ۱۰ دقیقه‌ای")
    
    # ثبت تابع خروج
    atexit.register(exit_handler)
    
    # ثبت مدیریت سیگنال‌ها
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ذخیره شناسه فرآیند
    save_pid()
    
    # ارسال پیام تست اولیه برای اطمینان از عملکرد صحیح
    logger.info("ارسال پیام تست اولیه")
    test_result = formatter.send_test_message()
    logger.info(f"نتیجه ارسال پیام تست: {test_result}")
    
    # ارسال پیام زنده بودن سیستم
    send_alive_message()
    
    # ارسال گزارش اولیه
    send_periodic_report()
    
    # زمان آخرین ارسال گزارش
    last_report_time = datetime.now()
    last_alive_time = datetime.now()
    
    # حلقه اصلی برنامه
    logger.info("شروع حلقه اصلی برنامه")
    try:
        while True:
            # زمان فعلی
            now = datetime.now()
            
            # بررسی زمان ارسال گزارش دوره‌ای (هر ۱۰ دقیقه)
            if now - last_report_time >= timedelta(minutes=10):
                send_periodic_report()
                last_report_time = now
                
            # بررسی زمان ارسال پیام زنده بودن سیستم (هر ۶ ساعت)
            if now - last_alive_time >= timedelta(hours=6):
                send_alive_message()
                last_alive_time = now
                
            # انتظار برای یک دقیقه
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("برنامه با دستور کاربر متوقف شد")
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {str(e)}")
    
    logger.info("پایان گزارش‌دهنده ۱۰ دقیقه‌ای")

if __name__ == "__main__":
    main()