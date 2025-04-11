/**
 * ماژول به‌روزرسانی قیمت ارزهای دیجیتال
 * 
 * این فایل برای به‌روزرسانی خودکار قیمت‌های ارزهای دیجیتال در سایت استفاده می‌شود.
 * با استفاده از تکنیک‌های بهینه‌سازی مانند صف درخواست‌ها و تأخیر زمانی بین آن‌ها،
 * از محدودیت‌های API اجتناب می‌کند.
 */

// آرایه‌های سکه‌ها برای به‌روزرسانی خودکار - ارزهای میم و ارزان حذف شده‌اند
const aiCoins = ['RNDR', 'FET', 'OCEAN', 'AGIX'];

// برای مدیریت سکه‌هایی که در حال به‌روزرسانی هستند
const updatingCoins = new Set();

// تابع اصلی به‌روزرسانی ارزهای دیجیتال ویژه
function updateSpecialCoins() {
    console.log("Updating AI coins only");
    
    // ارزهای میم و ارزان حذف شده‌اند
    const allCoins = [...aiCoins];
    
    console.log("Coins to update:", allCoins);
    
    // به‌روزرسانی هر سکه با تاخیر متفاوت برای جلوگیری از درخواست‌های همزمان زیاد
    allCoins.forEach((coin, index) => {
        setTimeout(() => {
            if (!updatingCoins.has(coin)) {
                updatingCoins.add(coin);
                console.log(`Updating ${coin} price...`);
                
                // مستقیم فراخوانی API برای هر سکه
                fetch(`/api/price/${coin.toLowerCase()}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log(`API response for ${coin}:`, data);
                        if (data.success && data.data && data.data.price) {
                            const price = parseFloat(data.data.price);
                            const change = parseFloat(data.data.change_24h || 0);
                            
                            // آپدیت قیمت با استفاده از ID استاندارد
                            const priceElement = document.getElementById(`${coin}-USDT-price`);
                            if (priceElement) {
                                priceElement.textContent = formatPrice(price);
                                console.log(`Successfully updated ${coin} price to ${price}`);
                            } else {
                                console.error(`Price element for ${coin} not found!`);
                            }
                            
                            // آپدیت درصد تغییرات با استفاده از ID استاندارد
                            const changeElement = document.getElementById(`${coin}-USDT-change`);
                            if (changeElement) {
                                changeElement.textContent = formatChange(change);
                                if (change >= 0) {
                                    changeElement.classList.add('positive-change');
                                    changeElement.classList.remove('negative-change');
                                } else {
                                    changeElement.classList.add('negative-change');
                                    changeElement.classList.remove('positive-change');
                                }
                            } else {
                                console.error(`Change element for ${coin} not found!`);
                            }
                        }
                    })
                    .catch(error => {
                        console.error(`Error updating ${coin}:`, error);
                    })
                    .finally(() => {
                        setTimeout(() => {
                            updatingCoins.delete(coin);
                        }, 5000); // پاک کردن از لیست در حال به‌روزرسانی‌ها بعد از 5 ثانیه
                    });
            }
        }, index * 500); // تاخیر 500 میلی‌ثانیه بین هر سکه
    });
}

// تابع به‌روزرسانی قیمت یک سکه مشخص
function updateCoinPrice(coin) {
    fetch(`/api/price/${coin.toLowerCase()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(response => {
            if (response && response.success && response.data) {
                const data = response.data;
                if (data && data.price) {
                    const price = parseFloat(data.price);
                    const change = parseFloat(data.change_24h || 0);
                    
                    const coinSymbol = coin.toUpperCase();
                    
                    // آپدیت قیمت با استفاده از ID استاندارد
                    const priceElement = document.getElementById(`${coinSymbol}-USDT-price`);
                    if (priceElement) {
                        priceElement.textContent = formatPrice(price);
                        console.log(`Successfully updated ${coin} price to ${price}`);
                    }
                    
                    // آپدیت درصد تغییرات با استفاده از ID استاندارد
                    const changeElement = document.getElementById(`${coinSymbol}-USDT-change`);
                    if (changeElement) {
                        changeElement.textContent = formatChange(change);
                        if (change >= 0) {
                            changeElement.classList.add('positive-change');
                            changeElement.classList.remove('negative-change');
                        } else {
                            changeElement.classList.add('negative-change');
                            changeElement.classList.remove('positive-change');
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error(`Error updating ${coin}:`, error);
        });
}

// تابع قالب‌بندی قیمت بر اساس بزرگی اعداد
function formatPrice(price) {
    // Format based on price magnitude
    if (price >= 1000) {
        return price.toLocaleString('en-US', {maximumFractionDigits: 0});
    } else if (price >= 1) {
        return price.toLocaleString('en-US', {maximumFractionDigits: 2});
    } else if (price >= 0.01) {
        return price.toLocaleString('en-US', {maximumFractionDigits: 4});
    } else {
        return price.toLocaleString('en-US', {maximumFractionDigits: 8});
    }
}

// تابع قالب‌بندی درصد تغییرات
function formatChange(change) {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
}

// تابع به‌روزرسانی قیمت‌های ارزهای اصلی
function updateMainCoins() {
    console.log("Updating prices for:", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]);
    
    // Update prices at intervals to avoid overwhelming the API
    setTimeout(() => { updateCoinPrice('BTC'); }, 100);
    setTimeout(() => { updateCoinPrice('ETH'); }, 900);
    setTimeout(() => { updateCoinPrice('SOL'); }, 1700);
    setTimeout(() => { updateCoinPrice('XRP'); }, 2500);
}

// تابع به‌روزرسانی قیمت در سیگنال‌ها
function updateSignalPrices() {
    try {
        console.log('Updating signal prices');
        
        // دریافت قیمت بیت‌کوین با استفاده از ID استاندارد جدید
        const btcPrice = document.getElementById('BTC-USDT-price')?.textContent;
        if (btcPrice && btcPrice !== '--') {
            const btcSignalPrice = document.getElementById('btc-signal-price');
            if (btcSignalPrice) {
                console.log('Updating BTC price to:', btcPrice);
                btcSignalPrice.textContent = btcPrice + ' USDT';
            }
        }
        
        // دریافت قیمت اتریوم با استفاده از ID استاندارد جدید
        const ethPrice = document.getElementById('ETH-USDT-price')?.textContent;
        if (ethPrice && ethPrice !== '--') {
            const ethSignalPrice = document.getElementById('eth-signal-price');
            if (ethSignalPrice) {
                console.log('Updating ETH price to:', ethPrice);
                ethSignalPrice.textContent = ethPrice + ' USDT';
            }
        }
    } catch (error) {
        console.error('Error updating signal prices:', error);
    }
}

// راه‌اندازی به‌روزرسانی قیمت‌ها در هنگام بارگذاری صفحه
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded - initializing cryptocurrency updates");
    
    // به‌روزرسانی اولیه
    updateMainCoins();
    console.log("Main coins update initialized");
    
    // به‌روزرسانی فوری ارزهای ویژه
    updateSpecialCoins();
    console.log("Special coins update initialized");
    
    // چک کردن المان‌های قیمت
    setTimeout(checkPriceElements, 2000);
    
    // به‌روزرسانی خودکار ارزهای اصلی هر 30 ثانیه
    setInterval(updateMainCoins, 30000);
    
    // به‌روزرسانی خودکار ارزهای ویژه هر 45 ثانیه
    setInterval(updateSpecialCoins, 45000);
});

// بررسی موجود بودن المان‌های قیمت در DOM
function checkPriceElements() {
    const allCoins = ['BTC', 'ETH', 'SOL', 'XRP', ...aiCoins];
    
    console.log("Checking price elements for these coins:", allCoins);
    
    allCoins.forEach(coin => {
        const priceEl = document.getElementById(`${coin}-USDT-price`);
        const changeEl = document.getElementById(`${coin}-USDT-change`);
        
        if (priceEl) {
            console.log(`✓ Price element for ${coin} found`);
            // به روزرسانی مستقیم
            updateCoinPrice(coin);
        } else {
            console.error(`✗ Price element for ${coin} NOT found!`);
        }
        
        if (!changeEl) {
            console.error(`✗ Change element for ${coin} NOT found!`);
        }
    });
}