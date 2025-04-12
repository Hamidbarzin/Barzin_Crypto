"""
سیستم مدیریت حافظه نهان (Cache) برای کاهش درخواست‌های API

این ماژول برای ذخیره موقت داده‌های دریافتی از API‌های خارجی استفاده می‌شود
تا تعداد درخواست‌ها را کاهش دهد و سرعت بارگذاری صفحات را افزایش دهد.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """مدیریت حافظه نهان برای داده‌های API"""
    
    def __init__(self, default_ttl_seconds: int = 60):
        """
        راه‌اندازی مدیریت حافظه نهان
        
        Args:
            default_ttl_seconds: مدت زمان پیش‌فرض اعتبار داده در حافظه نهان (ثانیه)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl_seconds
        logger.info(f"Cache manager initialized with default TTL of {default_ttl_seconds} seconds")
    
    def get(self, key: str) -> Optional[Any]:
        """
        دریافت داده از حافظه نهان
        
        Args:
            key: کلید داده
            
        Returns:
            داده ذخیره شده یا None اگر کلید منقضی شده یا وجود نداشته باشد
        """
        if key not in self.cache:
            return None
        
        value, expiry = self.cache[key]
        current_time = time.time()
        
        if current_time > expiry:
            # حذف داده منقضی شده
            logger.debug(f"Cache key '{key}' expired and removed")
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for key '{key}'")
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        ذخیره داده در حافظه نهان
        
        Args:
            key: کلید داده
            value: داده برای ذخیره
            ttl_seconds: مدت زمان اعتبار (ثانیه)، اگر None باشد از مقدار پیش‌فرض استفاده می‌شود
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = time.time() + ttl
        
        self.cache[key] = (value, expiry)
        logger.debug(f"Cache set for key '{key}' with TTL {ttl} seconds")
    
    def delete(self, key: str) -> bool:
        """
        حذف داده از حافظه نهان
        
        Args:
            key: کلید داده
            
        Returns:
            آیا داده حذف شد
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache key '{key}' manually deleted")
            return True
        return False
    
    def clear(self) -> None:
        """پاک کردن تمام داده‌های حافظه نهان"""
        self.cache.clear()
        logger.info("Cache cleared completely")
    
    def cleanup(self) -> int:
        """
        حذف داده‌های منقضی شده
        
        Returns:
            تعداد کلیدهای حذف شده
        """
        current_time = time.time()
        expired_keys = [k for k, (_, exp) in self.cache.items() if current_time > exp]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache keys")
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """
        آمار حافظه نهان
        
        Returns:
            آمار مربوط به حافظه نهان
        """
        current_time = time.time()
        total_items = len(self.cache)
        expired_items = sum(1 for _, exp in self.cache.values() if current_time > exp)
        valid_items = total_items - expired_items
        
        # میانگین زمان باقیمانده برای داده‌های معتبر
        remaining_ttls = [exp - current_time for _, exp in self.cache.values() 
                         if current_time <= exp]
        avg_remaining_ttl = sum(remaining_ttls) / len(remaining_ttls) if remaining_ttls else 0
        
        return {
            "total_items": total_items,
            "valid_items": valid_items,
            "expired_items": expired_items,
            "avg_remaining_ttl": avg_remaining_ttl
        }
    
    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """
        دریافت چندین داده از حافظه نهان
        
        Args:
            keys: لیست کلیدها
            
        Returns:
            دیکشنری از کلیدها و مقادیر معتبر
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        
        logger.debug(f"Cache multi-get: found {len(result)} of {len(keys)} keys")
        return result
    
    def set_multiple(self, items: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """
        ذخیره چندین داده در حافظه نهان
        
        Args:
            items: دیکشنری از کلیدها و مقادیر
            ttl_seconds: مدت زمان اعتبار (ثانیه)
        """
        for key, value in items.items():
            self.set(key, value, ttl_seconds)
        
        logger.debug(f"Cache multi-set: stored {len(items)} keys")


# نمونه سازی یک نمونه عمومی از مدیریت حافظه نهان
# TTL پیش‌فرض: 5 دقیقه
price_cache = CacheManager(default_ttl_seconds=300)  # برای قیمت‌ها
news_cache = CacheManager(default_ttl_seconds=1800)  # برای اخبار (30 دقیقه)
technical_cache = CacheManager(default_ttl_seconds=900)  # برای تحلیل تکنیکال (15 دقیقه)