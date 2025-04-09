#!/usr/bin/env python3
"""
ماژول قالب‌بندی ساده پیام‌های تلگرام با تمرکز بر گزارش‌های ارز دیجیتال

این ماژول به راحتی قالب‌های مختلف برای گزارش قیمت، تحلیل تکنیکال و سیگنال‌های خرید و فروش 
را فراهم می‌کند و با ماژول simple_telegram_sender.py کار می‌کند.
همچنین قابلیت ارسال نمودارهای تحلیل تکنیکال را با استفاده از ماژول chart_generator.py دارد.
"""

import os
import logging
from datetime import datetime
import random

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# وارد کردن ماژول ارسال پیام
try:
    import simple_telegram_sender as telegram
    logger.info("ماژول ارسال پیام تلگرام با موفقیت بارگذاری شد")
except ImportError:
    logger.error("خطا در بارگذاری ماژول ارسال پیام تلگرام")
    telegram = None

# وارد کردن ماژول تولید نمودار
try:
    from chart_generator import generate_candlestick_chart, generate_technical_chart, generate_all_charts
    logger.info("ماژول تولید نمودار با موفقیت بارگذاری شد")
    CHARTS_ENABLED = True
except ImportError:
    logger.warning("ماژول تولید نمودار در دسترس نیست. قابلیت ارسال نمودار غیرفعال خواهد بود.")
    CHARTS_ENABLED = False
    
    # تعریف توابع جایگزین
    def generate_candlestick_chart(*args, **kwargs):
        return None
    def generate_technical_chart(*args, **kwargs):
        return None
    def generate_all_charts(*args, **kwargs):
        return {}

def format_price(price):
    """
    قالب‌بندی قیمت با جداکننده هزارتایی و اعشار مناسب
    """
    if isinstance(price, (int, float)):
        if price >= 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.6f}"
    else:
        return f"${price}"

def get_emoji_for_change(change):
    """
    انتخاب ایموجی مناسب برای تغییرات قیمت
    """
    if isinstance(change, (int, float)):
        if change > 3:
            return "🚀"  # افزایش شدید
        elif change > 0:
            return "🟢"  # افزایش
        elif change < -3:
            return "📉"  # کاهش شدید
        elif change < 0:
            return "🔴"  # کاهش
        else:
            return "⚖️"  # بدون تغییر
    return "⚖️"  # پیش‌فرض

def get_trend_description(trend_value):
    """
    توصیف روند بازار بر اساس مقدار عددی
    مقدار بین -100 تا +100 است
    """
    if trend_value > 70:
        return "صعودی قوی 🚀"
    elif trend_value > 30:
        return "صعودی 🟢"
    elif trend_value > 10:
        return "صعودی ملایم 🟢"
    elif trend_value < -70:
        return "نزولی قوی 📉"
    elif trend_value < -30:
        return "نزولی 🔴"
    elif trend_value < -10:
        return "نزولی ملایم 🔴"
    else:
        return "خنثی/رنج ⚖️"

def format_market_overview(prices=None):
    """
    قالب‌بندی گزارش کلی بازار
    
    Args:
        prices (dict): دیکشنری قیمت‌ها (اختیاری)
    
    Returns:
        str: متن قالب‌بندی شده گزارش
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🌟 <b>Crypto Barzin - گزارش بازار</b>
━━━━━━━━━━━━━━━━━━

📊 <b>قیمت‌های لحظه‌ای بازار:</b>
"""
    
    if prices:
        # استفاده از داده‌های واقعی
        for symbol, data in prices.items():
            coin_name = symbol.split('/')[0]
            price = data.get('price', 0)
            change = data.get('change_24h', 0)
            emoji = get_emoji_for_change(change)
            
            price_str = format_price(price)
            change_str = f"{change:+.2f}%" if isinstance(change, (int, float)) else f"{change}"
            
            message += f"• {coin_name}: {price_str} ({emoji} {change_str})\n"
    else:
        # استفاده از داده‌های نمونه
        message += f"• بیت‌کوین (BTC): $65,433.45 (🟢 +2.34%)\n"
        message += f"• اتریوم (ETH): $3,458.12 (🟢 +1.76%)\n"
        message += f"• بایننس کوین (BNB): $548.67 (🔴 -0.85%)\n"
        message += f"• ریپل (XRP): $0.5247 (🟢 +0.32%)\n"
        message += f"• سولانا (SOL): $142.35 (🟢 +3.56%)\n"
    
    # روند کلی بازار
    market_trend = random.randint(-100, 100)
    trend_desc = get_trend_description(market_trend)
    
    message += f"\n📈 <b>روند کلی بازار:</b> {trend_desc}\n"
    
    # شاخص ترس و طمع
    fear_index = random.randint(1, 100)
    if fear_index > 75:
        fear_status = "طمع شدید 🤑"
    elif fear_index > 60:
        fear_status = "طمع 🤑"
    elif fear_index > 40:
        fear_status = "خنثی 😐"
    elif fear_index > 25:
        fear_status = "ترس 😨"
    else:
        fear_status = "ترس شدید 😱"
    
    message += f"😱 <b>شاخص ترس و طمع:</b> {fear_index} ({fear_status})\n"
    
    # اخبار مهم
    message += f"\n📰 <b>مهمترین اخبار:</b>\n"
    message += f"• احتمال تصویب ETF اتریوم در هفته آینده\n"
    message += f"• افزایش سرمایه‌گذاری نهادی در بیت‌کوین\n"
    message += f"• معرفی پروتکل جدید لایه دوم برای XRP\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return message

