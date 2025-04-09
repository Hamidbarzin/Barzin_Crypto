// سیستم ساده‌ی تب‌ها بدون وابستگی به بوت‌استرپ

// نمایش تب انتخاب شده
function showTab(tabId) {
    console.log('Showing tab with ID:', tabId);
    
    // مخفی کردن همه تب‌ها
    const tabs = document.querySelectorAll('.content-tab');
    tabs.forEach(tab => {
        tab.style.display = 'none';
    });
    
    // غیرفعال کردن همه دکمه‌های تب
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => {
        button.classList.remove('active');
    });
    
    // نمایش تب انتخاب شده
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.style.display = 'block';
        
        // فعال کردن دکمه مربوطه
        const selectedButton = document.querySelector(`[data-tab="${tabId}"]`);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
        
        // اگر تب سیگنال‌ها فعال شد، قیمت‌ها را به‌روز کن
        if (tabId === 'signals-tab') {
            updateSignalPrices();
        }
    } else {
        console.error('Tab not found:', tabId);
    }
}

// به‌روزرسانی قیمت‌های واقعی در کارت‌های سیگنال
function updateSignalPrices() {
    try {
        console.log('Updating signal prices');
        
        // دریافت قیمت بیت‌کوین
        const btcPrice = document.getElementById('BTC-USDT-price')?.textContent;
        if (btcPrice && btcPrice !== '--') {
            const btcSignalPrice = document.getElementById('btc-signal-price');
            if (btcSignalPrice) {
                console.log('Updating BTC price to:', btcPrice);
                btcSignalPrice.textContent = btcPrice;
            }
        }
        
        // دریافت قیمت اتریوم
        const ethPrice = document.getElementById('ETH-USDT-price')?.textContent;
        if (ethPrice && ethPrice !== '--') {
            const ethSignalPrice = document.getElementById('eth-signal-price');
            if (ethSignalPrice) {
                console.log('Updating ETH price to:', ethPrice);
                ethSignalPrice.textContent = ethPrice;
            }
        }
    } catch (error) {
        console.error('Error updating signal prices:', error);
    }
}

// مقداردهی اولیه هنگام بارگذاری صفحه
document.addEventListener('DOMContentLoaded', function() {
    // نمایش تب اولیه (تب فنی)
    showTab('technical-tab');
    
    // به‌روزرسانی خودکار قیمت‌ها هر ۳۰ ثانیه
    setInterval(updateSignalPrices, 30000);
});