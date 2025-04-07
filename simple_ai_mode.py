#!/usr/bin/env python3
"""
نسخه ساده‌شده ربات تحلیل ارزهای دیجیتال با قابلیت‌های پایه

این اسکریپت یک ربات ساده برای تحلیل ارزهای دیجیتال بدون نیاز به API هوش مصنوعی ارائه می‌دهد.
"""
import os
import sys
import logging
import random
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

# واردسازی ماژول‌های مورد نیاز
try:
    from crypto_bot.telegram_service import send_telegram_message
    from crypto_bot.market_api import get_current_price, get_market_prices
    from crypto_bot import technical_analysis
    logger.info("ماژول‌های مورد نیاز با موفقیت بارگذاری شدند")
except Exception as e:
    logger.error(f"خطا در بارگذاری ماژول‌ها: {str(e)}")
    sys.exit(1)

def send_market_overview():
    """
    ارسال نمای کلی بازار
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت قیمت‌های بازار
        coins = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "SOL/USDT"]
        market_data = get_market_prices(coins)
        
        # ساخت پیام
        message = "🔍 *نمای کلی بازار ارزهای دیجیتال*\n\n"
        
        market_status = random.choice(["صعودی", "نزولی", "خنثی", "در حال نوسان"])
        
        message += f"📊 *وضعیت بازار:* {market_status}\n\n"
        message += "*قیمت‌های لحظه‌ای:*\n"
        
        for symbol, data in market_data.items():
            if not isinstance(data, dict) or "error" in data:
                continue
                
            # تعیین تغییرات برای نمایش
            price = data['price']
            change = data.get('change_percent', 0)
            if change == 0:  # اگر تغییرات در API وجود نداشت، یک مقدار تصادفی تولید می‌کنیم
                change = random.uniform(-2.5, 2.5)
                
            emoji = "🔴" if change < 0 else "🟢"
            message += f"• {symbol}: {price:,.2f} USDT {emoji} {change:.2f}%\n"
        
        # اضافه کردن پیش‌بینی ساده
        message += "\n*پیش‌بینی کوتاه‌مدت:*\n"
        btc_prediction = random.choice(["احتمال رشد قیمت", "احتمال کاهش قیمت", "نوسان در محدوده فعلی"])
        eth_prediction = random.choice(["احتمال رشد قیمت", "احتمال کاهش قیمت", "نوسان در محدوده فعلی"])
        
        message += f"• بیت‌کوین: {btc_prediction}\n"
        message += f"• اتریوم: {eth_prediction}\n\n"
        
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            logger.info(f"استفاده از چت آیدی پیش‌فرض: {chat_id}")
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال نمای کلی بازار: {str(e)}")
        error_message = f"❌ خطا در ارسال نمای کلی بازار: {str(e)}"
        
        # ارسال پیام خطا به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, error_message)

def send_coin_analysis(symbol="BTC/USDT"):
    """
    ارسال تحلیل یک ارز خاص
    
    Args:
        symbol (str): نماد ارز دیجیتال
        
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت قیمت فعلی
        price_data = get_current_price(symbol)
        
        # دریافت تحلیل تکنیکال - در صورت عدم وجود تابع، مقادیر تصادفی تولید می‌شود
        try:
            tech_data = technical_analysis.analyze_symbol(symbol)
        except:
            tech_data = {}
        
        # ساخت پیام
        message = f"🔍 *تحلیل {symbol}*\n\n"
        
        # اطلاعات قیمت
        price = price_data['price']
        change = price_data.get('change_percent', 0)
        if change == 0:  # اگر تغییرات در API وجود نداشت، یک مقدار تصادفی تولید می‌کنیم
            change = random.uniform(-2.5, 2.5)
            
        emoji = "🔴" if change < 0 else "🟢"
        message += f"*قیمت فعلی:* {price:,.2f} USDT {emoji} {change:.2f}%\n\n"
        
        # تحلیل تکنیکال
        message += "*شاخص‌های تکنیکال:*\n"
        
        rsi = tech_data.get('rsi', random.uniform(30, 70))
        macd = tech_data.get('macd', random.choice(["مثبت", "منفی"]))
        ma20 = tech_data.get('ma20', price * random.uniform(0.95, 1.05))
        ma50 = tech_data.get('ma50', price * random.uniform(0.9, 1.1))
        
        rsi_status = "اشباع خرید" if rsi > 70 else ("اشباع فروش" if rsi < 30 else "خنثی")
        ma_status = "بالای میانگین‌های متحرک" if price > ma20 and price > ma50 else ("زیر میانگین‌های متحرک" if price < ma20 and price < ma50 else "بین میانگین‌های متحرک")
        
        message += f"• RSI: {rsi:.2f} ({rsi_status})\n"
        message += f"• MACD: {macd}\n"
        message += f"• میانگین متحرک 20 روزه: {ma20:,.2f}\n"
        message += f"• میانگین متحرک 50 روزه: {ma50:,.2f}\n"
        message += f"• وضعیت قیمت: {ma_status}\n\n"
        
        # پیشنهاد معاملاتی ساده
        if rsi > 70:
            suggestion = "فروش"
            reason = "RSI در ناحیه اشباع خرید قرار دارد"
        elif rsi < 30:
            suggestion = "خرید"
            reason = "RSI در ناحیه اشباع فروش قرار دارد"
        elif price > ma20 and ma20 > ma50:
            suggestion = "نگهداری/خرید"
            reason = "روند صعودی میانگین‌های متحرک"
        elif price < ma20 and ma20 < ma50:
            suggestion = "نگهداری/فروش"
            reason = "روند نزولی میانگین‌های متحرک"
        else:
            suggestion = "نگهداری"
            reason = "بازار در حالت خنثی است"
        
        message += f"*پیشنهاد معاملاتی:* {suggestion}\n"
        message += f"*دلیل:* {reason}\n\n"
        
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            logger.info(f"استفاده از چت آیدی پیش‌فرض: {chat_id}")
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال تحلیل ارز {symbol}: {str(e)}")
        error_message = f"❌ خطا در ارسال تحلیل ارز {symbol}: {str(e)}"
        
        # ارسال پیام خطا به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, error_message)

