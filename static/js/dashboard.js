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

// Initialize auto-refresh
document.addEventListener('DOMContentLoaded', function() {
    // Set up price auto-refresh (every 30 seconds)
    setInterval(updatePrices, 30000);
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
