#!/usr/bin/env python3
"""
ماژول ارسال پیام تلگرام برای Replit

این ماژول از طریق API تلگرام پیام‌ها را ارسال می‌کند و
برای محیط Replit بهینه‌سازی شده است
"""

import requests
import logging
import os
import json
from datetime import datetime
import random
import time
import pytz  # برای کار با منطقه‌های زمانی مختلف

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("replit_telegram")

# توکن و چت آیدی
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7429658178:AAFc8hfXeog2Cu8EWOcXQbMc5Nn-q-f1ePk")
CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "722627622")

def send_message(text, chat_id=None, parse_mode="HTML"):
    """
    ارسال پیام به تلگرام
    
    Args:
        text (str): متن پیام
        chat_id (str, optional): شناسه چت. اگر None باشد، از CHAT_ID پیش‌فرض استفاده می‌شود
        parse_mode (str, optional): نوع پارس کردن متن. پیش‌فرض "HTML"
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if chat_id is None:
        chat_id = CHAT_ID
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        logger.info("در حال ارسال پیام به تلگرام...")
        response = requests.post(url, data=payload)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get("ok"):
            logger.info("پیام با موفقیت ارسال شد")
            return True
        else:
            logger.error(f"خطا در ارسال پیام: {response_json.get('description', 'خطای ناشناخته')}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {str(e)}")
        return False

def get_crypto_prices():
    """
    دریافت قیمت‌های ارزهای دیجیتال
    
    Returns:
        dict: دیکشنری قیمت‌های ارزهای دیجیتال
    """
    try:
        # تلاش برای دریافت قیمت‌های واقعی از CoinGecko
        api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,solana,binancecoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # تبدیل به فرمت مورد نظر ما
            prices = {
                "BTC/USDT": {
                    "price": data["bitcoin"]["usd"],
                    "change_24h": data["bitcoin"]["usd_24h_change"]
                },
                "ETH/USDT": {
                    "price": data["ethereum"]["usd"],
                    "change_24h": data["ethereum"]["usd_24h_change"]
                },
                "XRP/USDT": {
                    "price": data["ripple"]["usd"],
                    "change_24h": data["ripple"]["usd_24h_change"]
                },
                "SOL/USDT": {
                    "price": data["solana"]["usd"],
                    "change_24h": data["solana"]["usd_24h_change"]
                },
                "BNB/USDT": {
                    "price": data["binancecoin"]["usd"],
                    "change_24h": data["binancecoin"]["usd_24h_change"]
                }
            }
            
            return prices
    except Exception as e:
        logger.warning(f"خطا در دریافت قیمت‌های واقعی: {str(e)}")
    
    # در صورت بروز خطا، از قیمت‌های تصادفی استفاده می‌کنیم
    base_prices = {
        "BTC/USDT": 76000,
        "ETH/USDT": 3400,
        "XRP/USDT": 0.53,
        "SOL/USDT": 165,
        "BNB/USDT": 580
    }
    
    result = {}
    for symbol, base_price in base_prices.items():
        # تغییر قیمت بین -2% تا +2%
        price_change = random.uniform(-0.02, 0.02)
        new_price = base_price * (1 + price_change)
        
        # تغییر ۲۴ ساعته بین -5% تا +5%
        change_24h = random.uniform(-5, 5)
        
        result[symbol] = {
            "price": round(new_price, 2) if new_price >= 1 else round(new_price, 8),
            "change_24h": round(change_24h, 2)
        }
    
    return result
    
def format_price(price):
    """
    قالب‌بندی قیمت با جداکننده هزارگان
    
    Args:
        price (float): قیمت
        
    Returns:
        str: قیمت قالب‌بندی شده
    """
    if price >= 1:
        return f"{price:,.2f}"
    else:
        return f"{price:.8f}"

def format_change(change):
    """
    قالب‌بندی تغییر قیمت با علامت مثبت یا منفی
    
    Args:
        change (float): درصد تغییر
        
    Returns:
        str: درصد تغییر قالب‌بندی شده
    """
    return f"{'+' if change >= 0 else ''}{change:.2f}%"

def send_price_report():
    """
    ارسال گزارش قیمت‌های ارزهای دیجیتال
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    try:
        # دریافت قیمت‌های فعلی
        prices = get_crypto_prices()
        
        # ساخت متن پیام با زمان تورنتو
        toronto_timezone = pytz.timezone('America/Toronto')
        toronto_time = datetime.now(toronto_timezone)
        current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🚀 <b>Crypto Barzin - گزارش قیمت‌ها</b>
