"""
ماژول تولید نمودارهای تحلیل فنی برای ارزهای دیجیتال

این ماژول با استفاده از کتابخانه‌های matplotlib و mplfinance، نمودارهای تحلیل تکنیکال
مانند کندل استیک، MACD، RSI و میانگین متحرک را تولید می‌کند.
"""

import os
import random
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import mplfinance as mpf

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('chart_generator')

# مسیر ذخیره نمودارها
CHART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'charts')
os.makedirs(CHART_DIR, exist_ok=True)

def generate_random_ohlc_data(symbol="BTC/USDT", days=30, base_price=None, volatility=0.05):
    """
    تولید داده‌های قیمتی تصادفی برای تست
    
    Args:
        symbol (str): نماد ارز
        days (int): تعداد روزها
        base_price (float): قیمت پایه (اگر None باشد، مقدار تصادفی تولید می‌شود)
        volatility (float): میزان نوسان
        
    Returns:
        pd.DataFrame: دیتافریم داده‌های قیمتی
    """
    # تنظیم قیمت پایه
    if base_price is None:
        if 'BTC' in symbol:
            base_price = 65000
        elif 'ETH' in symbol:
            base_price = 3500
        elif 'SOL' in symbol:
            base_price = 150
        elif 'XRP' in symbol:
            base_price = 0.5
        else:
            base_price = 100
    
    # تولید تاریخ‌های متوالی
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # تولید داده‌های قیمت
    np.random.seed(42)  # برای تولید مقادیر یکسان در هر اجرا
    
    # روند کلی قیمت
    trend = np.random.choice([-1, 1], p=[0.3, 0.7])  # احتمال بیشتر برای روند صعودی
    trend_strength = np.random.uniform(0.001, 0.003)
    
    # تولید قیمت‌های پایه
    price_changes = np.random.normal(trend * trend_strength, volatility, size=len(date_range))
    price_multipliers = np.cumprod(1 + price_changes)
    closes = base_price * price_multipliers
    
    # تولید قیمت‌های باز شدن، بالاترین و پایین‌ترین
    opens = closes * np.random.uniform(0.99, 1.01, size=len(date_range))
    highs = np.maximum(opens, closes) * np.random.uniform(1.001, 1.02, size=len(date_range))
    lows = np.minimum(opens, closes) * np.random.uniform(0.98, 0.999, size=len(date_range))
    
    # تولید حجم معاملات
    volumes = np.random.normal(base_price * 1000, base_price * 500, size=len(date_range))
    volumes = np.abs(volumes)
    
    # ایجاد دیتافریم
    df = pd.DataFrame({
        'Date': date_range,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    })
    
    # تنظیم ستون تاریخ به عنوان ایندکس
    df.set_index('Date', inplace=True)
    
    return df

def get_historical_data(symbol="BTC/USDT", timeframe="1d", limit=30):
    """
    دریافت داده‌های تاریخی از API
    در این نسخه از داده‌های تصادفی استفاده می‌کنیم
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        limit (int): تعداد داده‌ها
        
    Returns:
        pd.DataFrame: دیتافریم داده‌های تاریخی
    """
    try:
        # در نسخه نهایی اینجا باید از API واقعی استفاده شود
        df = generate_random_ohlc_data(symbol=symbol, days=limit)
        logger.info(f"داده‌های تاریخی برای {symbol} تولید شد")
        return df
    except Exception as e:
        logger.error(f"خطا در دریافت داده‌های تاریخی: {e}")
        # در صورت خطا، داده‌های تصادفی تولید می‌کنیم
        return generate_random_ohlc_data(symbol=symbol, days=limit)

def calculate_indicators(df):
    """
    محاسبه شاخص‌های تکنیکال
    
    Args:
        df (pd.DataFrame): دیتافریم داده‌های قیمتی
        
    Returns:
        pd.DataFrame: دیتافریم با شاخص‌های اضافه شده
    """
    # کپی از دیتافریم اصلی
    data = df.copy()
    
    # محاسبه میانگین متحرک ساده 20 روزه و 50 روزه
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    
    # محاسبه میانگین متحرک نمایی 12 روزه و 26 روزه برای MACD
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    
    # محاسبه MACD و سیگنال
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # محاسبه RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # محاسبه باندهای بولینگر
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    data['BB_Std'] = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2)
    data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2)
    
    return data

