// src/i18n.js - تنظیمات چندزبانگی برای React
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

i18n
  // بارگذاری ترجمه‌ها از /public/locales
  .use(Backend)
  // تشخیص زبان کاربر
  .use(LanguageDetector)
  // انتقال نمونه i18n به react-i18next
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'fa'],
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // برای React نیازی نیست
    },
    
    // کنترل جهت زبان
    react: {
      useSuspense: true,
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'querystring'],
      caches: ['localStorage'],
    },
  });

export default i18n;