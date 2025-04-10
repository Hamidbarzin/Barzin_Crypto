// src/LanguageSwitcher.js - کامپوننت تغییر زبان
import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();
  
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    // تنظیم ویژگی dir برای HTML برای پشتیبانی از RTL
    document.documentElement.dir = lng === 'fa' ? 'rtl' : 'ltr';
    // همچنین می‌توانید یک کلاس به body برای استایل‌دهی RTL اضافی اضافه کنید
    document.body.className = lng === 'fa' ? 'rtl' : 'ltr';
    
    // ذخیره زبان در localStorage برای استفاده در بارگذاری‌های بعدی
    localStorage.setItem('userLanguage', lng);
    
    // ذخیره در کوکی‌ها برای دسترسی سرور
    document.cookie = `lang=${lng}; path=/; max-age=${60*60*24*30}`; // ۳۰ روز
    
    // ارسال درخواست به API برای ذخیره ترجیح زبان کاربر در بک‌اند
    // این قسمت در صورتی که کاربر وارد شده است اجرا می‌شود
    if (window.isLoggedIn) {
      fetch('/api/user/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: lng }),
      }).catch(error => console.error('خطا در به‌روزرسانی ترجیح زبان:', error));
    }
  };

  return (
    <div className="language-switcher">
      <p>{t('language.select')}:</p>
      <div className="language-buttons">
        <button 
          onClick={() => changeLanguage('en')} 
          className={i18n.language === 'en' ? 'active' : ''}
        >
          🇺🇸 {t('language.english')}
        </button>
        <button 
          onClick={() => changeLanguage('fa')} 
          className={i18n.language === 'fa' ? 'active' : ''}
        >
          🇮🇷 {t('language.persian')}
        </button>
      </div>
    </div>
  );
};

export default LanguageSwitcher;