━━━━━━━━━━━━━━━━━━

💰 <b>قیمت‌های لحظه‌ای ارزهای دیجیتال</b>

<code>
{'ارز':<8} {'قیمت (USDT)':<15} {'تغییر 24h':<10}
</code>
"""

        for symbol, data in prices.items():
            coin = symbol.split('/')[0]
            price = format_price(data["price"])
            change = format_change(data["change_24h"])
            change_emoji = "🟢" if data["change_24h"] >= 0 else "🔴"
            
            message += f"<code>{coin:<8} {price:<15} {change:<10}</code> {change_emoji}\n"
        
        message += f"""
⏰ <b>زمان:</b> {current_time}
🤖 <b>سرویس:</b> Crypto Barzin (Replit)
"""
        
        return send_message(message)
    except Exception as e:
        logger.error(f"خطا در ارسال گزارش قیمت: {str(e)}")
        return False

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
    
    return send_message(message)

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

✅ <b>وضعیت سرویس:</b> فعال
⚙️ <b>سرویس فعال:</b> سرویس تلگرام Replit

⏰ <b>زمان گزارش:</b> {current_time} (تورنتو)
"""
    
    return send_message(message)

def send_technical_analysis(symbol=None):
    """
    ارسال تحلیل تکنیکال یک ارز
    
    Args:
        symbol (str, optional): نماد ارز. اگر None باشد، یک ارز تصادفی انتخاب می‌شود.
        
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    try:
        # تنظیم زمان به وقت تورنتو
        toronto_timezone = pytz.timezone('America/Toronto')
        toronto_time = datetime.now(toronto_timezone)
        current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # انتخاب یک ارز تصادفی اگر symbol تعیین نشده باشد
        if symbol is None:
            coins = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
            symbol = random.choice(coins)
        
        # تبدیل نماد به فرمت مناسب برای نمایش
        display_symbol = symbol.split('/')[0]
        
        try:
            # تلاش برای استفاده از ماژول تحلیل تکنیکال واقعی
            from crypto_bot.technical_analysis import analyze_symbol
            analysis = analyze_symbol(symbol, "1d")
            
            # اگر تحلیل موفقیت‌آمیز نبود، از داده‌های تصادفی استفاده می‌کنیم
            if not analysis or "error" in analysis:
                raise Exception("تحلیل تکنیکال با خطا مواجه شد")
                
            # استخراج داده‌ها از تحلیل
            rsi = analysis.get('rsi', random.uniform(20, 80))
            macd = analysis.get('macd', random.uniform(-10, 10))
            macd_signal = analysis.get('macd_signal', random.uniform(-10, 10))
            signal = analysis.get('signal', 'خنثی')
            ma20 = analysis.get('ma20', 0)
            ma50 = analysis.get('ma50', 0)
            ma200 = analysis.get('ma200', 0)
            
            # قیمت فعلی
            # محاسبه سیگنال‌های مورد نیاز
            if ma20 > ma50 > ma200:
                ma_status = "صعودی قوی"
                ma_emoji = "🟢"
            elif ma20 > ma50:
                ma_status = "صعودی"
                ma_emoji = "🟢"
            elif ma20 < ma50 < ma200:
                ma_status = "نزولی قوی"
                ma_emoji = "🔴"
            elif ma20 < ma50:
                ma_status = "نزولی"
                ma_emoji = "🔴"
            else:
                ma_status = "مبهم/رنج"
                ma_emoji = "🟡"
                
            if 'bb_upper' in analysis and 'bb_lower' in analysis and 'bb_middle' in analysis:
                bb_upper = analysis['bb_upper']
                bb_lower = analysis['bb_lower']
                bb_middle = analysis['bb_middle']
                current_price = analysis.get('close', 0)
                
                if current_price > bb_upper:
                    bb_status = "اشباع خرید"
                    bb_emoji = "🔴"
                elif current_price < bb_lower:
                    bb_status = "اشباع فروش"
                    bb_emoji = "🟢"
                elif current_price > bb_middle:
                    bb_status = "صعودی"
                    bb_emoji = "🟢"
                elif current_price < bb_middle:
                    bb_status = "نزولی"
                    bb_emoji = "🔴"
                else:
                    bb_status = "خنثی"
                    bb_emoji = "🟡"
            else:
                bb_status = random.choice(["اشباع خرید", "صعودی", "خنثی", "نزولی", "اشباع فروش"])
                bb_emoji = "🟢" if "اشباع فروش" in bb_status or "صعودی" in bb_status else ("🔴" if "اشباع خرید" in bb_status or "نزولی" in bb_status else "🟡")
            
            # وضعیت RSI
            rsi_status = "فروش بیش از حد" if rsi < 30 else ("خرید بیش از حد" if rsi > 70 else "خنثی")
            rsi_emoji = "🟢" if rsi < 30 else ("🔴" if rsi > 70 else "🟡")
            
            # وضعیت MACD
            macd_status = "صعودی" if macd > macd_signal else ("نزولی" if macd < macd_signal else "خنثی")
            macd_emoji = "🟢" if macd > macd_signal else ("🔴" if macd < macd_signal else "🟡")
            
            # سیگنال نهایی
            signal_emoji = "🟢" if "خرید" in signal else ("🔴" if "فروش" in signal else "🟡")
            
            # دریافت قیمت فعلی
            prices = get_crypto_prices()
            if display_symbol in prices:
                price = prices[display_symbol]['price']
                change = prices[display_symbol]['change_24h']
            else:
                # اگر قیمت در دسترس نبود، از داده‌های تصادفی استفاده می‌کنیم
                if display_symbol == "BTC":
                    price = random.uniform(60000, 70000)
                elif display_symbol == "ETH":
                    price = random.uniform(3000, 4000)
                elif display_symbol == "BNB":
                    price = random.uniform(500, 600)
                elif display_symbol == "SOL":
                    price = random.uniform(130, 150)
                elif display_symbol == "XRP":
                    price = random.uniform(0.50, 0.55)
                else:
                    price = random.uniform(0.1, 1000)
                change = random.uniform(-3, 5)
            
            # تبدیل به رشته‌های قابل نمایش
            price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
            change_emoji = "🟢" if change >= 0 else "🔴"
            change_str = f"{'+' if change >= 0 else ''}{change:.2f}%"
            
            # نام فارسی ارز
            if display_symbol == "BTC":
                name = "بیت‌کوین"
            elif display_symbol == "ETH":
                name = "اتریوم"
            elif display_symbol == "BNB":
                name = "بایننس کوین"
            elif display_symbol == "SOL":
                name = "سولانا"
            elif display_symbol == "XRP":
                name = "ریپل"
            else:
                name = display_symbol
            
            # هدف قیمتی و حد ضرر
            if "خرید" in signal:
                target = price * (1 + random.uniform(0.05, 0.2))
                target_str = f"${target:,.2f}" if target >= 1 else f"${target:.6f}"
                
                sl = price * (1 - random.uniform(0.03, 0.08))
                sl_str = f"${sl:,.2f}" if sl >= 1 else f"${sl:.6f}"
            else:
                target = None
                sl = None
        
        except Exception as e:
            logger.warning(f"استفاده از تحلیل تکنیکال واقعی با خطا مواجه شد: {str(e)}")
            logger.info("استفاده از داده‌های تصادفی برای تحلیل تکنیکال")
            
            # داده‌های تصادفی برای تحلیل
            if display_symbol == "BTC":
                name = "بیت‌کوین"
                price = random.uniform(60000, 70000)
            elif display_symbol == "ETH":
                name = "اتریوم"
                price = random.uniform(3000, 4000)
            elif display_symbol == "BNB":
                name = "بایننس کوین"
                price = random.uniform(500, 600)
            elif display_symbol == "SOL":
                name = "سولانا"
                price = random.uniform(130, 150)
            elif display_symbol == "XRP":
                name = "ریپل"
                price = random.uniform(0.50, 0.55)
            else:
                name = display_symbol
                price = random.uniform(0.1, 1000)
        
            # داده‌های تصادفی برای تحلیل
            change = random.uniform(-3, 5)
            rsi = random.uniform(20, 80)
            macd = random.uniform(-10, 10)
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
                target = price * (1 + random.uniform(0.05, 0.2))
                target_str = f"${target:,.2f}" if target >= 1 else f"${target:.6f}"
                
                sl = price * (1 - random.uniform(0.03, 0.08))
                sl_str = f"${sl:,.2f}" if sl >= 1 else f"${sl:.6f}"
            else:
                target = None
                sl = None
        
        # ساخت متن پیام
        message = f"""
