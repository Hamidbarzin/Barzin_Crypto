// فایل جاوااسکریپت جایگزین برای داشبورد
console.log('dashboard_fix.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, running dashboard_fix.js');
    
    // بروزرسانی بخش قیمت‌های جاری
    function updatePrices() {
        const symbols = [];
        
        document.querySelectorAll('#priceTableBody tr').forEach(row => {
            symbols.push(row.getAttribute('data-symbol'));
        });
        
        if (symbols.length === 0) {
            console.log('No symbols found in price table');
            return;
        }
        
        console.log('Updating prices for:', symbols);
        
        symbols.forEach(symbol => {
            fetch(`/api/price/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.data[symbol]) {
                        updatePriceRow(symbol, data.data[symbol]);
                    }
                })
                .catch(error => console.error('Error updating prices:', error));
        });
    }
    
    // بروزرسانی ردیف قیمت
    function updatePriceRow(symbol, data) {
        const row = document.querySelector(`#priceTableBody tr[data-symbol="${symbol}"]`);
        if (!row) {
            console.error(`No row found for symbol ${symbol}`);
            return;
        }
        
        const priceCell = row.querySelector('.price-value');
        if (!priceCell) {
            console.error(`No price cell found for symbol ${symbol}`);
            return;
        }
        
        const oldPrice = parseFloat(priceCell.textContent.replace('$', ''));
        const newPrice = data.price;
        
        priceCell.textContent = '$' + newPrice.toFixed(2);
        
        if (newPrice > oldPrice) {
            priceCell.classList.add('price-up');
            setTimeout(() => priceCell.classList.remove('price-up'), 1000);
        } else if (newPrice < oldPrice) {
            priceCell.classList.add('price-down');
            setTimeout(() => priceCell.classList.remove('price-down'), 1000);
        }
        
        if (data.change_24h !== undefined) {
            const changeCell = row.querySelector('td:nth-child(3)');
            if (changeCell) {
                changeCell.textContent = data.change_24h.toFixed(2) + '%';
                changeCell.className = data.change_24h >= 0 ? 'price-up' : 'price-down';
            }
        }
    }
    
    // فرمت‌کردن اعداد
    function formatNumber(num) {
        return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    }
    
    // بروزرسانی اطلاعات کالاها (طلا، نقره، نفت)
    function updateCommodities() {
        console.log('Updating commodities...');
        
        fetch('/api/commodities')
            .then(response => response.json())
            .then(data => {
                console.log('Commodities data received:', data);
                
                if (data.success && data.data) {
                    // بروزرسانی طلا
                    if (data.data.GOLD) {
                        const goldPrice = document.querySelector('.gold-price');
                        if (goldPrice) {
                            goldPrice.textContent = '$' + data.data.GOLD.price.toFixed(2);
                            console.log('Updated gold price');
                        } else {
                            console.error('Element with class gold-price not found');
                        }
                        
                        const goldChange = document.querySelector('.gold-change');
                        if (goldChange) {
                            goldChange.textContent = data.data.GOLD.change.toFixed(2) + '%';
                            goldChange.className = 'badge gold-change ' + (data.data.GOLD.change > 0 ? 'bg-success' : 'bg-danger');
                            console.log('Updated gold change');
                        } else {
                            console.error('Element with class gold-change not found');
                        }
                    }
                    
                    // بروزرسانی نقره
                    if (data.data.SILVER) {
                        const silverPrice = document.querySelector('.silver-price');
                        if (silverPrice) {
                            silverPrice.textContent = '$' + data.data.SILVER.price.toFixed(2);
                            console.log('Updated silver price');
                        } else {
                            console.error('Element with class silver-price not found');
                        }
                        
                        const silverChange = document.querySelector('.silver-change');
                        if (silverChange) {
                            silverChange.textContent = data.data.SILVER.change.toFixed(2) + '%';
                            silverChange.className = 'badge silver-change ' + (data.data.SILVER.change > 0 ? 'bg-success' : 'bg-danger');
                            console.log('Updated silver change');
                        } else {
                            console.error('Element with class silver-change not found');
                        }
                    }
                    
                    // بروزرسانی نفت
                    if (data.data.OIL) {
                        const oilPrice = document.querySelector('.oil-price');
                        if (oilPrice) {
                            oilPrice.textContent = '$' + data.data.OIL.price.toFixed(2);
                            console.log('Updated oil price');
                        } else {
                            console.error('Element with class oil-price not found');
                        }
                        
                        const oilChange = document.querySelector('.oil-change');
                        if (oilChange) {
                            oilChange.textContent = data.data.OIL.change.toFixed(2) + '%';
                            oilChange.className = 'badge oil-change ' + (data.data.OIL.change > 0 ? 'bg-success' : 'bg-danger');
                            console.log('Updated oil change');
                        } else {
                            console.error('Element with class oil-change not found');
                        }
                    }
                }
            })
            .catch(error => console.error('Error updating commodities:', error));
    }
    
    // بروزرسانی اطلاعات ارزهای جهانی
    function updateForex() {
        console.log('Updating forex rates...');
        
        fetch('/api/forex')
            .then(response => response.json())
            .then(data => {
                console.log('Forex data received:', data);
                
                if (data.success && data.data) {
                    const forexTableBody = document.querySelector('.forex-table tbody');
                    if (forexTableBody) {
                        console.log('Forex table body found, updating...');
                        forexTableBody.innerHTML = '';
                        
                        for (const [symbol, info] of Object.entries(data.data)) {
                            const row = document.createElement('tr');
                            row.className = 'forex-row';
                            row.innerHTML = `
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="ms-2">
                                            <h6 class="mb-0">${info.name}</h6>
                                            <small class="text-muted">${symbol}</small>
                                        </div>
                                    </div>
                                </td>
                                <td>${info.price.toFixed(4)}</td>
                                <td>
                                    <span class="badge ${info.change > 0 ? 'bg-success' : 'bg-danger'}">
                                        ${info.change.toFixed(2)}%
                                    </span>
                                </td>
                            `;
                            forexTableBody.appendChild(row);
                        }
                        console.log('Forex table updated');
                    } else {
                        console.error('Forex table body not found');
                        console.log('Searching for any table element...');
                        const tables = document.querySelectorAll('table');
                        console.log(`Found ${tables.length} tables on the page`);
                    }
                }
            })
            .catch(error => console.error('Error updating forex rates:', error));
    }
    
    // بروزرسانی شاخص‌های اقتصادی
    function updateEconomic() {
        console.log('Updating economic indicators...');
        
        fetch('/api/economic')
            .then(response => response.json())
            .then(data => {
                console.log('Economic data received:', data);
                
                if (data.success && data.data) {
                    // بروزرسانی خطر رکود
                    if (data.data.recession_risk) {
                        const element = document.querySelector('.economic-indicator.risk-low, .economic-indicator.risk-medium, .economic-indicator.risk-high');
                        if (element) {
                            console.log('Recession risk element found, updating...');
                            element.className = 'economic-indicator ' + 
                                (data.data.recession_risk.value === 'کم' ? 'risk-low' : 
                                    (data.data.recession_risk.value === 'متوسط' ? 'risk-medium' : 'risk-high'));
                            
                            const valueElem = element.querySelector('.fw-bold');
                            if (valueElem) valueElem.textContent = data.data.recession_risk.value;
                            
                            const trendElem = element.querySelector('.badge');
                            if (trendElem) {
                                trendElem.textContent = data.data.recession_risk.trend;
                                trendElem.className = 'badge bg-secondary trend-' + 
                                    (data.data.recession_risk.trend === 'رو به بالا' ? 'up' : 
                                        (data.data.recession_risk.trend === 'رو به پایین' ? 'down' : 'stable'));
                            }
                        } else {
                            console.error('Recession risk element not found');
                        }
                    }
                    
                    // بروزرسانی بازارهای جهانی
                    if (data.data.global_markets) {
                        const status = document.querySelector('.global-markets-status');
                        if (status) {
                            console.log('Global markets status element found, updating...');
                            status.textContent = data.data.global_markets.status;
                        } else {
                            console.error('Global markets status element not found');
                        }
                        
                        const trend = document.querySelector('.global-markets-trend');
                        if (trend) {
                            trend.textContent = data.data.global_markets.trend;
                        } else {
                            console.error('Global markets trend element not found');
                        }
                    }
                    
                    // بروزرسانی تورم
                    if (data.data.inflation) {
                        const value = document.querySelector('.inflation-value');
                        if (value) {
                            console.log('Inflation value element found, updating...');
                            value.textContent = data.data.inflation.value;
                        } else {
                            console.error('Inflation value element not found');
                        }
                        
                        const trend = document.querySelector('.inflation-trend');
                        if (trend) {
                            trend.textContent = data.data.inflation.trend;
                        } else {
                            console.error('Inflation trend element not found');
                        }
                    }
                    
                    // بروزرسانی نرخ بهره
                    if (data.data.interest_rates) {
                        const value = document.querySelector('.interest-rates-value');
                        if (value) {
                            console.log('Interest rates value element found, updating...');
                            value.textContent = data.data.interest_rates.value;
                        } else {
                            console.error('Interest rates value element not found');
                        }
                        
                        const trend = document.querySelector('.interest-rates-trend');
                        if (trend) {
                            trend.textContent = data.data.interest_rates.trend;
                        } else {
                            console.error('Interest rates trend element not found');
                        }
                    }
                }
            })
            .catch(error => console.error('Error updating economic indicators:', error));
    }
    
    // اضافه کردن تمام المنت‌های HTML موردنیاز اگر وجود نداشته باشند
    function fixMissingElements() {
        console.log('Checking for missing elements...');
        
        // بخش کالاها
        const commoditiesSection = document.querySelector('#commodities-section');
        if (!commoditiesSection) {
            console.log('Creating commodities section...');
            
            // پیدا کردن محل مناسب برای قرار دادن بخش کالاها
            const container = document.querySelector('.container') || document.querySelector('.container-fluid');
            
            if (container) {
                const newSection = document.createElement('div');
                newSection.id = 'commodities-section';
                newSection.className = 'row mb-4';
                newSection.innerHTML = `
                    <div class="col-12">
                        <div class="card dashboard-card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h3 class="mb-0">کالاها و ارزهای جهانی</h3>
                                <button id="refreshCommodities" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-sync-alt ms-1"></i> بروزرسانی
                                </button>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4 mb-4 mb-md-0">
                                        <div class="card commodity-card h-100 shadow-sm">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-center mb-3">
                                                    <div class="commodity-icon gold-bg">
                                                        <i class="fas fa-coins"></i>
                                                    </div>
                                                    <span class="badge gold-change bg-success">0.75%</span>
                                                </div>
                                                <h4 class="card-title">طلا - اونس</h4>
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <h5 class="mb-0 gold-price">$2250.50</h5>
                                                    <small class="text-muted">XAU/USD</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4 mb-md-0">
                                        <div class="card commodity-card h-100 shadow-sm">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-center mb-3">
                                                    <div class="commodity-icon silver-bg">
                                                        <i class="fas fa-coins"></i>
                                                    </div>
                                                    <span class="badge silver-change bg-danger">-0.25%</span>
                                                </div>
                                                <h4 class="card-title">نقره - اونس</h4>
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <h5 class="mb-0 silver-price">$28.75</h5>
                                                    <small class="text-muted">XAG/USD</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card commodity-card h-100 shadow-sm">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-center mb-3">
                                                    <div class="commodity-icon oil-bg">
                                                        <i class="fas fa-gas-pump"></i>
                                                    </div>
                                                    <span class="badge oil-change bg-success">1.2%</span>
                                                </div>
                                                <h4 class="card-title">نفت - بشکه</h4>
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <h5 class="mb-0 oil-price">$82.35</h5>
                                                    <small class="text-muted">OIL/USD</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // افزودن بخش جدید به صفحه
                const dashboardHeader = document.querySelector('.dashboard-header');
                if (dashboardHeader && dashboardHeader.nextElementSibling) {
                    container.insertBefore(newSection, dashboardHeader.nextElementSibling.nextElementSibling);
                } else {
                    container.appendChild(newSection);
                }
            }
        }
        
        // بخش ارزهای جهانی
        const forexSection = document.querySelector('#forex-section');
        if (!forexSection) {
            console.log('Creating forex section...');
            
            const container = document.querySelector('.container') || document.querySelector('.container-fluid');
            
            if (container) {
                const newSection = document.createElement('div');
                newSection.id = 'forex-section';
                newSection.className = 'row mb-4';
                newSection.innerHTML = `
                    <div class="col-lg-6">
                        <div class="card dashboard-card h-100 mb-0">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h3 class="mb-0">ارز‌های جهانی</h3>
                                <button id="refreshForex" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-sync-alt ms-1"></i> بروزرسانی
                                </button>
                            </div>
                            <div class="card-body p-0">
                                <table class="table data-table forex-table mb-0">
                                    <thead>
                                        <tr>
                                            <th>ارز</th>
                                            <th>قیمت</th>
                                            <th>تغییر</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <!-- این بخش به صورت داینامیک پر می‌شود -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="card dashboard-card h-100 mb-0">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h3 class="mb-0">شاخص‌های اقتصادی</h3>
                                <button id="refreshEconomic" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-sync-alt ms-1"></i> بروزرسانی
                                </button>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="economic-indicator risk-medium mb-3">
                                            <h5 class="mb-2">وضعیت ریسک رکود</h5>
                                            <div class="d-flex justify-content-between">
                                                <span class="fw-bold">متوسط</span>
                                                <span class="badge bg-secondary trend-stable">ثابت</span>
                                            </div>
                                        </div>
                                        <div class="economic-indicator mb-3">
                                            <h5 class="mb-2">وضعیت بازارهای جهانی</h5>
                                            <div class="d-flex justify-content-between">
                                                <span class="fw-bold text-success global-markets-status">مثبت</span>
                                                <span class="badge bg-secondary trend-up global-markets-trend">رو به بالا</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="economic-indicator mb-3">
                                            <h5 class="mb-2">نرخ تورم جهانی</h5>
                                            <div class="d-flex justify-content-between">
                                                <span class="fw-bold inflation-value">3.2%</span>
                                                <span class="badge bg-success trend-down inflation-trend">رو به پایین</span>
                                            </div>
                                        </div>
                                        <div class="economic-indicator mb-3">
                                            <h5 class="mb-2">نرخ بهره</h5>
                                            <div class="d-flex justify-content-between">
                                                <span class="fw-bold interest-rates-value">5.25%</span>
                                                <span class="badge bg-secondary trend-stable interest-rates-trend">ثابت</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // افزودن بخش جدید به صفحه
                const commoditiesSection = document.querySelector('#commodities-section');
                if (commoditiesSection) {
                    container.insertBefore(newSection, commoditiesSection.nextElementSibling);
                } else {
                    container.appendChild(newSection);
                }
            }
        }
        
        // اضافه کردن لیستنرها به دکمه‌های جدید
        const refreshCommoditiesBtn = document.getElementById('refreshCommodities');
        if (refreshCommoditiesBtn) {
            refreshCommoditiesBtn.addEventListener('click', function() {
                console.log('Refresh commodities button clicked');
                updateCommodities();
                this.disabled = true;
                setTimeout(() => { this.disabled = false; }, 3000);
            });
        }
        
        const refreshForexBtn = document.getElementById('refreshForex');
        if (refreshForexBtn) {
            refreshForexBtn.addEventListener('click', function() {
                console.log('Refresh forex button clicked');
                updateForex();
                this.disabled = true;
                setTimeout(() => { this.disabled = false; }, 3000);
            });
        }
        
        const refreshEconomicBtn = document.getElementById('refreshEconomic');
        if (refreshEconomicBtn) {
            refreshEconomicBtn.addEventListener('click', function() {
                console.log('Refresh economic button clicked');
                updateEconomic();
                this.disabled = true;
                setTimeout(() => { this.disabled = false; }, 3000);
            });
        }
        
        const mainRefreshBtn = document.getElementById('refreshBtn');
        if (mainRefreshBtn) {
            mainRefreshBtn.addEventListener('click', function() {
                console.log('Main refresh button clicked');
                updatePrices();
                updateCommodities();
                updateForex();
                updateEconomic();
            });
        }
    }
    
    // فانکشن اصلی برای شروع همه فعالیت‌ها
    function initializeDashboard() {
        console.log('Initializing dashboard...');
        
        // ترمیم المان‌های مفقود شده
        fixMissingElements();
        
        // اجرای فانکشن‌های بروزرسانی
        setTimeout(() => {
            console.log('Initial data refresh...');
            updatePrices();
            updateCommodities();
            updateForex();
            updateEconomic();
            
            // راه‌اندازی تایمر برای بروزرسانی خودکار
            setInterval(updatePrices, 30000);
            setInterval(updateCommodities, 300000);
            setInterval(updateForex, 300000);
            setInterval(updateEconomic, 600000);
        }, 1000);
    }
    
    // شروع کار داشبورد
    initializeDashboard();
});