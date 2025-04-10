// src/api.js - کلاس مدیریت درخواست‌های API با پشتیبانی چندزبانگی
import axios from 'axios';
import i18n from './i18n';

// ایجاد نمونه axios با تنظیمات پایه
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// افزودن interceptor درخواست برای گنجاندن زبان فعلی
api.interceptors.request.use(config => {
  // دریافت زبان فعلی
  const language = i18n.language || 'en';
  
  // افزودن زبان به پرسش URL
  if (config.url.includes('?')) {
    config.url = `${config.url}&lang=${language}`;
  } else {
    config.url = `${config.url}?lang=${language}`;
  }
  
  // افزودن زبان به هدرها
  config.headers['Accept-Language'] = language;
  
  return config;
});

// کلاس‌های Api برای مدیریت درخواست‌های مختلف
export const CryptoApi = {
  getPrices: () => api.get('/crypto/prices'),
  getTechnicalAnalysis: (symbol) => api.get(`/crypto/technical/${symbol}`),
  getSignals: () => api.get('/crypto/signals'),
  
  // متدهای مدیریت هشدارهای قیمت
  createAlert: (data) => api.post('/price-alerts', data),
  getAlerts: () => api.get('/price-alerts'),
  updateAlert: (id, data) => api.put(`/price-alerts/${id}`, data),
  deleteAlert: (id) => api.delete(`/price-alerts/${id}`),
};

export const UserApi = {
  // متدهای مربوط به تنظیمات کاربر
  getPreferences: () => api.get('/user/preferences'),
  updatePreferences: (data) => api.post('/user/preferences', data),
  
  // متد خاص برای به‌روزرسانی زبان
  updateLanguage: (language) => api.post('/user/preferences/language', { language }),
};

export default api;