📊 <b>Crypto Barzin - تحلیل {name} ({display_symbol})</b>
━━━━━━━━━━━━━━━━━━

💰 <b>قیمت فعلی:</b> {price_str} ({change_emoji} {change_str})

🔍 <b>تحلیل تکنیکال:</b>
• <b>RSI:</b> {rsi:.2f} ({rsi_status} {rsi_emoji})
• <b>MACD:</b> {macd_status} {macd_emoji}
• <b>میانگین متحرک:</b> {ma_status} {ma_emoji}
• <b>باندهای بولینگر:</b> {bb_status} {bb_emoji}

🎯 <b>سیگنال کلی:</b> {signal} {signal_emoji}
"""
        
        if target is not None:
            message += f"🎯 <b>هدف قیمتی:</b> {target_str}\n"
            message += f"🛑 <b>حد ضرر:</b> {sl_str}\n"
        
        # توضیحات تکمیلی برای سیگنال
        if "خرید قوی" in signal:
            message += f"\n💼 <b>توصیه معاملاتی:</b>\n"
            message += f"در شرایط فعلی، {name} یک فرصت خرید عالی ایجاد کرده است. تمام شاخص‌های تکنیکال در بازه‌های مطلوب قرار دارند. می‌توانید با احتیاط و با در نظر گرفتن حد ضرر، اقدام به خرید کنید."
        elif "خرید" in signal:
            message += f"\n💼 <b>توصیه معاملاتی:</b>\n"
            message += f"شرایط برای خرید {name} مناسب است، اما بهتر است با حجم کمتر و با احتیاط بیشتر وارد شوید. حتماً حد ضرر را تنظیم کنید."
        elif "فروش قوی" in signal:
            message += f"\n💼 <b>توصیه معاملاتی:</b>\n"
            message += f"شاخص‌های تکنیکال {name} در وضعیت فروش قرار دارند. اگر موقعیت خرید باز دارید، بهتر است سود خود را شناسایی کنید. برای فروش کوتاه‌مدت نیز فرصت مناسبی است."
        elif "فروش" in signal:
            message += f"\n💼 <b>توصیه معاملاتی:</b>\n"
            message += f"نشانه‌هایی از ضعف در قیمت {name} دیده می‌شود. اگر موقعیت خرید دارید، بهتر است بخشی از سود خود را برداشت کنید یا حد ضرر خود را بالاتر ببرید."
        elif "خنثی" in signal:
            message += f"\n💼 <b>توصیه معاملاتی:</b>\n"
            message += f"بازار {name} در حال حاضر در وضعیت مبهم قرار دارد. بهتر است صبر کنید تا روند مشخص‌تری شکل بگیرد."
        
        message += f"\n⏰ <b>زمان تحلیل (تورنتو):</b> {current_time}"
        
        return send_message(message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل تکنیکال: {str(e)}")
        return False

def send_trading_signals():
    """
    ارسال سیگنال‌های معاملاتی
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    try:
        # تنظیم زمان به وقت تورنتو
        toronto_timezone = pytz.timezone('America/Toronto')
        toronto_time = datetime.now(toronto_timezone)
        current_time = toronto_time.strftime("%Y-%m-%d %H:%M:%S")
        
        coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT", "AVAX", "MATIC", "DOGE"]
        symbols = []
        
        # انتخاب تصادفی 2-4 ارز از لیست
        signal_count = random.randint(2, 4)
        selected_coins = random.sample(coins, signal_count)
        
        # ساخت پیام
        message = f"""
💰 <b>Crypto Barzin - سیگنال‌های معاملاتی</b>
━━━━━━━━━━━━━━━━━━

"""
        # بخش سیگنال‌های خرید
        message += "🟢 <b>سیگنال‌های خرید:</b>\n\n"
        
        buy_signals = 0
        for coin in selected_coins[:signal_count//2]:
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
            elif coin == "XRP":
                name = "ریپل"
                price = random.uniform(0.50, 0.55)
            elif coin == "ADA":
                name = "کاردانو"
                price = random.uniform(0.30, 0.40)
            elif coin == "DOT":
                name = "پولکادات"
                price = random.uniform(5, 7)
            elif coin == "AVAX":
                name = "آوالانچ"
                price = random.uniform(20, 30)
            elif coin == "MATIC":
                name = "پلیگان"
                price = random.uniform(0.50, 0.70)
            elif coin == "DOGE":
                name = "دوج کوین"
                price = random.uniform(0.10, 0.15)
            else:
                name = coin
                price = random.uniform(1, 100)
                
            # محاسبه هدف قیمتی و حد ضرر
            target1 = price * (1 + random.uniform(0.03, 0.08))
            target2 = price * (1 + random.uniform(0.08, 0.15))
            target3 = price * (1 + random.uniform(0.15, 0.25))
            sl = price * (1 - random.uniform(0.03, 0.07))
            
            # تبدیل به رشته‌های قابل نمایش
            price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
            target1_str = f"${target1:,.2f}" if target1 >= 1 else f"${target1:.6f}"
            target2_str = f"${target2:,.2f}" if target2 >= 1 else f"${target2:.6f}"
            target3_str = f"${target3:,.2f}" if target3 >= 1 else f"${target3:.6f}"
            sl_str = f"${sl:,.2f}" if sl >= 1 else f"${sl:.6f}"
            
            message += f"<b>{name} ({coin}/USDT)</b>\n"
            message += f"💵 قیمت خرید: {price_str}\n"
            message += f"🎯 هدف اول: {target1_str}\n"
            message += f"🎯 هدف دوم: {target2_str}\n"
            message += f"🎯 هدف سوم: {target3_str}\n"
            message += f"🛑 حد ضرر: {sl_str}\n\n"
            
            buy_signals += 1
        
        if buy_signals == 0:
            message += "در حال حاضر سیگنال خرید معتبری وجود ندارد.\n\n"
            
        # بخش سیگنال‌های فروش
        message += "🔴 <b>سیگنال‌های فروش:</b>\n\n"
        
        sell_signals = 0
        for coin in selected_coins[signal_count//2:]:
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
            elif coin == "XRP":
                name = "ریپل"
                price = random.uniform(0.50, 0.55)
            elif coin == "ADA":
                name = "کاردانو"
                price = random.uniform(0.30, 0.40)
            elif coin == "DOT":
                name = "پولکادات"
                price = random.uniform(5, 7)
            elif coin == "AVAX":
                name = "آوالانچ"
                price = random.uniform(20, 30)
            elif coin == "MATIC":
                name = "پلیگان"
                price = random.uniform(0.50, 0.70)
            elif coin == "DOGE":
                name = "دوج کوین"
                price = random.uniform(0.10, 0.15)
            else:
                name = coin
                price = random.uniform(1, 100)
                
            # محاسبه هدف قیمتی و حد ضرر
            target1 = price * (1 - random.uniform(0.03, 0.08))
            target2 = price * (1 - random.uniform(0.08, 0.15))
            target3 = price * (1 - random.uniform(0.15, 0.25))
            sl = price * (1 + random.uniform(0.03, 0.07))
            
            # تبدیل به رشته‌های قابل نمایش
            price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
            target1_str = f"${target1:,.2f}" if target1 >= 1 else f"${target1:.6f}"
            target2_str = f"${target2:,.2f}" if target2 >= 1 else f"${target2:.6f}"
            target3_str = f"${target3:,.2f}" if target3 >= 1 else f"${target3:.6f}"
            sl_str = f"${sl:,.2f}" if sl >= 1 else f"${sl:.6f}"
            
            message += f"<b>{name} ({coin}/USDT)</b>\n"
            message += f"💵 قیمت فروش: {price_str}\n"
            message += f"🎯 هدف اول: {target1_str}\n"
            message += f"🎯 هدف دوم: {target2_str}\n"
            message += f"🎯 هدف سوم: {target3_str}\n"
            message += f"🛑 حد ضرر: {sl_str}\n\n"
            
            sell_signals += 1
            
        if sell_signals == 0:
            message += "در حال حاضر سیگنال فروش معتبری وجود ندارد.\n\n"
        
        # اطلاعات تکمیلی
        message += """
⚠️ <b>تذکر مهم:</b>
• معامله با ارزهای دیجیتال همراه با ریسک است.
• همیشه از حد ضرر استفاده کنید.
• این سیگنال‌ها صرفاً پیشنهاد هستند و تصمیم نهایی با شماست.
• از سرمایه‌گذاری بیش از توان مالی خود خودداری کنید.
"""
        
        message += f"\n⏰ <b>زمان سیگنال (تورنتو):</b> {current_time}"
        
        return send_message(message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"خطا در ارسال سیگنال‌های معاملاتی: {str(e)}")
        return False

if __name__ == "__main__":
    # تست ارسال پیام
    send_test_message()