#!/usr/bin/env python3
"""
سرویس هشدار قیمت ارزهای دیجیتال

این ماژول وظیفه نظارت بر قیمت‌های ارزهای دیجیتال و ارسال 
هشدار در صورت رسیدن به محدوده‌های خاص را بر عهده دارد.
"""

import logging
import datetime
import pytz
from typing import Dict, List, Optional, Tuple, Any

from crypto_bot import market_data
import replit_telegram_sender

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("price_alert")

# منطقه زمانی تورنتو
toronto_tz = pytz.timezone('America/Toronto')

# لیست محدوده‌های قیمتی برای هشدار
# ساختار: {symbol: [(price, type, triggered)]}
# type می‌تواند "above" یا "below" باشد
price_alerts: Dict[str, List[Tuple[float, str, bool]]] = {}


def set_price_alert(symbol: str, price: float, alert_type: str = "above") -> bool:
    """
    تنظیم هشدار قیمت برای یک ارز خاص
    
    Args:
        symbol (str): نماد ارز (مثلاً BTC/USDT)
        price (float): قیمت هدف
        alert_type (str): نوع هشدار ("above" برای بالاتر از قیمت، "below" برای پایین‌تر از قیمت)
        
    Returns:
        bool: وضعیت تنظیم هشدار
    """
    if symbol not in price_alerts:
        price_alerts[symbol] = []
    
    # اگر هشدار مشابهی قبلاً تنظیم شده، آن را به‌روزرسانی می‌کنیم
    for i, (old_price, old_type, _) in enumerate(price_alerts[symbol]):
        if abs(old_price - price) < 0.001 and old_type == alert_type:
            price_alerts[symbol][i] = (price, alert_type, False)
            logger.info(f"هشدار قیمت برای {symbol} بروزرسانی شد: {alert_type} {price}")
            return True
    
    # هشدار جدید اضافه می‌کنیم
    price_alerts[symbol].append((price, alert_type, False))
    logger.info(f"هشدار قیمت برای {symbol} تنظیم شد: {alert_type} {price}")
    return True


def remove_price_alert(symbol: str, price: float, alert_type: str = "above") -> bool:
    """
    حذف هشدار قیمت برای یک ارز خاص
    
    Args:
        symbol (str): نماد ارز (مثلاً BTC/USDT)
        price (float): قیمت هدف
        alert_type (str): نوع هشدار ("above" برای بالاتر از قیمت، "below" برای پایین‌تر از قیمت)
        
    Returns:
        bool: وضعیت حذف هشدار
    """
    if symbol not in price_alerts:
        logger.warning(f"هیچ هشداری برای {symbol} وجود ندارد")
        return False
    
    for i, (old_price, old_type, _) in enumerate(price_alerts[symbol]):
        if abs(old_price - price) < 0.001 and old_type == alert_type:
            price_alerts[symbol].pop(i)
            logger.info(f"هشدار قیمت برای {symbol} حذف شد: {alert_type} {price}")
            return True
    
    logger.warning(f"هشدار قیمت مورد نظر برای {symbol} یافت نشد: {alert_type} {price}")
    return False


def get_price_alerts(symbol: Optional[str] = None) -> Dict[str, List[Tuple[float, str, bool]]]:
    """
    دریافت لیست هشدارهای قیمت
    
    Args:
        symbol (Optional[str]): نماد ارز برای فیلتر (اگر None باشد همه هشدارها برگردانده می‌شوند)
        
    Returns:
        Dict[str, List[Tuple[float, str, bool]]]: دیکشنری هشدارهای قیمت
    """
    if symbol:
        return {symbol: price_alerts.get(symbol, [])}
    return price_alerts


def _format_price_for_message(price: float) -> str:
    """
    فرمت کردن قیمت برای نمایش در پیام
    
    Args:
        price (float): قیمت
        
    Returns:
        str: قیمت فرمت شده
    """
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.6f}"


