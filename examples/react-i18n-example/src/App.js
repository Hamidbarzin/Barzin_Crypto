// src/App.js - کامپوننت اصلی برنامه
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import CryptoDashboard from './CryptoDashboard';
import './App.css';

function App() {
  const { i18n, t } = useTranslation();

  // تنظیم جهت متن بر اساس زبان فعلی در هنگام بارگذاری
  useEffect(() => {
    document.documentElement.dir = i18n.language === 'fa' ? 'rtl' : 'ltr';
    document.body.className = i18n.language === 'fa' ? 'rtl' : 'ltr';
  }, [i18n.language]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>{t('app.title')}</h1>
        <p>{t('app.description')}</p>
        <LanguageSwitcher />
      </header>
      
      <nav className="app-navigation">
        <ul>
          <li><a href="#home">{t('nav.home')}</a></li>
          <li><a href="#dashboard" className="active">{t('nav.dashboard')}</a></li>
          <li><a href="#settings">{t('nav.settings')}</a></li>
        </ul>
      </nav>
      
      <main className="app-content">
        <CryptoDashboard />
      </main>
      
      <footer className="app-footer">
        <p>© ۱۴۰۴ - طراح و توسعه دهنده: حمید برزین</p>
      </footer>
    </div>
  );
}

export default App;