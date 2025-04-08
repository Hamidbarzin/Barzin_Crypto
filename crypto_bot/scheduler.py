"""
ماژول زمان‌بندی وظایف خودکار

این ماژول برای زمان‌بندی وظایف دوره‌ای و خودکار کردن ارسال گزارش‌ها و هشدارها استفاده می‌شود.
"""

import os
import time
import logging
import threading
import schedule
from datetime import datetime

from crypto_bot.signal_generator import generate_signals, get_signals_summary
from crypto_bot.telegram_service import send_telegram_message
from crypto_bot.market_data import get_current_prices

logger = logging.getLogger(__name__)

# پیکربندی global برای اجرا یا توقف scheduler
_running = False
_scheduler_thread = None

def send_price_updates():
    """
    ارسال بروزرسانی قیمت‌های ارزهای دیجیتال اصلی
    """
    try:
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "BNB/USDT"]
        prices = get_current_prices(symbols=symbols)
        
        message = "💰 *قیمت‌های لحظه‌ای ارزهای دیجیتال*\n\n"
        
        for symbol in symbols:
            if symbol in prices:
                data = prices[symbol]
                if isinstance(data, dict) and 'price' in data:
                    price = data['price']
                    change_24h = data.get('change_24h', 0)
                    
                    # نمایش تغییرات با فرمت مناسب
                    change_emoji = "🟢" if change_24h >= 0 else "🔴"
                    change_sign = "+" if change_24h > 0 else ""
                    
                    message += f"{symbol}: {price:,.2f} USDT {change_emoji} {change_sign}{change_24h:.2f}%\n"
        
        message += f"\n⏱ بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if chat_id:
            send_telegram_message(chat_id=int(chat_id), message=message)
        else:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
    
    except Exception as e:
        logger.error(f"خطا در ارسال بروزرسانی قیمت‌ها: {str(e)}")

def send_trading_signals():
    """
    ارسال سیگنال‌های معاملاتی براساس تحلیل تکنیکال
    """
    try:
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"]
        
        signals = generate_signals(symbols)
        
        if not signals.get('buy') and not signals.get('sell'):
            logger.info("هیچ سیگنال معاملاتی قابل توجهی یافت نشد")
            return
        
        # تهیه خلاصه سیگنال‌ها
        summary = get_signals_summary(signals)
        
        # ارسال به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if chat_id:
            send_telegram_message(chat_id=int(chat_id), message=summary)
        else:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
    
    except Exception as e:
        logger.error(f"خطا در ارسال سیگنال‌های معاملاتی: {str(e)}")

def send_market_overview():
    """
    ارسال نمای کلی بازار شامل قیمت‌ها و روند کلی
    """
    try:
        # در اینجا می‌توان ترکیبی از قیمت‌ها و سیگنال‌ها را ارسال کرد
        # برای جلوگیری از تکرار، فعلاً فقط یک پیام ساده ارسال می‌کنیم
        
        message = "🌍 *نمای کلی بازار ارزهای دیجیتال*\n\n"
        
        # اضافه کردن روند کلی بازار (در اینجا به صورت ساده)
        symbols = ["BTC/USDT", "ETH/USDT"]
        prices = get_current_prices(symbols=symbols)
        
        # بررسی روند کلی بازار بر اساس بیت‌کوین و اتریوم
        btc_change = prices.get("BTC/USDT", {}).get("change_24h", 0)
        eth_change = prices.get("ETH/USDT", {}).get("change_24h", 0)
        
        avg_change = (btc_change + eth_change) / 2
        
        if avg_change > 3:
            market_status = "صعودی قوی 📈📈"
        elif avg_change > 1:
            market_status = "صعودی 📈"
        elif avg_change > -1:
            market_status = "خنثی ↔️"
        elif avg_change > -3:
            market_status = "نزولی 📉"
        else:
            market_status = "نزولی قوی 📉📉"
            
        message += f"وضعیت کلی بازار: {market_status}\n"
        message += f"میانگین تغییرات 24 ساعته: {avg_change:.2f}%\n\n"
        
        # اضافه کردن قیمت‌های فعلی چند ارز مهم
        message += "قیمت‌های فعلی:\n"
        for symbol, data in prices.items():
            if isinstance(data, dict) and 'price' in data:
                price = data['price']
                change = data.get('change_24h', 0)
                change_sign = "+" if change > 0 else ""
                message += f"{symbol}: {price:,.2f} USDT ({change_sign}{change:.2f}%)\n"
                
        message += f"\n⏱ بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if chat_id:
            send_telegram_message(chat_id=int(chat_id), message=message)
        else:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
    
    except Exception as e:
        logger.error(f"خطا در ارسال نمای کلی بازار: {str(e)}")

def send_alive_message():
    """
    ارسال پیام برای نشان دادن فعال بودن سیستم
    """
    try:
        message = "🤖 *سیستم پیام‌رسانی تلگرام فعال است*\n\n"
        message += f"زمان فعلی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال به تلگرام
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if chat_id:
            send_telegram_message(chat_id=int(chat_id), message=message)
        else:
            logger.error("چت آیدی پیش‌فرض تنظیم نشده است")
    
    except Exception as e:
        logger.error(f"خطا در ارسال پیام وضعیت سیستم: {str(e)}")

def _setup_schedule():
    """
    تنظیم زمان‌بندی وظایف
    """
    # پاک کردن زمان‌بندی‌های قبلی
    schedule.clear()
    
    # زمان‌بندی جدید
    schedule.every(30).minutes.do(send_price_updates)
    schedule.every(2).hours.do(send_trading_signals)
    schedule.every(4).hours.do(send_market_overview)
    schedule.every(12).hours.do(send_alive_message)
    
    # ارسال یک پیام در شروع کار برای اطمینان از عملکرد صحیح
    send_alive_message()
    
    logger.info("زمان‌بندی با موفقیت تنظیم شد")

def _run_scheduler():
    """
    اجرای زمان‌بندی در یک حلقه
    این تابع در یک thread جداگانه اجرا می‌شود
    """
    global _running
    logger.info("زمان‌بندی شروع به کار کرد")
    
    while _running:
        schedule.run_pending()
        time.sleep(1)
    
    logger.info("زمان‌بندی متوقف شد")

def start_scheduler():
    """
    شروع زمان‌بندی
    """
    global _running, _scheduler_thread
    
    if _running:
        return {"status": "warning", "message": "زمان‌بندی در حال حاضر فعال است"}
    
    _running = True
    _setup_schedule()
    
    _scheduler_thread = threading.Thread(target=_run_scheduler)
    _scheduler_thread.daemon = True
    _scheduler_thread.start()
    
    return {"status": "success", "message": "زمان‌بندی با موفقیت شروع شد"}

def stop_scheduler():
    """
    توقف زمان‌بندی
    """
    global _running, _scheduler_thread
    
    if not _running:
        return {"status": "warning", "message": "زمان‌بندی در حال حاضر متوقف است"}
    
    _running = False
    if _scheduler_thread:
        _scheduler_thread.join(timeout=5)
    
    return {"status": "success", "message": "زمان‌بندی با موفقیت متوقف شد"}

def get_scheduler_status():
    """
    دریافت وضعیت فعلی زمان‌بندی
    """
    global _running
    
    jobs = []
    for job in schedule.get_jobs():
        jobs.append({
            "name": job.job_func.__name__,
            "interval": str(job.interval),
            "next_run": job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else None
        })
    
    return {
        "running": _running,
        "jobs": jobs
    }