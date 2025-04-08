#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تولیدکننده نمودار کندل استیک برای ارزهای دیجیتال

این ماژول با استفاده از کتابخانه های matplotlib و mplfinance
نمودارهای کندل استیک را برای ارزهای دیجیتال تولید می کند.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import logging
import time
from datetime import datetime, timedelta
import ccxt
import tempfile

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chart_generator")

# مسیر ذخیره موقت تصاویر
CHART_DIR = "static/charts"
os.makedirs(CHART_DIR, exist_ok=True)

def get_ohlcv_data(symbol, timeframe='1d', limit=30, exchange_id='binance'):
    """
    دریافت داده های OHLCV (قیمت باز، بالا، پایین، بسته و حجم) از صرافی
    
    Args:
        symbol (str): نماد ارز دیجیتال مانند BTC/USDT
        timeframe (str): بازه زمانی، مثلا 1d, 4h, 1h, 15m
        limit (int): تعداد کندل‌ها
        exchange_id (str): نام صرافی
        
    Returns:
        pandas.DataFrame: داده‌های OHLCV به صورت دیتافریم
    """
    try:
        logger.info(f"دریافت داده‌های OHLCV برای {symbol} با بازه زمانی {timeframe} از {exchange_id}")
        
        # تلاش برای استفاده از صرافی‌های مختلف در صورت خطا
        exchanges = ['kucoin', 'binance', 'coinex', 'kraken']
        
        # اگر صرافی وارد شده در لیست نباشد، آن را به ابتدای لیست اضافه می‌کنیم
        if exchange_id not in exchanges:
            exchanges.insert(0, exchange_id)
        else:
            # در غیر این صورت، صرافی را به ابتدای لیست منتقل می‌کنیم
            exchanges.remove(exchange_id)
            exchanges.insert(0, exchange_id)
        
        for ex_id in exchanges:
            try:
                # ساخت نمونه از صرافی
                exchange_class = getattr(ccxt, ex_id)
                exchange = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                
                # دریافت داده های OHLCV
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                # در صورت خالی بودن، به صرافی بعدی می‌رویم
                if not ohlcv:
                    logger.warning(f"صرافی {ex_id} داده‌های OHLCV خالی برای {symbol} برگرداند.")
                    continue
                    
                # تبدیل به دیتافریم
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # تبدیل timestamp به datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # تنظیم timestamp به عنوان ایندکس
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"داده‌های OHLCV با موفقیت از {ex_id} دریافت شدند. تعداد کندل‌ها: {len(df)}")
                
                return df
                
            except Exception as e:
                logger.error(f"خطا در دریافت داده‌های OHLCV از {ex_id}: {str(e)}")
                continue
        
        logger.error(f"هیچ یک از صرافی‌ها نتوانستند داده‌های OHLCV را برای {symbol} برگردانند.")
        return None
        
    except Exception as e:
        logger.error(f"خطا در دریافت داده‌های OHLCV: {str(e)}")
        return None