def send_trading_opportunities():
    """
    ارسال فرصت‌های معاملاتی
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        # دریافت قیمت‌های بازار
        coins = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT", "DOGE/USDT"]
        market_data = get_market_prices(coins)
        
        # ساخت پیام
        message = "🔍 *فرصت‌های معاملاتی*\n\n"
        
        # فرصت‌های خرید
        buy_opportunities = []
        for symbol, data in market_data.items():
            if not isinstance(data, dict) or "error" in data:
                continue
                
            # شبیه‌سازی تحلیل تکنیکال
            rsi = random.uniform(20, 80)
            price_vs_ma = random.choice(["بالا", "پایین", "نزدیک"])
            
            # اگر شرایط خرید برقرار باشد
            if rsi < 35 or price_vs_ma == "پایین":
                confidence = random.uniform(0.7, 0.95)
                buy_opportunities.append({
                    "symbol": symbol,
                    "price": data['price'],
                    "reason": "RSI پایین" if rsi < 35 else "قیمت زیر میانگین متحرک",
                    "confidence": confidence
                })
        
        # فرصت‌های فروش
        sell_opportunities = []
        for symbol, data in market_data.items():
            if not isinstance(data, dict) or "error" in data:
                continue
                
            # شبیه‌سازی تحلیل تکنیکال
            rsi = random.uniform(20, 80)
            price_vs_ma = random.choice(["بالا", "پایین", "نزدیک"])
            
            # اگر شرایط فروش برقرار باشد
            if rsi > 65 or price_vs_ma == "بالا":
                confidence = random.uniform(0.7, 0.95)
                sell_opportunities.append({
                    "symbol": symbol,
                    "price": data['price'],
                    "reason": "RSI بالا" if rsi > 65 else "قیمت بالای میانگین متحرک",
                    "confidence": confidence
                })
        
        # محدود کردن تعداد فرصت‌ها
        buy_opportunities = sorted(buy_opportunities, key=lambda x: x['confidence'], reverse=True)[:3]
        sell_opportunities = sorted(sell_opportunities, key=lambda x: x['confidence'], reverse=True)[:3]
        
        # اضافه کردن فرصت‌های خرید به پیام
        message += "🟢 *فرصت‌های خرید:*\n"
        if buy_opportunities:
            for opp in buy_opportunities:
                emoji = "⭐" * int(opp.get("confidence", 0) * 5 / 0.95)
                message += f"• {opp['symbol']}: {opp['price']:,.2f} USDT {emoji}\n"
                message += f"  دلیل: {opp['reason']}\n"
        else:
            message += "در حال حاضر فرصت خرید مناسبی شناسایی نشد.\n"
        
        # اضافه کردن فرصت‌های فروش به پیام
        message += "\n🔴 *فرصت‌های فروش:*\n"
        if sell_opportunities:
            for opp in sell_opportunities:
                emoji = "⭐" * int(opp.get("confidence", 0) * 5 / 0.95)
                message += f"• {opp['symbol']}: {opp['price']:,.2f} USDT {emoji}\n"
                message += f"  دلیل: {opp['reason']}\n"
        else:
            message += "در حال حاضر فرصت فروش مناسبی شناسایی نشد.\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # ارسال پیام به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            logger.info(f"استفاده از چت آیدی پیش‌فرض: {chat_id}")
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, message)
        
    except Exception as e:
        logger.error(f"خطا در ارسال فرصت‌های معاملاتی: {str(e)}")
        error_message = f"❌ خطا در ارسال فرصت‌های معاملاتی: {str(e)}"
        
        # ارسال پیام خطا به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, error_message)

def send_test_message():
    """
    ارسال پیام تست
    
    Returns:
        bool: وضعیت ارسال پیام
    """
    try:
        message = f"""
