#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت اجرای ربات هوشمند برای استفاده در Replit Workflows

این اسکریپت برای اجرای ربات به صورت دائمی در محیط Replit طراحی شده است.
"""

import logging
import time
import sys
import os
import traceback

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("smart_bot_workflow.log")
    ]
)
logger = logging.getLogger("smart_bot_workflow")

def run_smart_bot():
    """
    اجرای ربات هوشمند
    """
    try:
        logger.info("شروع اجرای ربات هوشمند در گردش کار Replit")
        
        # ارسال یک پیام تست
        import simple_ai_mode
        logger.info("در حال ارسال پیام تست...")
        simple_ai_mode.send_test_message()
        
        # شروع زمانبندی اصلی
        import smart_ai_scheduler
        
        # اجرای زمان‌بندی
        logger.info("در حال اجرای زمان‌بندی...")
        smart_ai_scheduler.main()
        
        return True
    except Exception as e:
        logger.error(f"خطا در اجرای ربات هوشمند: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        run_smart_bot()
    except KeyboardInterrupt:
        logger.info("اجرای ربات با دستور کاربر متوقف شد")
        sys.exit(0)
    except Exception as e:
        logger.error(f"خطای کلی در اجرای ربات: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)