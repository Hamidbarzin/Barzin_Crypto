"""
سیستم مدیریت حافظه نهان (Cache) برای کاهش درخواست‌های API

این ماژول برای ذخیره موقت داده‌های دریافتی از API‌های خارجی استفاده می‌شود
تا تعداد درخواست‌ها را کاهش دهد و سرعت بارگذاری صفحات را افزایش دهد.
"""

import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CacheManager:
    """مدیریت حافظه نهان برای داده‌های API"""
    
    def __init__(self, default_ttl_seconds: int = 60):
        """
        راه‌اندازی مدیریت حافظه نهان
        
        Args:
            default_ttl_seconds: مدت زمان پیش‌فرض اعتبار داده در حافظه نهان (ثانیه)
        """
        self.cache = {}  # کلید: (مقدار، زمان انقضا)
        self.default_ttl_seconds = default_ttl_seconds
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
            logger.debug(f"Cache miss for key: {key}")
            return None
        
        value, expire_time = self.cache[key]
        
        # بررسی اعتبار داده
        if expire_time < time.time():
            logger.debug(f"Cache expired for key: {key}")
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        ذخیره داده در حافظه نهان
        
        Args:
            key: کلید داده
            value: داده برای ذخیره
            ttl_seconds: مدت زمان اعتبار (ثانیه)، اگر None باشد از مقدار پیش‌فرض استفاده می‌شود
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl_seconds
        
        expire_time = time.time() + ttl_seconds
        self.cache[key] = (value, expire_time)
        logger.debug(f"Cache set for key: {key}, expires in {ttl_seconds} seconds")
    
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
            logger.debug(f"Cache deleted for key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """پاک کردن تمام داده‌های حافظه نهان"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup(self) -> int:
        """
        حذف داده‌های منقضی شده
        
        Returns:
            تعداد کلیدهای حذف شده
        """
        now = time.time()
        expired_keys = [k for k, (_, expire_time) in self.cache.items() if expire_time < now]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """
        آمار حافظه نهان
        
        Returns:
            آمار مربوط به حافظه نهان
        """
        now = time.time()
        total = len(self.cache)
        expired = sum(1 for _, expire_time in self.cache.values() if expire_time < now)
        valid = total - expired
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': expired,
            'oldest_entry_ttl': min((expire_time - now for _, expire_time in self.cache.values()), default=0) if self.cache else 0,
            'newest_entry_ttl': max((expire_time - now for _, expire_time in self.cache.values()), default=0) if self.cache else 0,
            'average_ttl': sum((expire_time - now for _, expire_time in self.cache.values())) / total if total > 0 else 0
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
        
        logger.debug(f"Cache get_multiple: {len(result)}/{len(keys)} hits")
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
        
        logger.debug(f"Cache set_multiple: {len(items)} items")


# ایجاد یک نمونه از مدیر حافظه نهان برای استفاده در کل برنامه
# زمان اعتبار پیش‌فرض 180 ثانیه (3 دقیقه) برای قیمت‌ها
price_cache = CacheManager(default_ttl_seconds=180)

# زمان اعتبار پیش‌فرض 600 ثانیه (10 دقیقه) برای اخبار و تحلیل‌ها
news_cache = CacheManager(default_ttl_seconds=600)