def generate_candlestick_chart(symbol="BTC/USDT", timeframe="1d", days=30):
    """
    تولید نمودار کندل استیک با شاخص‌های تکنیکال
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        days (int): تعداد روزها
        
    Returns:
        str: مسیر فایل نمودار تولید شده
    """
    try:
        # دریافت داده‌های تاریخی
        df = get_historical_data(symbol=symbol, timeframe=timeframe, limit=days)
        
        # محاسبه شاخص‌ها
        data = calculate_indicators(df)
        
        # تنظیمات استایل نمودار
        mc = mpf.make_marketcolors(
            up='green', down='red',
            wick={'up': 'green', 'down': 'red'},
            volume={'up': 'green', 'down': 'red'},
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            figcolor='white',
            facecolor='white',
            edgecolor='black',
            gridcolor='gray',
            gridstyle=':',
            rc={'font.size': 10}
        )
        
        # اضافه کردن میانگین‌های متحرک به نمودار
        apds = [
            mpf.make_addplot(data['SMA20'], color='blue', width=0.7),
            mpf.make_addplot(data['SMA50'], color='orange', width=0.7),
            # اضافه کردن باندهای بولینگر
            mpf.make_addplot(data['BB_Upper'], color='gray', width=0.5, linestyle='--'),
            mpf.make_addplot(data['BB_Lower'], color='gray', width=0.5, linestyle='--'),
        ]
        
        # تعیین مسیر فایل خروجی
        symbol_name = symbol.replace('/', '_')
        filename = f"chart_{symbol_name}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(CHART_DIR, filename)
        
        # تنظیم عنوان نمودار
        title = f"نمودار {symbol} - {timeframe}"
        
        # رسم نمودار کندل استیک
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=s,
            addplot=apds,
            volume=True,
            figsize=(12, 8),
            title=title,
            returnfig=True
        )
        
        # ذخیره نمودار
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"نمودار کندل استیک برای {symbol} ایجاد شد: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"خطا در تولید نمودار کندل استیک: {e}")
        return None

def generate_technical_chart(symbol="BTC/USDT", timeframe="1d", days=30):
    """
    تولید نمودار تحلیل تکنیکال شامل MACD و RSI
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        days (int): تعداد روزها
        
    Returns:
        str: مسیر فایل نمودار تولید شده
    """
    try:
        # دریافت داده‌های تاریخی
        df = get_historical_data(symbol=symbol, timeframe=timeframe, limit=days)
        
        # محاسبه شاخص‌ها
        data = calculate_indicators(df)
        
        # ایجاد نمودار با 3 بخش: قیمت، MACD و RSI
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # نمودار قیمت و میانگین‌های متحرک
        axes[0].plot(data.index, data['Close'], label='قیمت', color='black')
        axes[0].plot(data.index, data['SMA20'], label='SMA20', color='blue')
        axes[0].plot(data.index, data['SMA50'], label='SMA50', color='orange')
        axes[0].plot(data.index, data['BB_Upper'], label='BB Upper', color='gray', linestyle='--')
        axes[0].plot(data.index, data['BB_Lower'], label='BB Lower', color='gray', linestyle='--')
        axes[0].set_title(f"تحلیل تکنیکال {symbol} - {timeframe}")
        axes[0].legend(loc='upper left')
        axes[0].grid(True, linestyle='--', alpha=0.6)
        
        # MACD
        axes[1].plot(data.index, data['MACD'], label='MACD', color='blue')
        axes[1].plot(data.index, data['Signal'], label='Signal', color='red')
        axes[1].bar(data.index, data['MACD'] - data['Signal'], color=['green' if (data['MACD'] - data['Signal']).iloc[i] >= 0 else 'red' for i in range(len(data))], alpha=0.5)
        axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        axes[1].set_title('MACD')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, linestyle='--', alpha=0.6)
        
        # RSI
        axes[2].plot(data.index, data['RSI'], label='RSI', color='purple')
        axes[2].axhline(y=70, color='red', linestyle='--', alpha=0.5)
        axes[2].axhline(y=30, color='green', linestyle='--', alpha=0.5)
        axes[2].set_title('RSI')
        axes[2].set_ylim(0, 100)
        axes[2].legend(loc='upper left')
        axes[2].grid(True, linestyle='--', alpha=0.6)
        
        # تنظیم فرمت محور x در همه زیرنمودارها
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
        # تنظیم فاصله بین زیرنمودارها
        plt.tight_layout()
        
        # تعیین مسیر فایل خروجی
        symbol_name = symbol.replace('/', '_')
        filename = f"technical_{symbol_name}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(CHART_DIR, filename)
        
        # ذخیره نمودار
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"نمودار تحلیل تکنیکال برای {symbol} ایجاد شد: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"خطا در تولید نمودار تحلیل تکنیکال: {e}")
        return None

def generate_all_charts(symbol="BTC/USDT", timeframe="1d", days=30):
    """
    تولید تمام نمودارهای تحلیلی برای یک ارز
    
    Args:
        symbol (str): نماد ارز
        timeframe (str): بازه زمانی
        days (int): تعداد روزها
        
    Returns:
        dict: دیکشنری مسیر فایل‌های نمودار تولید شده
    """
    charts = {}
    
    # تولید نمودار کندل استیک
    candlestick_chart = generate_candlestick_chart(symbol=symbol, timeframe=timeframe, days=days)
    if candlestick_chart:
        charts['candlestick'] = candlestick_chart
    
    # تولید نمودار تحلیل تکنیکال
    technical_chart = generate_technical_chart(symbol=symbol, timeframe=timeframe, days=days)
    if technical_chart:
        charts['technical'] = technical_chart
    
    return charts

def main():
    """
    تابع اصلی برای تست ماژول
    """
    symbol = "BTC/USDT"
    timeframe = "1d"
    days = 30
    
    logger.info(f"شروع تولید نمودارها برای {symbol}")
    
    # تولید تمام نمودارها
    charts = generate_all_charts(symbol=symbol, timeframe=timeframe, days=days)
    
    # نمایش مسیرهای فایل‌های تولید شده
    for chart_type, filepath in charts.items():
        logger.info(f"نمودار {chart_type}: {filepath}")
    
    logger.info("تولید نمودارها به پایان رسید")

if __name__ == "__main__":
    main()