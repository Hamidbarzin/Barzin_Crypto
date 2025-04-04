#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت تست برای سیستم تحلیل تکنیکال

این اسکریپت به شما امکان می‌دهد سیستم تحلیل تکنیکال را تست کنید
و نتایج را در کنسول مشاهده کنید.
"""

import json
import logging
from pprint import pprint
import sys

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_technical_analysis")

def test_technical_analysis():
    """
    تست سیستم تحلیل تکنیکال
    """
    try:
        # وارد کردن ماژول‌ها
        logger.info("در حال وارد کردن ماژول‌های مورد نیاز...")
        from crypto_bot.technical_analysis import (
            get_sample_data, 
            calculate_indicators, 
            generate_signals, 
            get_latest_signals, 
            get_technical_analysis
        )
        logger.info("ماژول‌ها با موفقیت وارد شدند")
        
        # پارامترهای ورودی
        symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC/USDT"
        logger.info(f"در حال تست تحلیل تکنیکال برای {symbol}...")
        
        # دریافت داده‌های نمونه
        logger.info("دریافت داده‌های نمونه...")
        df = get_sample_data(symbol)
        logger.info(f"داده‌های نمونه با موفقیت ایجاد شدند: {len(df)} رکورد")
        
        # نمایش داده‌های اولیه
        print("\n=== داده‌های قیمت ===")
        print(df.tail().to_string())
        
        # محاسبه شاخص‌ها
        logger.info("محاسبه شاخص‌های تکنیکال...")
        df_with_indicators = calculate_indicators(df)
        
        # نمایش شاخص‌های مهم
        print("\n=== شاخص‌های تکنیکال ===")
        columns = ['close', 'sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal']
        print(df_with_indicators[columns].tail().to_string())
        
        # تولید سیگنال‌ها
        logger.info("تولید سیگنال‌های معاملاتی...")
        df_with_signals = generate_signals(df_with_indicators)
        
        # نمایش سیگنال‌ها
        print("\n=== سیگنال‌های معاملاتی ===")
        signal_columns = ['close', 'sma_signal', 'macd_signal_line', 'rsi_signal', 'bb_signal', 'combined_signal']
        print(df_with_signals[signal_columns].tail().to_string())
        
        # دریافت آخرین سیگنال‌ها
        logger.info("دریافت آخرین سیگنال‌ها...")
        latest_signals = get_latest_signals(symbol)
        
        # نمایش آخرین سیگنال‌ها
        print("\n=== آخرین سیگنال‌ها ===")
        print(json.dumps(latest_signals, indent=2, ensure_ascii=False))
        
        # دریافت تحلیل تکنیکال کامل
        logger.info("دریافت تحلیل تکنیکال کامل...")
        technical_analysis = get_technical_analysis(symbol)
        
        # نمایش تحلیل تکنیکال کامل
        print("\n=== تحلیل تکنیکال کامل ===")
        print(json.dumps(technical_analysis, indent=2, ensure_ascii=False))
        
        logger.info("تست با موفقیت انجام شد")
        return True
    
    except Exception as e:
        logger.error(f"خطا در تست سیستم تحلیل تکنیکال: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_telegram_technical_report():
    """
    تست گزارش تحلیل تکنیکال به تلگرام
    """
    try:
        logger.info("در حال تست ارسال گزارش تحلیل تکنیکال به تلگرام...")
        
        # وارد کردن ماژول‌ها
        import telegram_reporter
        
        # پارامترهای ورودی
        symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC/USDT"
        
        # تهیه گزارش تحلیل تکنیکال
        report = telegram_reporter.get_technical_report(symbol)
        
        # نمایش گزارش
        print("\n=== گزارش تحلیل تکنیکال ===")
        print(report)
        
        # پرسش از کاربر برای ارسال به تلگرام
        send_to_telegram = input("\nآیا می‌خواهید این گزارش به تلگرام ارسال شود؟ (y/n): ")
        
        if send_to_telegram.lower() == 'y':
            # ارسال گزارش به تلگرام
            result = telegram_reporter.send_technical_analysis(symbol)
            if result:
                logger.info("گزارش با موفقیت به تلگرام ارسال شد")
            else:
                logger.error("خطا در ارسال گزارش به تلگرام")
        
        logger.info("تست با موفقیت انجام شد")
        return True
    
    except Exception as e:
        logger.error(f"خطا در تست گزارش تلگرام: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("\n=== تست سیستم تحلیل تکنیکال ===\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--telegram':
        # حذف آرگومان تلگرام
        sys.argv.pop(1)
        # تست گزارش تلگرام
        test_telegram_technical_report()
    else:
        # تست تحلیل تکنیکال
        test_technical_analysis()