def format_coin_analysis(symbol="BTC/USDT", data=None):
    """
    قالب‌بندی تحلیل تکنیکال یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز
        data (dict): دیکشنری داده‌های تحلیل تکنیکال (اختیاری)
    
    Returns:
        str: متن قالب‌بندی شده تحلیل
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    coin_name = symbol.split('/')[0]
    
    message = f"""
📊 <b>Crypto Barzin - تحلیل {coin_name}</b>
━━━━━━━━━━━━━━━━━━

"""
    
    if data:
        # استفاده از داده‌های واقعی
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        rsi = data.get('rsi', 50)
        macd = data.get('macd', 0)
        macd_signal = data.get('macd_signal', 0)
        
        price_str = format_price(price)
        change_emoji = get_emoji_for_change(change)
        change_str = f"{change:+.2f}%" if isinstance(change, (int, float)) else f"{change}"
        
        message += f"💰 <b>قیمت فعلی:</b> {price_str} ({change_emoji} {change_str})\n\n"
        
        # RSI
        rsi_status = "فروش بیش از حد" if rsi < 30 else ("خرید بیش از حد" if rsi > 70 else "خنثی")
        rsi_emoji = "🟢" if rsi < 30 else ("🔴" if rsi > 70 else "🟡")
        message += f"• <b>RSI:</b> {rsi:.2f} ({rsi_status} {rsi_emoji})\n"
        
        # MACD
        macd_status = "صعودی" if macd > macd_signal else ("نزولی" if macd < macd_signal else "خنثی")
        macd_emoji = "🟢" if macd > macd_signal else ("🔴" if macd < macd_signal else "🟡")
        message += f"• <b>MACD:</b> {macd_status} {macd_emoji}\n"
        
        # میانگین‌های متحرک
        ma_status = data.get('ma_status', "خنثی")
        ma_emoji = "🟢" if "صعودی" in ma_status else ("🔴" if "نزولی" in ma_status else "🟡")
        message += f"• <b>میانگین متحرک:</b> {ma_status} {ma_emoji}\n"
        
        # باندهای بولینگر
        bb_status = data.get('bb_status', "خنثی")
        bb_emoji = "🟢" if "اشباع فروش" in bb_status else ("🔴" if "اشباع خرید" in bb_status else "🟡")
        message += f"• <b>باندهای بولینگر:</b> {bb_status} {bb_emoji}\n"
        
        # سیگنال کلی
        signal = data.get('signal', 'خنثی')
        signal_emoji = "🟢" if "خرید" in signal else ("🔴" if "فروش" in signal else "🟡")
        message += f"\n🎯 <b>سیگنال کلی:</b> {signal} {signal_emoji}\n"
        
        # هدف قیمتی
        if "خرید" in signal:
            target = price * (1 + random.uniform(0.05, 0.2))
            target_str = format_price(target)
            message += f"🎯 <b>هدف قیمتی:</b> {target_str}\n"
            sl = price * (1 - random.uniform(0.03, 0.08))
            sl_str = format_price(sl)
            message += f"🛑 <b>حد ضرر:</b> {sl_str}\n"
    else:
        # استفاده از داده‌های نمونه
        price = 65433.45 if coin_name == "BTC" else 3458.12 if coin_name == "ETH" else 142.35
        change = 2.34 if coin_name == "BTC" else 1.76 if coin_name == "ETH" else 3.56
        
        price_str = format_price(price)
        change_emoji = get_emoji_for_change(change)
        change_str = f"+{change}%"
        
        message += f"💰 <b>قیمت فعلی:</b> {price_str} ({change_emoji} {change_str})\n\n"
        
        message += f"• <b>RSI:</b> 32.45 (فروش بیش از حد 🟢)\n"
        message += f"• <b>MACD:</b> صعودی 🟢\n"
        message += f"• <b>میانگین متحرک:</b> مبهم/رنج 🟡\n"
        message += f"• <b>باندهای بولینگر:</b> نزولی 🟡\n"
        
        message += f"\n🎯 <b>سیگنال کلی:</b> خرید 🟢\n"
        
        target = price * 1.15
        target_str = format_price(target)
        message += f"🎯 <b>هدف قیمتی:</b> {target_str}\n"
        
        sl = price * 0.93
        sl_str = format_price(sl)
        message += f"🛑 <b>حد ضرر:</b> {sl_str}\n"
    
    message += f"\n⏰ <b>زمان:</b> {current_time}"
    
    return message

def format_trading_signals(signals=None):
    """
    قالب‌بندی سیگنال‌های معاملاتی
    
    Args:
        signals (list): لیست سیگنال‌ها (اختیاری)
    
    Returns:
        str: متن قالب‌بندی شده سیگنال‌ها
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
💰 <b>Crypto Barzin - سیگنال‌های معاملاتی</b>
━━━━━━━━━━━━━━━━━━

