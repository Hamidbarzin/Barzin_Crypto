#!/usr/bin/env python3
"""
Cryptocurrency Price Alert Service

This module is responsible for monitoring cryptocurrency prices 
and sending alerts when prices reach specific thresholds.
"""

import logging
import datetime
import pytz
from typing import Dict, List, Optional, Tuple, Any

from crypto_bot import market_data
import replit_telegram_sender

# Setup logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("price_alert")

# Toronto timezone
toronto_tz = pytz.timezone('America/Toronto')

# List of price ranges for alerts
# Structure: {symbol: [(price, type, triggered)]}
# type can be "above" or "below"
price_alerts: Dict[str, List[Tuple[float, str, bool]]] = {}


def set_price_alert(symbol: str, price: float, alert_type: str = "above") -> bool:
    """
    Set price alert for a specific cryptocurrency
    
    Args:
        symbol (str): Currency symbol (e.g. BTC/USDT)
        price (float): Target price
        alert_type (str): Alert type ("above" for price above target, "below" for price below target)
        
    Returns:
        bool: Alert setting status
    """
    if symbol not in price_alerts:
        price_alerts[symbol] = []
    
    # If a similar alert already exists, update it
    for i, (old_price, old_type, _) in enumerate(price_alerts[symbol]):
        if abs(old_price - price) < 0.001 and old_type == alert_type:
            price_alerts[symbol][i] = (price, alert_type, False)
            logger.info(f"Price alert for {symbol} updated: {alert_type} {price}")
            return True
    
    # Add a new alert
    price_alerts[symbol].append((price, alert_type, False))
    logger.info(f"Price alert for {symbol} set: {alert_type} {price}")
    return True


def remove_price_alert(symbol: str, price: float, alert_type: str = "above") -> bool:
    """
    Remove price alert for a specific cryptocurrency
    
    Args:
        symbol (str): Currency symbol (e.g. BTC/USDT)
        price (float): Target price
        alert_type (str): Alert type ("above" for price above target, "below" for price below target)
        
    Returns:
        bool: Alert removal status
    """
    if symbol not in price_alerts:
        logger.warning(f"No alerts exist for {symbol}")
        return False
    
    for i, (old_price, old_type, _) in enumerate(price_alerts[symbol]):
        if abs(old_price - price) < 0.001 and old_type == alert_type:
            price_alerts[symbol].pop(i)
            logger.info(f"Price alert for {symbol} removed: {alert_type} {price}")
            return True
    
    logger.warning(f"Price alert for {symbol} not found: {alert_type} {price}")
    return False


def get_price_alerts(symbol: Optional[str] = None) -> Dict[str, List[Tuple[float, str, bool]]]:
    """
    Get the list of price alerts
    
    Args:
        symbol (Optional[str]): Currency symbol filter (if None, all alerts are returned)
        
    Returns:
        Dict[str, List[Tuple[float, str, bool]]]: Dictionary of price alerts
    """
    if symbol:
        return {symbol: price_alerts.get(symbol, [])}
    return price_alerts


def _format_price_for_message(price: float) -> str:
    """
    Format price for display in message
    
    Args:
        price (float): Price value
        
    Returns:
        str: Formatted price string
    """
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.6f}"


def check_price_alerts() -> List[Dict[str, Any]]:
    """
    Check prices and send alerts when reaching specific thresholds
    
    Returns:
        List[Dict[str, Any]]: List of triggered alerts
    """
    triggered_alerts = []
    
    for symbol, alerts in price_alerts.items():
        # Get current price
        try:
            prices_data = market_data.get_current_prices([symbol])
            if symbol not in prices_data or "price" not in prices_data[symbol]:
                logger.warning(f"Unable to get price for {symbol}")
                continue
            current_price = prices_data[symbol]["price"]
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            continue
        
        # Check alerts
        for i, (target_price, alert_type, triggered) in enumerate(alerts):
            # If the alert was previously triggered, check if it should be reset
            if triggered:
                # "above" alert: if price drops at least 1% below target price, reset it
                if alert_type == "above" and current_price < target_price * 0.99:
                    alerts[i] = (target_price, alert_type, False)
                    logger.info(f"Alert for {symbol} of type {alert_type} at price {target_price} reset")
                
                # "below" alert: if price rises at least 1% above target price, reset it
                elif alert_type == "below" and current_price > target_price * 1.01:
                    alerts[i] = (target_price, alert_type, False)
                    logger.info(f"Alert for {symbol} of type {alert_type} at price {target_price} reset")
                
                continue
            
            # Check alert trigger conditions
            alert_triggered = False
            
            if alert_type == "above" and current_price >= target_price:
                alert_triggered = True
            elif alert_type == "below" and current_price <= target_price:
                alert_triggered = True
            
            if alert_triggered:
                # Alert is triggered
                alerts[i] = (target_price, alert_type, True)
                
                # Generate alert information
                alert_info = {
                    "symbol": symbol,
                    "current_price": current_price,
                    "target_price": target_price,
                    "alert_type": alert_type,
                    "time": datetime.datetime.now(toronto_tz)
                }
                
                triggered_alerts.append(alert_info)
                
                # Send Telegram alert
                alert_message = generate_alert_message(alert_info)
                try:
                    replit_telegram_sender.send_message(alert_message, parse_mode="HTML")
                    logger.info(f"Price alert for {symbol} sent: {alert_type} {target_price}")
                except Exception as e:
                    logger.error(f"Error sending price alert to Telegram: {str(e)}")
    
    return triggered_alerts


def generate_alert_message(alert_info: Dict[str, Any]) -> str:
    """
    Generate price alert message
    
    Args:
        alert_info (Dict[str, Any]): Alert information
        
    Returns:
        str: Formatted alert message
    """
    symbol = alert_info["symbol"]
    current_price = alert_info["current_price"]
    target_price = alert_info["target_price"]
    alert_type = alert_info["alert_type"]
    alert_time = alert_info["time"].strftime("%H:%M:%S")
    
    # Format prices
    formatted_current = _format_price_for_message(current_price)
    formatted_target = _format_price_for_message(target_price)
    
    # Determine alert type
    if alert_type == "above":
        direction = "بالاتر از"  # Persian: "above"
        emoji = "🔺"
    else:
        direction = "پایین‌تر از"  # Persian: "below" 
        emoji = "🔻"
    
    # Calculate percent change
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


# Add default price alerts
set_price_alert("BTC/USDT", 82000, "above")  # Alert when Bitcoin price rises above 82000
set_price_alert("BTC/USDT", 81500, "below")  # Alert when Bitcoin price falls below 81500
set_price_alert("ETH/USDT", 1650, "above")   # Alert when Ethereum price rises above 1650
set_price_alert("ETH/USDT", 1580, "below")   # Alert when Ethereum price falls below 1580

# Main function for testing
if __name__ == "__main__":
    print("Testing price alert service...")
    
    # Test setting alerts
    set_price_alert("BTC/USDT", 80000, "above")
    set_price_alert("ETH/USDT", 1500, "below")
    
    # Display configured alerts
    print("Configured alerts:")
    print(get_price_alerts())
    
    # Test checking alerts
    print("Checking alerts...")
    triggered = check_price_alerts()
    
    if triggered:
        print(f"{len(triggered)} alerts activated")
    else:
        print("No alerts activated")