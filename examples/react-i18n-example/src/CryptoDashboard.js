// src/CryptoDashboard.js - کامپوننت داشبورد ارزهای دیجیتال
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './CryptoDashboard.css';

const CryptoDashboard = () => {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(true);
  
  // داده‌های نمونه برای مثال
  const [cryptoData, setCryptoData] = useState([
    { 
      id: 'bitcoin', 
      symbol: 'BTC', 
      price: 42500, 
      change: 2.5,
      signal: 'buy'
    },
    { 
      id: 'ethereum', 
      symbol: 'ETH', 
      price: 2280, 
      change: -1.8,
      signal: 'sell'
    },
    { 
      id: 'solana', 
      symbol: 'SOL', 
      price: 152, 
      change: 4.2,
      signal: 'buy'
    },
    { 
      id: 'binance_coin', 
      symbol: 'BNB', 
      price: 560, 
      change: 0.3,
      signal: 'wait'
    }
  ]);

  // شبیه‌سازی بارگذاری داده‌ها
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  // فرمت کردن قیمت
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 2
    }).format(price);
  };

  // فرمت کردن درصد تغییر
  const formatChange = (change) => {
    return `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
  };

  // رنگ متناسب با تغییر قیمت
  const getChangeClass = (change) => {
    return change > 0 ? 'positive-change' : change < 0 ? 'negative-change' : '';
  };

  // کلاس سیگنال معاملاتی
  const getSignalClass = (signal) => {
    switch(signal) {
      case 'buy': return 'signal-buy';
      case 'sell': return 'signal-sell';
      case 'wait': return 'signal-wait';
      default: return '';
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="crypto-dashboard">
      <h2>{t('dashboard.market_overview')}</h2>
      
      <div className="crypto-cards">
        {cryptoData.map(crypto => (
          <div key={crypto.id} className="crypto-card">
            <div className="crypto-header">
              <h3>{t(crypto.id)} ({crypto.symbol})</h3>
              <span className={`signal-badge ${getSignalClass(crypto.signal)}`}>
                {t(`crypto.signals.${crypto.signal}`)}
              </span>
            </div>
            
            <div className="crypto-body">
              <div className="price-info">
                <div className="price-row">
                  <span className="label">{t('crypto.price')}:</span>
                  <span className="value">{formatPrice(crypto.price)}</span>
                </div>
                <div className="price-row">
                  <span className="label">{t('crypto.change')}:</span>
                  <span className={`value ${getChangeClass(crypto.change)}`}>
                    {formatChange(crypto.change)}
                  </span>
                </div>
              </div>
              
              <div className="crypto-actions">
                {crypto.signal === 'buy' && (
                  <button className="action-button buy">
                    {t('crypto.signals.buy')}
                  </button>
                )}
                {crypto.signal === 'sell' && (
                  <button className="action-button sell">
                    {t('crypto.signals.sell')}
                  </button>
                )}
                {crypto.signal === 'wait' && (
                  <button className="action-button wait" disabled>
                    {t('crypto.signals.wait')}
                  </button>
                )}
                <button className="action-button alert">
                  {t('set_alert')}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="dashboard-footer">
        <p>{t('dashboard.trading_signals')}</p>
        <button>{t('show_signals_directly')}</button>
      </div>
    </div>
  );
};

export default CryptoDashboard;