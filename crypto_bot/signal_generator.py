"""
ماژول تولید سیگنال‌های معاملاتی

این ماژول سیگنال‌های خرید و فروش را بر اساس تحلیل تکنیکال تولید می‌کند.
"""

import logging
from typing import Dict, List, Any, Optional

from crypto_bot.technical_analysis import get_technical_analysis

logger = logging.getLogger(__name__)

def generate_signals(symbols: List[str], timeframe: str = "1d") -> Dict[str, List[Dict[str, Any]]]:
    """
    تولید سیگنال‌های معاملاتی برای مجموعه‌ای از ارزها
    
    Args:
        symbols (List[str]): لیست نمادهای ارزهای دیجیتال
        timeframe (str): بازه زمانی
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: دیکشنری شامل لیست سیگنال‌های خرید و فروش
    """
    try:
        buy_signals = []
        sell_signals = []
        
        for symbol in symbols:
            # تحلیل تکنیکال ارز
            analysis = get_technical_analysis(symbol, timeframe)
            
            # اگر تحلیل با خطا مواجه شده باشد، آن را نادیده می‌گیریم
            if 'error' in analysis:
                logger.warning(f"خطا در تحلیل {symbol}: {analysis['error']}")
                continue
                
            # تصمیم‌گیری بر اساس سیگنال
            signal = analysis.get('signal', 'خنثی')
            
            if 'خرید' in signal:
                signal_info = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal': signal,
                    'strength': analysis.get('signal_strength', 0)
                }
                
                # اضافه کردن سایر اطلاعات تحلیلی اگر موجود باشند
                for key in ['rsi', 'macd', 'ma20', 'ma50', 'ma200', 'bb_width']:
                    if key in analysis:
                        signal_info[key] = analysis[key]
                        
                buy_signals.append(signal_info)
                
            elif 'فروش' in signal:
                signal_info = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal': signal,
                    'strength': analysis.get('signal_strength', 0)
                }
                
                # اضافه کردن سایر اطلاعات تحلیلی اگر موجود باشند
                for key in ['rsi', 'macd', 'ma20', 'ma50', 'ma200', 'bb_width']:
                    if key in analysis:
                        signal_info[key] = analysis[key]
                
                sell_signals.append(signal_info)
        
        # مرتب‌سازی سیگنال‌ها بر اساس قدرت
        buy_signals = sorted(buy_signals, key=lambda x: x.get('strength', 0), reverse=True)
        sell_signals = sorted(sell_signals, key=lambda x: x.get('strength', 0), reverse=True)
        
        return {
            'buy': buy_signals,
            'sell': sell_signals
        }
            
    except Exception as e:
        logger.error(f"خطا در تولید سیگنال‌های معاملاتی: {str(e)}")
        return {
            'buy': [],
            'sell': []
        }

def get_signals_summary(signals: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    تهیه خلاصه‌ای از سیگنال‌های معاملاتی برای نمایش یا ارسال
    
    Args:
        signals (Dict[str, List[Dict[str, Any]]]): دیکشنری سیگنال‌های معاملاتی
        
    Returns:
        str: متن خلاصه سیگنال‌ها
    """
    summary = "🔔 *سیگنال‌های معاملاتی*\n\n"
    
    buy_signals = signals.get('buy', [])
    sell_signals = signals.get('sell', [])
    
    # سیگنال‌های خرید
    if buy_signals:
        summary += "🟢 *سیگنال‌های خرید:*\n"
        for i, signal in enumerate(buy_signals, 1):
            symbol = signal['symbol']
            signal_type = signal['signal']
            strength = signal.get('strength', 0)
            stars = "⭐" * min(5, strength)
            
            summary += f"{i}. {symbol}: {signal_type} {stars}\n"
            
            # اضافه کردن اطلاعات تکمیلی
            if 'rsi' in signal:
                summary += f"   RSI: {signal['rsi']:.1f}"
            if 'macd' in signal:
                summary += f" | MACD: {signal['macd']:.4f}"
            summary += "\n"
    else:
        summary += "🟢 *سیگنال‌های خرید:* هیچ سیگنال خریدی یافت نشد.\n\n"
    
    # سیگنال‌های فروش
    if sell_signals:
        summary += "\n🔴 *سیگنال‌های فروش:*\n"
        for i, signal in enumerate(sell_signals, 1):
            symbol = signal['symbol']
            signal_type = signal['signal']
            strength = signal.get('strength', 0)
            stars = "⭐" * min(5, strength)
            
            summary += f"{i}. {symbol}: {signal_type} {stars}\n"
            
            # اضافه کردن اطلاعات تکمیلی
            if 'rsi' in signal:
                summary += f"   RSI: {signal['rsi']:.1f}"
            if 'macd' in signal:
                summary += f" | MACD: {signal['macd']:.4f}"
            summary += "\n"
    else:
        summary += "\n🔴 *سیگنال‌های فروش:* هیچ سیگنال فروشی یافت نشد.\n"
    
    return summary