def generate_candlestick_chart(symbol, timeframe='1d', limit=30, title=None, filename=None):
    """
    تولید نمودار کندل استیک
    
    Args:
        symbol (str): نماد ارز دیجیتال مانند BTC/USDT
        timeframe (str): بازه زمانی، مثلا 1d, 4h, 1h, 15m
        limit (int): تعداد کندل‌ها
        title (str): عنوان نمودار
        filename (str): نام فایل خروجی
        
    Returns:
        str: مسیر فایل تصویر یا None در صورت خطا
    """
    try:
        logger.info(f"تولید نمودار کندل استیک برای {symbol} با بازه زمانی {timeframe}")
        
        # دریافت داده‌های OHLCV
        df = get_ohlcv_data(symbol, timeframe, limit)
        
        if df is None or len(df) < 2:
            logger.error(f"داده‌های OHLCV برای {symbol} کافی نیستند.")
            return None
            
        # اگر عنوان تعیین نشده باشد، به صورت خودکار می‌سازیم
        if title is None:
            title = f"نمودار {timeframe} {symbol}"
            
        # اگر نام فایل تعیین نشده باشد، به صورت خودکار می‌سازیم
        if filename is None:
            timestamp = int(time.time())
            filename = f"{symbol.replace('/', '_')}_{timeframe}_{timestamp}.png"
            filename = filename.replace('/', '_')
            
        # مسیر کامل فایل
        filepath = os.path.join(CHART_DIR, filename)
        
        # تنظیمات استایل نمودار
        s = mpf.make_mpf_style(
            base_mpf_style='yahoo',
            gridstyle='--',
            y_on_right=False,
            marketcolors=mpf.make_marketcolors(
                up='green',
                down='red',
                edge='inherit',
                wick='inherit',
                volume='inherit',
            )
        )
        
        # تولید نمودار کندل استیک با حجم و میانگین متحرک
        fig, axes = mpf.plot(
            df,
            type='candle',
            title=title,
            style=s,
            volume=True,
            figsize=(12, 8),
            returnfig=True,
            mav=(7, 25),  # میانگین‌های متحرک 7 و 25 روزه
            tight_layout=True
        )
        
        # تنظیم فونت‌های فارسی (اگر فونت فارسی در سیستم نصب شده باشد)
        plt.rcParams['font.family'] = 'sans-serif'
        
        # ذخیره نمودار
        fig.savefig(filepath, dpi=100)
        plt.close(fig)
        
        logger.info(f"نمودار کندل استیک با موفقیت در {filepath} ذخیره شد.")
        
        return filepath
        
    except Exception as e:
        logger.error(f"خطا در تولید نمودار کندل استیک: {str(e)}")
        return None

def generate_multi_timeframe_charts(symbol, timeframes=['1d', '4h', '1h'], limit=30):
    """
    تولید نمودارهای کندل استیک در چند بازه زمانی مختلف
    
    Args:
        symbol (str): نماد ارز دیجیتال مانند BTC/USDT
        timeframes (list): لیست بازه‌های زمانی
        limit (int): تعداد کندل‌ها
        
    Returns:
        list: لیست مسیرهای فایل‌های تصویر
    """
    try:
        logger.info(f"تولید نمودارهای کندل استیک برای {symbol} در بازه‌های زمانی مختلف")
        
        result = []
        
        for timeframe in timeframes:
            filepath = generate_candlestick_chart(symbol, timeframe, limit)
            if filepath:
                result.append(filepath)
        
        logger.info(f"تعداد {len(result)} نمودار کندل استیک تولید شد.")
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در تولید نمودارهای کندل استیک در بازه‌های زمانی مختلف: {str(e)}")
        return []

def generate_chart_for_telegram(symbol, timeframe='1d', limit=30):
    """
    تولید نمودار کندل استیک برای ارسال در تلگرام
    
    Args:
        symbol (str): نماد ارز دیجیتال مانند BTC/USDT
        timeframe (str): بازه زمانی، مثلا 1d, 4h, 1h, 15m
        limit (int): تعداد کندل‌ها
        
    Returns:
        str: مسیر فایل تصویر یا None در صورت خطا
    """
    try:
        logger.info(f"تولید نمودار کندل استیک برای ارسال در تلگرام: {symbol} ({timeframe})")
        
        # عنوان نمودار را به همراه تاریخ و زمان می‌سازیم
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"نمودار {symbol} - {timeframe} - {current_time}"
        
        # تولید نمودار
        filepath = generate_candlestick_chart(symbol, timeframe, limit, title=title)
        
        return filepath
        
    except Exception as e:
        logger.error(f"خطا در تولید نمودار برای تلگرام: {str(e)}")
        return None

# آزمایش تابع
if __name__ == "__main__":
    # تست تولید نمودار برای بیت‌کوین
    filepath = generate_chart_for_telegram("BTC/USDT", "1d", 30)
    print(f"نمودار در مسیر زیر ذخیره شد: {filepath}")
    
    # تست تولید نمودار برای اتریوم
    filepath = generate_chart_for_telegram("ETH/USDT", "1d", 30)
    print(f"نمودار در مسیر زیر ذخیره شد: {filepath}")