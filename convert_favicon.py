#!/usr/bin/env python3
"""
این اسکریپت برای تبدیل آیکون SVG به PNG استفاده می‌شود
"""

import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def convert_svg_to_png(svg_path, png_path, width=32, height=32):
    """
    تبدیل فایل SVG به PNG
    
    Args:
        svg_path (str): مسیر فایل SVG
        png_path (str): مسیر فایل PNG خروجی
        width (int): عرض تصویر خروجی
        height (int): ارتفاع تصویر خروجی
    
    Returns:
        bool: نتیجه تبدیل
    """
    try:
        # تبدیل SVG به گرافیک قابل رندر
        drawing = svg2rlg(svg_path)
        
        # رندر کردن به PNG
        renderPM.drawToFile(drawing, png_path, fmt="PNG")
        
        print(f"تبدیل با موفقیت انجام شد: {svg_path} -> {png_path}")
        return True
    except Exception as e:
        print(f"خطا در تبدیل SVG به PNG: {e}")
        return False

def main():
    """
    تابع اصلی برنامه
    """
    svg_path = "static/icons/favicon-en.svg"
    png_path_32 = "static/icons/favicon-32x32.png"
    png_path_apple = "static/icons/apple-touch-icon.png"
    
    # تبدیل برای favicon-32x32.png
    convert_svg_to_png(svg_path, png_path_32, width=32, height=32)
    
    # تبدیل برای apple-touch-icon.png
    convert_svg_to_png(svg_path, png_path_apple, width=180, height=180)

if __name__ == "__main__":
    main()