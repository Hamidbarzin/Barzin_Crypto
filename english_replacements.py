#!/usr/bin/env python3
import re

def replace_persian_terms(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define replacements
    replacements = [
        # Signal indicators
        ("farsi_signal = 'خرید'", "farsi_signal = 'Buy'"),
        ("farsi_signal = 'خرید قوی'", "farsi_signal = 'Strong Buy'"),
        ("farsi_signal = 'فروش'", "farsi_signal = 'Sell'"),
        ("farsi_signal = 'خنثی'", "farsi_signal = 'Neutral'"),
        
        # Recommendations
        ('farsi_recommendation = "پیشنهاد معامله نوسانی (صعودی)"', 'farsi_recommendation = "Consider swing trade (bullish)"'),
        ('farsi_recommendation = "نقطه ورود مناسب برای معامله نوسانی صعودی"', 'farsi_recommendation = "Good entry point for bullish swing trade"'),
        ('farsi_recommendation = "پیشنهاد معامله نوسانی (نزولی)"', 'farsi_recommendation = "Consider swing trade (bearish)"'),
        ('farsi_recommendation = "منتظر سیگنال‌های واضح‌تر باشید"', 'farsi_recommendation = "Wait for clearer signals"')
    ]
    
    # Apply replacements
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Persian terms have been replaced with English in {file_path}")

if __name__ == "__main__":
    replace_persian_terms('main.py')