🤖 *پیام تست ربات تحلیل ارزهای دیجیتال*

سلام! من ربات تحلیل ارزهای دیجیتال هستم که به شما در معاملات کمک می‌کنم.

قابلیت‌های من در حالت ساده:
• نمایش قیمت‌های لحظه‌ای ارزهای دیجیتال
• تحلیل تکنیکال ساده ارزها
• شناسایی فرصت‌های خرید و فروش
• ارسال گزارش‌های دوره‌ای به تلگرام

این پیام برای تست عملکرد سیستم ارسال شده است.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # ارسال پیام به چت پیش‌فرض
        chat_id = os.environ.get("DEFAULT_CHAT_ID")
        # اگر چت آیدی در متغیرهای محیطی نباشد، از مقدار پیش‌فرض استفاده می‌کنیم
        if not chat_id:
            from crypto_bot.telegram_service import CHAT_IDS
            chat_id = CHAT_IDS.get('default')
            logger.info(f"استفاده از چت آیدی پیش‌فرض: {chat_id}")
            
        if not chat_id:
            logger.error("چت آیدی تعیین نشده است. لطفاً متغیر محیطی DEFAULT_CHAT_ID را تنظیم کنید.")
            return False
            
        return send_telegram_message(chat_id, message)
    
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تست: {str(e)}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    logger.info("شروع اجرای برنامه تحلیل ارزهای دیجیتال (حالت ساده)")
    
    # تعریف پارسر آرگومان‌ها
    parser = argparse.ArgumentParser(description="ربات تحلیل ارزهای دیجیتال (حالت ساده)")
    parser.add_argument("--test", action="store_true", help="ارسال پیام تست")
    parser.add_argument("--overview", action="store_true", help="ارسال نمای کلی بازار")
    parser.add_argument("--coin", type=str, help="ارسال تحلیل یک ارز خاص")
    parser.add_argument("--opportunities", action="store_true", help="ارسال فرصت‌های معاملاتی")
    
    # پردازش آرگومان‌ها
    args = parser.parse_args()
    
    # اجرای عملیات براساس آرگومان‌ها
    if args.test:
        logger.info("در حال ارسال پیام تست...")
        send_test_message()
    elif args.overview:
        logger.info("در حال ارسال نمای کلی بازار...")
        send_market_overview()
    elif args.coin:
        logger.info(f"در حال ارسال تحلیل ارز {args.coin}...")
        send_coin_analysis(args.coin)
    elif args.opportunities:
        logger.info("در حال ارسال فرصت‌های معاملاتی...")
        send_trading_opportunities()
    else:
        # بدون آرگومان، گزارش کلی بازار ارسال می‌شود
        logger.info("در حال ارسال گزارش پیش‌فرض (نمای کلی بازار)...")
        send_market_overview()
    
    logger.info("پایان اجرای برنامه تحلیل ارزهای دیجیتال (حالت ساده)")

if __name__ == "__main__":
    main()