def check_price_alerts() -> List[Dict[str, Any]]:
    """
    بررسی وضعیت قیمت‌ها و ارسال هشدار در صورت رسیدن به محدوده‌های خاص
    
    Returns:
        List[Dict[str, Any]]: لیست هشدارهای فعال شده
    """
    triggered_alerts = []
    
    for symbol, alerts in price_alerts.items():
        # دریافت قیمت فعلی
        try:
            prices_data = market_data.get_current_prices([symbol])
            if symbol not in prices_data or "price" not in prices_data[symbol]:
                logger.warning(f"امکان دریافت قیمت برای {symbol} وجود ندارد")
                continue
            current_price = prices_data[symbol]["price"]
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت {symbol}: {str(e)}")
            continue
        
        # بررسی هشدارها
        for i, (target_price, alert_type, triggered) in enumerate(alerts):
            # اگر هشدار قبلاً فعال شده باید دوباره بررسی کنیم که آیا باید مجدد فعال شود یا خیر
            if triggered:
                # هشدار "above": اگر قیمت به پایین برگشته و حداقل ۱٪ پایین‌تر از قیمت هدف باشد، بازنشانی شود
                if alert_type == "above" and current_price < target_price * 0.99:
                    alerts[i] = (target_price, alert_type, False)
                    logger.info(f"هشدار {symbol} از نوع {alert_type} در قیمت {target_price} بازنشانی شد")
                
                # هشدار "below": اگر قیمت به بالا برگشته و حداقل ۱٪ بالاتر از قیمت هدف باشد، بازنشانی شود
                elif alert_type == "below" and current_price > target_price * 1.01:
                    alerts[i] = (target_price, alert_type, False)
                    logger.info(f"هشدار {symbol} از نوع {alert_type} در قیمت {target_price} بازنشانی شد")
                
                continue
            
            # بررسی شرایط فعال‌سازی هشدار
            alert_triggered = False
            
            if alert_type == "above" and current_price >= target_price:
                alert_triggered = True
            elif alert_type == "below" and current_price <= target_price:
                alert_triggered = True
            
            if alert_triggered:
                # هشدار فعال شد
                alerts[i] = (target_price, alert_type, True)
                
                # پیام هشدار را تولید می‌کنیم
                alert_info = {
                    "symbol": symbol,
                    "current_price": current_price,
                    "target_price": target_price,
                    "alert_type": alert_type,
                    "time": datetime.datetime.now(toronto_tz)
                }
                
                triggered_alerts.append(alert_info)
                
                # ارسال هشدار تلگرام
                alert_message = generate_alert_message(alert_info)
                try:
                    replit_telegram_sender.send_message(alert_message)
                    logger.info(f"هشدار قیمت برای {symbol} ارسال شد: {alert_type} {target_price}")
                except Exception as e:
                    logger.error(f"خطا در ارسال هشدار قیمت به تلگرام: {str(e)}")
    
    return triggered_alerts


def generate_alert_message(alert_info: Dict[str, Any]) -> str:
    """
    تولید پیام هشدار قیمت
    
    Args:
        alert_info (Dict[str, Any]): اطلاعات هشدار
        
    Returns:
        str: پیام هشدار
    """
    symbol = alert_info["symbol"]
    current_price = alert_info["current_price"]
    target_price = alert_info["target_price"]
    alert_type = alert_info["alert_type"]
    alert_time = alert_info["time"].strftime("%H:%M:%S")
    
    # فرمت‌بندی قیمت‌ها
    formatted_current = _format_price_for_message(current_price)
    formatted_target = _format_price_for_message(target_price)
    
    # مشخص کردن نوع هشدار
    if alert_type == "above":
        direction = "بالاتر از"
        emoji = "🔺"
    else:
        direction = "پایین‌تر از"
        emoji = "🔻"
    
    # محاسبه درصد تغییر
    percent_change = abs((current_price - target_price) / target_price * 100)
    
    message = f"""🚨 <b>هشدار قیمت {emoji}</b> 🚨

<b>ارز:</b> {symbol}
<b>وضعیت:</b> قیمت {direction} محدوده هدف

<b>قیمت فعلی:</b> {formatted_current} USDT
<b>قیمت هدف:</b> {formatted_target} USDT
<b>تغییر:</b> {percent_change:.2f}%

<b>زمان:</b> {alert_time} به وقت تورنتو

<i>🤖 Crypto Barzin</i>
"""
    
    return message


# اضافه کردن چند هشدار پیش‌فرض
set_price_alert("BTC/USDT", 90000, "above")
set_price_alert("BTC/USDT", 75000, "below")
set_price_alert("ETH/USDT", 2000, "above")
set_price_alert("ETH/USDT", 1500, "below")

# تابع اصلی برای تست
if __name__ == "__main__":
    print("در حال تست سرویس هشدار قیمت...")
    
    # تست تنظیم هشدار
    set_price_alert("BTC/USDT", 80000, "above")
    set_price_alert("ETH/USDT", 1500, "below")
    
    # نمایش هشدارهای تنظیم شده
    print("هشدارهای تنظیم شده:")
    print(get_price_alerts())
    
    # تست بررسی هشدارها
    print("در حال بررسی هشدارها...")
    triggered = check_price_alerts()
    
    if triggered:
        print(f"{len(triggered)} هشدار فعال شد")
    else:
        print("هیچ هشداری فعال نشد")