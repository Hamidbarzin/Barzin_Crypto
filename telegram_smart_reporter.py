"""
اسکریپت ارسال گزارش‌های هوشمند به تلگرام با استفاده از هوش مصنوعی

این اسکریپت از ترکیب داده‌های قیمت، تحلیل تکنیکال، اخبار و هوش مصنوعی
برای ارائه گزارش‌های هوشمند به کاربر از طریق تلگرام استفاده می‌کند.
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# واردسازی ماژول‌های ربات
try:
    from crypto_bot.telegram_service import send_telegram_message
    logger.info("ماژول‌های تلگرام با موفقیت بارگذاری شدند")
except Exception as e:
    logger.error(f"خطا در بارگذاری ماژول تلگرام: {str(e)}")
    sys.exit(1)

try:
    from crypto_bot.market_api import get_current_price, get_market_prices, test_api_connection
    logger.info("ماژول API بازار با موفقیت بارگذاری شد")
except Exception as e:
    logger.error(f"خطا در بارگذاری ماژول API بازار: {str(e)}")
    sys.exit(1)

try:
    from crypto_bot.robot_advisor import (
        get_market_overview, get_coin_analysis, 
        get_buying_opportunities, get_selling_opportunities,
        get_market_news_analysis
    )
    logger.info("ماژول مشاور رباتیک با موفقیت بارگذاری شد")
except Exception as e:
    logger.error(f"خطا در بارگذاری ماژول مشاور رباتیک: {str(e)}")
    sys.exit(1)

def send_smart_market_overview():
    """
    ارسال نمای کلی بازار با استفاده از هوش مصنوعی
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت نمای کلی بازار
        overview_data = get_market_overview()
        
        if "error" in overview_data:
            error_message = f"❌ خطا در تحلیل بازار: {overview_data['error']}"
            return send_telegram_message(error_message)
        
        # ساخت پیام
        message = "🤖 *تحلیل هوشمند بازار ارزهای دیجیتال*\n\n"
        message += overview_data.get("overview", {}).get("analysis", "داده‌های تحلیل در دسترس نیست")
        message += f"\n\n📊 *قیمت‌های لحظه‌ای:*\n"
        
        market_data = overview_data.get("market_data", {})
        for symbol, data in market_data.items():
            if not isinstance(data, dict) or "error" in data:
                continue
            message += f"• {symbol}: {data['price']:,.2f} USDT"
            if data.get('change_percent', 0) != 0:
                change = data['change_percent']
                emoji = "🔴" if change < 0 else "🟢"
                message += f" {emoji} {change:.2f}%"
            message += "\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال نمای کلی بازار: {str(e)}")
        error_message = f"❌ خطا در ارسال نمای کلی بازار: {str(e)}"
        return send_telegram_message(error_message)

def send_smart_coin_analysis(symbol="BTC/USDT"):
    """
    ارسال تحلیل هوشمند یک ارز با استفاده از هوش مصنوعی
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت تحلیل ارز
        analysis_data = get_coin_analysis(symbol)
        
        if "error" in analysis_data:
            error_message = f"❌ خطا در تحلیل {symbol}: {analysis_data['error']}"
            return send_telegram_message(error_message)
        
        # ساخت پیام
        message = f"🤖 *تحلیل هوشمند {symbol}*\n\n"
        
        # اضافه کردن پیشنهاد هوش مصنوعی
        if "ai_suggestion" in analysis_data and "suggestion" in analysis_data["ai_suggestion"]:
            message += analysis_data["ai_suggestion"]["suggestion"]
        else:
            message += "داده‌های تحلیل هوشمند در دسترس نیست"
        
        message += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل ارز {symbol}: {str(e)}")
        error_message = f"❌ خطا در ارسال تحلیل ارز {symbol}: {str(e)}"
        return send_telegram_message(error_message)

def send_trading_opportunities():
    """
    ارسال فرصت‌های معاملاتی (خرید و فروش)
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت فرصت‌های خرید
        buy_opportunities = get_buying_opportunities(3)
        
        # دریافت فرصت‌های فروش
        sell_opportunities = get_selling_opportunities(3)
        
        # ساخت پیام
        message = "🤖 *فرصت‌های معاملاتی هوشمند*\n\n"
        
        # اضافه کردن فرصت‌های خرید
        message += "🟢 *فرصت‌های خرید:*\n"
        if buy_opportunities:
            for opp in buy_opportunities:
                emoji = "⭐" * int(opp.get("confidence", 0) * 5 / 0.95)
                message += f"• {opp['symbol']}: {opp['price']:,.2f} USDT {emoji}\n"
                message += f"  دلیل: {opp['reason']}\n"
        else:
            message += "در حال حاضر فرصت خرید مناسبی شناسایی نشد.\n"
        
        message += "\n🔴 *فرصت‌های فروش:*\n"
        if sell_opportunities:
            for opp in sell_opportunities:
                emoji = "⭐" * int(opp.get("confidence", 0) * 5 / 0.95)
                message += f"• {opp['symbol']}: {opp['price']:,.2f} USDT {emoji}\n"
                message += f"  دلیل: {opp['reason']}\n"
        else:
            message += "در حال حاضر فرصت فروش مناسبی شناسایی نشد.\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال فرصت‌های معاملاتی: {str(e)}")
        error_message = f"❌ خطا در ارسال فرصت‌های معاملاتی: {str(e)}"
        return send_telegram_message(error_message)