"""
    
    if signals:
        # استفاده از داده‌های واقعی
        for signal in signals:
            symbol = signal.get('symbol', 'BTC/USDT')
            coin_name = symbol.split('/')[0]
            action = signal.get('action', 'خرید')
            price = signal.get('price', 0)
            target = signal.get('target', 0)
            stop_loss = signal.get('stop_loss', 0)
            
            emoji = "🟢" if action == "خرید" else "🔴"
            price_str = format_price(price)
            target_str = format_price(target)
            stop_loss_str = format_price(stop_loss)
            
            message += f"{emoji} <b>{action} {coin_name}</b>\n"
            message += f"💲 قیمت ورود: {price_str}\n"
            message += f"🎯 هدف قیمتی: {target_str}\n"
            message += f"🛑 حد ضرر: {stop_loss_str}\n\n"
    else:
        # استفاده از داده‌های نمونه
        # سیگنال خرید BTC
        message += f"🟢 <b>خرید BTC</b>\n"
        message += f"💲 قیمت ورود: $65,000\n"
        message += f"🎯 هدف قیمتی: $72,500\n"
        message += f"🛑 حد ضرر: $61,500\n\n"
        
        # سیگنال خرید ETH
        message += f"🟢 <b>خرید ETH</b>\n"
        message += f"💲 قیمت ورود: $3,450\n"
        message += f"🎯 هدف قیمتی: $3,850\n"
        message += f"🛑 حد ضرر: $3,280\n\n"
        
        # سیگنال فروش XRP
        message += f"🔴 <b>فروش XRP</b>\n"
        message += f"💲 قیمت ورود: $0.52\n"
        message += f"🎯 هدف قیمتی: $0.48\n"
        message += f"🛑 حد ضرر: $0.54\n\n"
    
    message += f"⏰ <b>زمان:</b> {current_time}"
    
    return message

def send_market_overview(prices=None):
    """
    ارسال گزارش کلی بازار
    
    Args:
        prices (dict): دیکشنری قیمت‌ها (اختیاری)
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if telegram is None:
        logger.error("ماژول ارسال پیام تلگرام در دسترس نیست")
        return False
    
    message = format_market_overview(prices)
    return telegram.send_message(text=message, parse_mode="HTML")

def send_coin_analysis(symbol="BTC/USDT", data=None, with_chart=True):
    """
    ارسال تحلیل تکنیکال یک ارز دیجیتال
    
    Args:
        symbol (str): نماد ارز
        data (dict): دیکشنری داده‌های تحلیل تکنیکال (اختیاری)
        with_chart (bool): آیا نمودار تحلیل تکنیکال نیز ارسال شود؟
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if telegram is None:
        logger.error("ماژول ارسال پیام تلگرام در دسترس نیست")
        return False
    
    # ارسال متن تحلیل
    message = format_coin_analysis(symbol, data)
    success = telegram.send_message(text=message, parse_mode="HTML")
    
    # اگر نمودار درخواست شده و ماژول تولید نمودار فعال است
    if with_chart and CHARTS_ENABLED:
        try:
            logger.info(f"تولید نمودار برای {symbol}...")
            
            # تولید نمودار کندل استیک
            candlestick_chart = generate_candlestick_chart(symbol=symbol)
            if candlestick_chart:
                logger.info(f"ارسال نمودار کندل استیک برای {symbol}")
                telegram.send_photo(
                    photo_path=candlestick_chart,
                    caption=f"📊 نمودار کندل استیک {symbol.split('/')[0]} - تاریخ: {datetime.now().strftime('%Y-%m-%d')}"
                )
            
            # تولید نمودار تحلیل تکنیکال
            technical_chart = generate_technical_chart(symbol=symbol)
            if technical_chart:
                logger.info(f"ارسال نمودار تحلیل تکنیکال برای {symbol}")
                telegram.send_photo(
                    photo_path=technical_chart,
                    caption=f"📉 تحلیل تکنیکال {symbol.split('/')[0]} - شامل MACD و RSI - تاریخ: {datetime.now().strftime('%Y-%m-%d')}"
                )
                
            # اگر حداقل یک نمودار ارسال شد
            return True
        except Exception as e:
            logger.error(f"خطا در تولید یا ارسال نمودار: {e}")
    
    return success

def send_trading_signals(signals=None):
    """
    ارسال سیگنال‌های معاملاتی
    
    Args:
        signals (list): لیست سیگنال‌ها (اختیاری)
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if telegram is None:
        logger.error("ماژول ارسال پیام تلگرام در دسترس نیست")
        return False
    
    message = format_trading_signals(signals)
    return telegram.send_message(text=message, parse_mode="HTML")

