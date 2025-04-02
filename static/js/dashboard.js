// Dashboard JavaScript functionality

// Update prices in real-time
function updatePrices() {
    const symbols = [];
    
    // Collect all symbols from the price table
    document.querySelectorAll('#priceTableBody tr').forEach(row => {
        symbols.push(row.getAttribute('data-symbol'));
    });
    
    if (symbols.length === 0) return;
    
    // Fetch current prices for all symbols
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

// Update a single price row with new data
function updatePriceRow(symbol, data) {
    const row = document.querySelector(`#priceTableBody tr[data-symbol="${symbol}"]`);
    if (!row) return;
    
    // Get current price for comparison
    const priceCell = row.querySelector('.price-value');
    const oldPrice = parseFloat(priceCell.textContent.replace('$', ''));
    const newPrice = data.price;
    
    // Update price with animation
    priceCell.textContent = '$' + newPrice.toFixed(2);
    
    // Flash green/red based on price change
    if (newPrice > oldPrice) {
        priceCell.classList.add('price-up');
        setTimeout(() => priceCell.classList.remove('price-up'), 1000);
    } else if (newPrice < oldPrice) {
        priceCell.classList.add('price-down');
        setTimeout(() => priceCell.classList.remove('price-down'), 1000);
    }
    
    // Update other cells if available
    if (data.change_24h !== undefined) {
        const changeCell = row.querySelector('td:nth-child(3)');
        changeCell.textContent = data.change_24h.toFixed(2) + '%';
        changeCell.className = data.change_24h >= 0 ? 'price-up' : 'price-down';
    }
}

// Format numbers with comma separators
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// Function to refresh commodity data
function refreshCommodities() {
    console.log('Refreshing commodities...');
    fetch('/api/commodities')
        .then(response => response.json())
        .then(data => {
            console.log('Commodities data received:', data);
            if (data.success) {
                // Update gold
                if (data.data.GOLD) {
                    const goldPrice = document.querySelector('.gold-price');
                    if (goldPrice) {
                        goldPrice.textContent = '$' + data.data.GOLD.price.toFixed(2);
                    } else {
                        console.error('Element with class gold-price not found');
                    }
                    
                    const goldChange = document.querySelector('.gold-change');
                    if (goldChange) {
                        goldChange.textContent = data.data.GOLD.change.toFixed(2) + '%';
                        goldChange.className = 'badge gold-change ' + (data.data.GOLD.change > 0 ? 'bg-success' : 'bg-danger');
                    } else {
                        console.error('Element with class gold-change not found');
                    }
                }
                
                // Update silver
                if (data.data.SILVER) {
                    const silverPrice = document.querySelector('.silver-price');
                    if (silverPrice) {
                        silverPrice.textContent = '$' + data.data.SILVER.price.toFixed(2);
                    } else {
                        console.error('Element with class silver-price not found');
                    }
                    
                    const silverChange = document.querySelector('.silver-change');
                    if (silverChange) {
                        silverChange.textContent = data.data.SILVER.change.toFixed(2) + '%';
                        silverChange.className = 'badge silver-change ' + (data.data.SILVER.change > 0 ? 'bg-success' : 'bg-danger');
                    } else {
                        console.error('Element with class silver-change not found');
                    }
                }
                
                // Update oil
                if (data.data.OIL) {
                    const oilPrice = document.querySelector('.oil-price');
                    if (oilPrice) {
                        oilPrice.textContent = '$' + data.data.OIL.price.toFixed(2);
                    } else {
                        console.error('Element with class oil-price not found');
                    }
                    
                    const oilChange = document.querySelector('.oil-change');
                    if (oilChange) {
                        oilChange.textContent = data.data.OIL.change.toFixed(2) + '%';
                        oilChange.className = 'badge oil-change ' + (data.data.OIL.change > 0 ? 'bg-success' : 'bg-danger');
                    } else {
                        console.error('Element with class oil-change not found');
                    }
                }
            }
        })
        .catch(error => console.error('Error updating commodities:', error));
}

// Function to refresh forex rates
function refreshForex() {
    console.log('Refreshing forex rates...');
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
                } else {
                    console.error('Forex table body not found');
                }
            }
        })
        .catch(error => console.error('Error updating forex rates:', error));
}

// Function to refresh economic indicators
function refreshEconomic() {
    console.log('Refreshing economic indicators...');
    fetch('/api/economic')
        .then(response => response.json())
        .then(data => {
            console.log('Economic data received:', data);
            if (data.success && data.data) {
                // Update recession risk
                if (data.data.recession_risk) {
                    const element = document.querySelector('.economic-indicator.risk-low, .economic-indicator.risk-medium, .economic-indicator.risk-high');
                    if (element) {
                        console.log('Recession risk element found, updating...');
                        // Update class based on risk level
                        element.className = 'economic-indicator ' + 
                            (data.data.recession_risk.value === 'کم' ? 'risk-low' : 
                                (data.data.recession_risk.value === 'متوسط' ? 'risk-medium' : 'risk-high'));
                        
                        // Update value and trend
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
                
                // Update other indicators similarly
                // Global markets
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
                
                // Inflation
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
                
                // Interest rates
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

// Initialize auto-refresh
document.addEventListener('DOMContentLoaded', function() {
    // Set up price auto-refresh (every 30 seconds)
    setInterval(updatePrices, 30000);
    
    // Set up refresh buttons for new sections
    const refreshCommoditiesBtn = document.getElementById('refreshCommodities');
    if (refreshCommoditiesBtn) {
        refreshCommoditiesBtn.addEventListener('click', function() {
            refreshCommodities();
            this.disabled = true;
            setTimeout(() => { this.disabled = false; }, 3000); // Prevent spam clicks
        });
    }
    
    const refreshForexBtn = document.getElementById('refreshForex');
    if (refreshForexBtn) {
        refreshForexBtn.addEventListener('click', function() {
            refreshForex();
            this.disabled = true;
            setTimeout(() => { this.disabled = false; }, 3000);
        });
    }
    
    const refreshEconomicBtn = document.getElementById('refreshEconomic');
    if (refreshEconomicBtn) {
        refreshEconomicBtn.addEventListener('click', function() {
            refreshEconomic();
            this.disabled = true;
            setTimeout(() => { this.disabled = false; }, 3000);
        });
    }
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