def send_news_impact_analysis():
    """
    ارسال تحلیل تأثیر اخبار بر بازار
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت تحلیل اخبار
        news_analysis = get_market_news_analysis()
        
        if "error" in news_analysis:
            error_message = f"❌ خطا در تحلیل اخبار: {news_analysis['error']}"
            return send_telegram_message(error_message)
        
        # ساخت پیام
        message = "🤖 *تحلیل هوشمند تأثیر اخبار بر بازار*\n\n"
        
        if "news_impact_analysis" in news_analysis:
            message += news_analysis["news_impact_analysis"]
        else:
            message += "داده‌های تحلیل اخبار در دسترس نیست"
        
        message += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام
        return send_telegram_message(message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل اخبار: {str(e)}")
        error_message = f"❌ خطا در ارسال تحلیل اخبار: {str(e)}"
        return send_telegram_message(error_message)

def send_complete_report():
    """
    ارسال گزارش کامل بازار شامل تمام تحلیل‌های هوشمند
    
    Returns:
        bool: وضعیت ارسال گزارش‌ها
    """
    results = []
    
    logger.info("در حال ارسال نمای کلی بازار...")
    results.append(send_smart_market_overview())
    
    logger.info("در حال ارسال تحلیل بیت‌کوین...")
    results.append(send_smart_coin_analysis("BTC/USDT"))
    
    logger.info("در حال ارسال فرصت‌های معاملاتی...")
    results.append(send_trading_opportunities())
    
    logger.info("در حال ارسال تحلیل اخبار...")
    results.append(send_news_impact_analysis())
    
    # بررسی نتایج
    if all(results):
        logger.info("تمام گزارش‌ها با موفقیت ارسال شدند")
        return True
    else:
        logger.error("برخی از گزارش‌ها ارسال نشدند")
        return False

def send_test_message():
    """
    ارسال پیام تست برای بررسی عملکرد سیستم
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        message = f"""
🤖 *پیام تست ربات تحلیل هوشمند ارزهای دیجیتال*

سلام! من ربات تحلیل هوشمند ارزهای دیجیتال هستم که با استفاده از هوش مصنوعی، داده‌های بازار را تحلیل می‌کنم و به شما پیشنهادهای معاملاتی ارائه می‌دهم.

قابلیت‌های من:
• تحلیل کلی بازار
• تحلیل هوشمند ارزهای مختلف
• شناسایی فرصت‌های خرید و فروش
• تحلیل تأثیر اخبار بر بازار

این پیام برای تست عملکرد سیستم ارسال شده است. برای دریافت گزارش‌های دوره‌ای، ربات را روی سرور خود اجرا کنید.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return send_telegram_message(message)
    
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    
    این تابع براساس پارامترهای ورودی تصمیم می‌گیرد چه گزارشی ارسال شود
    """
    logger.info("شروع اجرای برنامه گزارش‌دهی هوشمند تلگرام")
    
    # تعریف پارسر آرگومان‌ها
    parser = argparse.ArgumentParser(description="ربات گزارش‌دهی هوشمند تلگرام")
    parser.add_argument("--test", action="store_true", help="ارسال پیام تست")
    parser.add_argument("--overview", action="store_true", help="ارسال نمای کلی بازار")
    parser.add_argument("--coin", type=str, help="ارسال تحلیل یک ارز خاص")
    parser.add_argument("--opportunities", action="store_true", help="ارسال فرصت‌های معاملاتی")
    parser.add_argument("--news", action="store_true", help="ارسال تحلیل اخبار")
    parser.add_argument("--full", action="store_true", help="ارسال گزارش کامل")
    
    # پردازش آرگومان‌ها
    args = parser.parse_args()
    
    # تست اتصال به API
    logger.info(f"نتیجه تست اتصال به API: {test_api_connection()}")
    
    # اجرای عملیات براساس آرگومان‌ها
    if args.test:
        logger.info("در حال ارسال پیام تست...")
        send_test_message()
    elif args.overview:
        logger.info("در حال ارسال نمای کلی بازار...")
        send_smart_market_overview()
    elif args.coin:
        logger.info(f"در حال ارسال تحلیل ارز {args.coin}...")
        send_smart_coin_analysis(args.coin)
    elif args.opportunities:
        logger.info("در حال ارسال فرصت‌های معاملاتی...")
        send_trading_opportunities()
    elif args.news:
        logger.info("در حال ارسال تحلیل اخبار...")
        send_news_impact_analysis()
    elif args.full:
        logger.info("در حال ارسال گزارش کامل...")
        send_complete_report()
    else:
        # بدون آرگومان، گزارش کلی بازار ارسال می‌شود
        logger.info("در حال ارسال گزارش پیش‌فرض (نمای کلی بازار)...")
        send_smart_market_overview()
    
    logger.info("پایان اجرای برنامه گزارش‌دهی هوشمند تلگرام")

if __name__ == "__main__":
    main()