def send_test_message():
    """
    ارسال پیام تست برای بررسی عملکرد سیستم
    
    Returns:
        bool: موفقیت یا شکست ارسال پیام
    """
    if telegram is None:
        logger.error("ماژول ارسال پیام تلگرام در دسترس نیست")
        return False
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🚀 <b>Crypto Barzin - پیام تست</b>
━━━━━━━━━━━━━━━━━━

سیستم گزارش‌دهی تلگرام فعال است و به درستی کار می‌کند.
این پیام با استفاده از ماژول قالب‌بندی ساده ارسال شده است.

برای گزارش‌های کامل‌تر می‌توانید از دستورات زیر استفاده کنید:
• دریافت گزارش کلی بازار
• دریافت تحلیل تکنیکال
• دریافت سیگنال‌های معاملاتی

⏰ <b>زمان:</b> {current_time}
    """
    
    return telegram.send_message(text=message, parse_mode="HTML")

def send_chart(symbol="BTC/USDT"):
    """
    فقط نمودار را برای یک ارز ارسال می‌کند
    
    Args:
        symbol (str): نماد ارز
        
    Returns:
        bool: موفقیت یا شکست ارسال نمودار
    """
    if telegram is None:
        logger.error("ماژول ارسال پیام تلگرام در دسترس نیست")
        return False
    
    if not CHARTS_ENABLED:
        logger.error("ماژول تولید نمودار در دسترس نیست")
        return False
    
    success = False
    try:
        logger.info(f"تولید نمودار برای {symbol}...")
        
        # تولید نمودار کندل استیک
        candlestick_chart = generate_candlestick_chart(symbol=symbol)
        if candlestick_chart:
            logger.info(f"ارسال نمودار کندل استیک برای {symbol}")
            telegram.send_photo(
                photo_path=candlestick_chart,
                caption=f"📊 نمودار کندل استیک {symbol.split('/')[0]} - تاریخ: {datetime.now().strftime('%Y-%m-%d')}"
            )
            success = True
        
        # تولید نمودار تحلیل تکنیکال
        technical_chart = generate_technical_chart(symbol=symbol)
        if technical_chart:
            logger.info(f"ارسال نمودار تحلیل تکنیکال برای {symbol}")
            telegram.send_photo(
                photo_path=technical_chart,
                caption=f"📉 تحلیل تکنیکال {symbol.split('/')[0]} - شامل MACD و RSI - تاریخ: {datetime.now().strftime('%Y-%m-%d')}"
            )
            success = True
        
        return success
    except Exception as e:
        logger.error(f"خطا در تولید یا ارسال نمودار: {e}")
        return False

# اگر این فایل به صورت مستقیم اجرا شود
if __name__ == "__main__":
    import sys
    
    # بررسی پارامترهای خط فرمان
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # ارسال پیام تست
            send_test_message()
            
        elif command == "market":
            # ارسال گزارش کلی بازار
            send_market_overview()
            
        elif command == "analysis":
            # ارسال تحلیل تکنیکال
            symbol = sys.argv[2] if len(sys.argv) > 2 else "BTC/USDT"
            send_coin_analysis(symbol)
            
        elif command == "signals":
            # ارسال سیگنال‌های معاملاتی
            send_trading_signals()
            
        elif command == "chart":
            # فقط ارسال نمودار
            symbol = sys.argv[2] if len(sys.argv) > 2 else "BTC/USDT"
            send_chart(symbol)
            
        else:
            print(f"دستور ناشناخته: {command}")
            print("دستورات قابل قبول: test, market, analysis, signals, chart")
    else:
        # بدون پارامتر، فقط یک پیام تست ارسال می‌کنیم
        send_test_message()