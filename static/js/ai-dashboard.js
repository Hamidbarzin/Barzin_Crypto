/**
 * داشبورد هوش مصنوعی
 * این فایل شامل کدهای جاوااسکریپت مربوط به داشبورد هوش مصنوعی است
 */

document.addEventListener('DOMContentLoaded', function() {
    // دکمه‌های انتخاب ارز
    const currencyButtons = document.querySelectorAll('.crypto-button');
    const symbolInput = document.getElementById('symbol-input');
    const analyzeButton = document.getElementById('analyze-button');
    
    // بخش‌های مختلف داشبورد
    const loadingSection = document.getElementById('loading-section');
    const pricePredictionSection = document.getElementById('price-prediction-section');
    const patternsSection = document.getElementById('patterns-section');
    const sentimentSection = document.getElementById('sentiment-section');
    const strategySection = document.getElementById('strategy-section');
    
    // دکمه‌های تنظیمات
    const timeframeButtons = document.querySelectorAll('.timeframe-btn');
    const riskButtons = document.querySelectorAll('.risk-btn');
    const strategyTimeframeButtons = document.querySelectorAll('.strategy-timeframe-btn');
    
    // متغیرهای سراسری
    let selectedSymbol = '';
    let selectedTimeframe = '24h';
    let selectedRisk = 'متوسط';
    let selectedStrategyTimeframe = 'کوتاه‌مدت';
    
    // اتصال رویدادها به دکمه‌های ارز
    currencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            selectedSymbol = this.getAttribute('data-symbol');
            analyzeCrypto(selectedSymbol);
            
            // به‌روزرسانی کلاس‌های CSS برای نمایش دکمه انتخاب شده
            currencyButtons.forEach(btn => btn.classList.remove('active', 'btn-warning'));
            currencyButtons.forEach(btn => btn.classList.add('btn-outline-warning'));
            this.classList.remove('btn-outline-warning');
            this.classList.add('active', 'btn-warning');
        });
    });
    
    // اتصال رویداد به دکمه تحلیل
    analyzeButton.addEventListener('click', function() {
        selectedSymbol = symbolInput.value.trim();
        if (selectedSymbol) {
            analyzeCrypto(selectedSymbol);
        }
    });
    
    // اتصال رویدادها به دکمه‌های بازه زمانی
    timeframeButtons.forEach(button => {
        button.addEventListener('click', function() {
            selectedTimeframe = this.getAttribute('data-timeframe');
            
            // به‌روزرسانی ظاهر دکمه‌ها
            timeframeButtons.forEach(btn => btn.classList.remove('active', 'btn-light'));
            timeframeButtons.forEach(btn => btn.classList.add('btn-outline-light'));
            this.classList.remove('btn-outline-light');
            this.classList.add('active', 'btn-light');
            
            // درخواست پیش‌بینی جدید
            fetchPricePrediction(selectedSymbol, selectedTimeframe);
        });
    });
    
    // اتصال رویدادها به دکمه‌های ریسک
    riskButtons.forEach(button => {
        button.addEventListener('click', function() {
            selectedRisk = this.getAttribute('data-risk');
            
            // به‌روزرسانی ظاهر دکمه‌ها
            riskButtons.forEach(btn => btn.classList.remove('active', 'btn-light'));
            riskButtons.forEach(btn => btn.classList.add('btn-outline-light'));
            this.classList.remove('btn-outline-light');
            this.classList.add('active', 'btn-light');
            
            // درخواست استراتژی جدید
            fetchTradingStrategy(selectedSymbol, selectedRisk, selectedStrategyTimeframe);
        });
    });
    
    // اتصال رویدادها به دکمه‌های افق زمانی استراتژی
    strategyTimeframeButtons.forEach(button => {
        button.addEventListener('click', function() {
            selectedStrategyTimeframe = this.getAttribute('data-timeframe');
            
            // به‌روزرسانی ظاهر دکمه‌ها
            strategyTimeframeButtons.forEach(btn => btn.classList.remove('active', 'btn-light'));
            strategyTimeframeButtons.forEach(btn => btn.classList.add('btn-outline-light'));
            this.classList.remove('btn-outline-light');
            this.classList.add('active', 'btn-light');
            
            // درخواست استراتژی جدید
            fetchTradingStrategy(selectedSymbol, selectedRisk, selectedStrategyTimeframe);
        });
    });
    
    /**
     * تحلیل ارز انتخاب شده و نمایش اطلاعات
     */
    function analyzeCrypto(symbol) {
        if (!symbol) return;
        
        console.log(`Analyzing ${symbol}...`);
        
        // نمایش بخش در حال بارگذاری
        loadingSection.classList.remove('d-none');
        pricePredictionSection.classList.add('d-none');
        patternsSection.classList.add('d-none');
        sentimentSection.classList.add('d-none');
        strategySection.classList.add('d-none');
        
        // به‌روزرسانی نماد ارز در همه بخش‌ها
        document.querySelectorAll('.selected-symbol').forEach(el => el.textContent = symbol);
        
        // فراخوانی API‌های مختلف
        Promise.all([
            fetchPricePrediction(symbol, selectedTimeframe),
            fetchPricePatterns(symbol),
            fetchMarketSentiment(),
            fetchTradingStrategy(symbol, selectedRisk, selectedStrategyTimeframe)
        ]).then(() => {
            // پنهان کردن بخش بارگذاری
            loadingSection.classList.add('d-none');
            
            // نمایش همه بخش‌های داشبورد
            pricePredictionSection.classList.remove('d-none');
            patternsSection.classList.remove('d-none');
            sentimentSection.classList.remove('d-none');
            strategySection.classList.remove('d-none');
        }).catch(error => {
            console.error('Error analyzing crypto:', error);
            loadingSection.classList.add('d-none');
        });
    }
    
    /**
     * دریافت پیش‌بینی قیمت
     */
    function fetchPricePrediction(symbol, timeframe) {
        return fetch(`/api/ai/price-prediction/${symbol}?timeframe=${timeframe}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updatePricePredictionUI(data.data, timeframe);
                } else {
                    console.error('Error fetching price prediction:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching price prediction:', error);
            });
    }
    
    /**
     * دریافت الگوهای قیمت
     */
    function fetchPricePatterns(symbol) {
        return fetch(`/api/ai/price-patterns/${symbol}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updatePatternsUI(data.data);
                } else {
                    console.error('Error fetching price patterns:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching price patterns:', error);
            });
    }
    
    /**
     * دریافت تحلیل احساسات بازار
     */
    function fetchMarketSentiment() {
        return fetch(`/api/ai/market-sentiment`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateSentimentUI(data.data);
                } else {
                    console.error('Error fetching market sentiment:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching market sentiment:', error);
            });
    }
    
    /**
     * دریافت استراتژی معاملاتی
     */
    function fetchTradingStrategy(symbol, riskLevel, timeframe) {
        return fetch(`/api/ai/trading-strategy/${symbol}?risk_level=${riskLevel}&timeframe=${timeframe}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStrategyUI(data.data);
                } else {
                    console.error('Error fetching trading strategy:', data.message);
                }
            })
            .catch(error => {
                console.error('Error fetching trading strategy:', error);
            });
    }
    
    /**
     * به‌روزرسانی رابط کاربری بخش پیش‌بینی قیمت
     */
    function updatePricePredictionUI(prediction, timeframe) {
        console.log('Updating price prediction UI:', prediction);
        
        // قیمت فعلی و پیش‌بینی شده
        document.querySelector('.current-price').textContent = formatPrice(prediction.current_price);
        document.querySelector('.predicted-price').textContent = formatPrice(prediction.predicted_price);
        
        // روند پیش‌بینی
        const trendElement = document.querySelector('.prediction-trend');
        trendElement.textContent = prediction.trend;
        
        // افق زمانی
        let timeHorizon = '24 ساعت آینده';
        if (timeframe === '7d') timeHorizon = '7 روز آینده';
        if (timeframe === '30d') timeHorizon = '30 روز آینده';
        document.querySelector('.time-horizon').textContent = timeHorizon;
        
        // دقت مدل
        const accuracy = prediction.model_accuracy || 0.7;
        document.querySelector('.model-accuracy').style.width = `${accuracy * 100}%`;
        document.querySelector('.model-accuracy-text').textContent = `${Math.round(accuracy * 100)}%`;
        
        // محدوده قیمت
        document.querySelector('.upper-bound').textContent = formatPrice(prediction.upper_bound);
        document.querySelector('.lower-bound').textContent = formatPrice(prediction.lower_bound);
        
        // عوامل مؤثر در پیش‌بینی
        if (prediction.factors) {
            const factors = prediction.factors;
            
            updateFactorBar('.factor-technical', '.factor-technical-bar', factors.technical || 0.65);
            updateFactorBar('.factor-sentiment', '.factor-sentiment-bar', factors.sentiment || 0.45);
            updateFactorBar('.factor-news', '.factor-news-bar', factors.news || 0.35);
            updateFactorBar('.factor-volume', '.factor-volume-bar', factors.volume || 0.8);
            updateFactorBar('.factor-historical', '.factor-historical-bar', factors.historical || 0.5);
        }
        
        // توصیه هوش مصنوعی
        const recElement = document.querySelector('.prediction-recommendation');
        recElement.textContent = prediction.recommendation || 'در حال حاضر روند صعودی پیش‌بینی می‌شود.';
        
        // به‌روزرسانی کلاس آلرت
        const alertElement = document.querySelector('.prediction-alert');
        if (prediction.trend === 'صعودی') {
            alertElement.className = 'alert alert-success prediction-alert';
        } else if (prediction.trend === 'نزولی') {
            alertElement.className = 'alert alert-danger prediction-alert';
        } else {
            alertElement.className = 'alert alert-warning prediction-alert';
        }
    }
    
    /**
     * به‌روزرسانی رابط کاربری بخش الگوهای قیمت
     */
    function updatePatternsUI(patterns) {
        console.log('Updating patterns UI:', patterns);
        
        const patternsContainer = document.querySelector('.patterns-list');
        const emptyNotice = document.querySelector('.patterns-empty');
        
        // پاک کردن محتوای قبلی
        patternsContainer.innerHTML = '';
        
        // بررسی وجود الگو
        if (!patterns.patterns_found || !patterns.identified_patterns || patterns.identified_patterns.length === 0) {
            emptyNotice.classList.remove('d-none');
            return;
        }
        
        // نمایش الگوها
        emptyNotice.classList.add('d-none');
        
        // ساخت کارت برای هر الگو
        patterns.identified_patterns.forEach(pattern => {
            // تعیین رنگ بر اساس سیگنال
            let cardColor = 'warning';
            if (pattern.signal === 'خرید') cardColor = 'success';
            if (pattern.signal === 'فروش') cardColor = 'danger';
            
            // ساخت HTML کارت
            const patternCard = `
                <div class="col-md-6 mb-3">
                    <div class="card h-100 border-${cardColor}">
                        <div class="card-header bg-${cardColor} bg-opacity-10">
                            <h6 class="card-title mb-0 d-flex justify-content-between">
                                <span>${pattern.pattern_name}</span>
                                <span class="badge bg-${cardColor}">${pattern.signal}</span>
                            </h6>
                        </div>
                        <div class="card-body">
                            <p>${pattern.description}</p>
                            <div class="mt-3">
                                <div class="d-flex justify-content-between mb-1">
                                    <span>درصد تکمیل:</span>
                                    <span>${pattern.completion_percentage}%</span>
                                </div>
                                <div class="progress mb-3" style="height: 8px;">
                                    <div class="progress-bar bg-${cardColor}" role="progressbar" style="width: ${pattern.completion_percentage}%"></div>
                                </div>
                                <div class="d-flex justify-content-between mb-1">
                                    <span>اطمینان:</span>
                                    <span>${Math.round(pattern.confidence * 100)}%</span>
                                </div>
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar bg-${cardColor}" role="progressbar" style="width: ${pattern.confidence * 100}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            patternsContainer.innerHTML += patternCard;
        });
    }
    
    /**
     * به‌روزرسانی رابط کاربری بخش تحلیل احساسات
     */
    function updateSentimentUI(sentiment) {
        console.log('Updating sentiment UI:', sentiment);
        
        // نمره کلی احساسات
        const score = sentiment.overall_sentiment;
        const normalizedScore = Math.round((score + 1) * 50); // تبدیل محدوده -1 تا 1 به 0 تا 100
        document.querySelector('.sentiment-score').textContent = score.toFixed(2);
        
        // برچسب احساسات
        const labelElement = document.querySelector('.sentiment-label');
        labelElement.textContent = sentiment.sentiment_label;
        
        // رنگ‌آمیزی بر اساس احساسات
        if (sentiment.sentiment_label === "مثبت") {
            labelElement.className = 'sentiment-label text-success';
            document.querySelector('.sentiment-chart').style.background = `conic-gradient(#198754 ${normalizedScore}%, #e9ecef 0)`;
        } else if (sentiment.sentiment_label === "منفی") {
            labelElement.className = 'sentiment-label text-danger';
            document.querySelector('.sentiment-chart').style.background = `conic-gradient(#dc3545 ${normalizedScore}%, #e9ecef 0)`;
        } else {
            labelElement.className = 'sentiment-label text-warning';
            document.querySelector('.sentiment-chart').style.background = `conic-gradient(#ffc107 ${normalizedScore}%, #e9ecef 0)`;
        }
        
        // توضیحات احساسات
        document.querySelector('.sentiment-description').textContent = sentiment.sentiment_description || '';
        
        // منابع مختلف
        updateFactorBar('.sentiment-news', '.sentiment-news-bar', mapSentimentToRange(0.3));
        updateFactorBar('.sentiment-social', '.sentiment-social-bar', mapSentimentToRange(0.1));
        updateFactorBar('.sentiment-forums', '.sentiment-forums-bar', mapSentimentToRange(-0.2));
        updateFactorBar('.sentiment-market', '.sentiment-market-bar', mapSentimentToRange(0.5));
        
        // کلمات کلیدی
        const keywordsContainer = document.querySelector('.sentiment-keywords');
        keywordsContainer.innerHTML = '';
        
        if (sentiment.keywords && sentiment.keywords.length > 0) {
            sentiment.keywords.forEach(keyword => {
                keywordsContainer.innerHTML += `<span class="badge bg-secondary">${keyword}</span>`;
            });
        }
        
        // آمار
        document.querySelector('.news-count').textContent = sentiment.news_analysis ? sentiment.news_analysis.length : 0;
        document.querySelector('.sentiment-date').textContent = sentiment.timestamp || new Date().toLocaleString('fa-IR');
    }
    
    /**
     * به‌روزرسانی رابط کاربری بخش استراتژی معاملاتی
     */
    function updateStrategyUI(strategy) {
        console.log('Updating strategy UI:', strategy);
        
        // نام و نوع استراتژی
        document.querySelector('.strategy-name').textContent = strategy.strategy_name || '';
        document.querySelector('.strategy-type').textContent = strategy.strategy_type || '';
        
        // بازه زمانی
        document.querySelector('.strategy-timeframe').textContent = strategy.timeframe || '';
        
        // سطح ریسک
        const confidence = strategy.confidence || 0.7;
        document.querySelector('.strategy-confidence').textContent = `${Math.round(confidence * 100)}%`;
        document.querySelector('.strategy-confidence-bar').style.width = `${confidence * 100}%`;
        
        // توضیحات استراتژی
        document.querySelector('.strategy-description').textContent = strategy.strategy_description || '';
        
        // شاخص‌های کلیدی
        const indicatorsContainer = document.querySelector('.key-indicators');
        indicatorsContainer.innerHTML = '';
        
        if (strategy.key_indicators && strategy.key_indicators.length > 0) {
            strategy.key_indicators.forEach(indicator => {
                indicatorsContainer.innerHTML += `<span class="badge bg-secondary me-2 mb-2">${indicator}</span>`;
            });
        }
        
        // نقاط ورود
        const entryPointsContainer = document.querySelector('.entry-points-list');
        entryPointsContainer.innerHTML = '';
        
        if (strategy.entry_points && strategy.entry_points.length > 0) {
            strategy.entry_points.forEach(point => {
                entryPointsContainer.innerHTML += `<li>${point}</li>`;
            });
        }
        
        // نقاط خروج
        const exitPointsContainer = document.querySelector('.exit-points-list');
        exitPointsContainer.innerHTML = '';
        
        if (strategy.exit_points && strategy.exit_points.length > 0) {
            strategy.exit_points.forEach(point => {
                exitPointsContainer.innerHTML += `<li>${point}</li>`;
            });
        }
        
        // حد ضرر و حد سود
        document.querySelector('.stop-loss').textContent = strategy.stop_loss || '';
        document.querySelector('.take-profit').textContent = strategy.take_profit || '';
        
        // نسبت ریسک به پاداش
        document.querySelector('.risk-reward-ratio').textContent = strategy.risk_reward_ratio || '';
    }
    
    /**
     * به‌روزرسانی نوار عامل
     */
    function updateFactorBar(valueSelector, barSelector, value) {
        const percentage = Math.round(value * 100);
        document.querySelector(valueSelector).textContent = `${percentage}%`;
        document.querySelector(barSelector).style.width = `${percentage}%`;
    }
    
    /**
     * تبدیل مقدار احساسات به درصد
     */
    function mapSentimentToRange(value) {
        // تبدیل مقدار -1 تا 1 به 0 تا 1
        return (value + 1) / 2;
    }
    
    /**
     * قالب‌بندی قیمت
     */
    function formatPrice(price) {
        if (!price) return '0';
        
        // اگر قیمت کمتر از 0.01 باشد، تا 8 رقم اعشار نمایش داده شود
        if (price < 0.01) {
            return price.toFixed(8);
        }
        
        // اگر قیمت کمتر از 1 باشد، تا 6 رقم اعشار نمایش داده شود
        if (price < 1) {
            return price.toFixed(6);
        }
        
        // اگر قیمت کمتر از 100 باشد، تا 4 رقم اعشار نمایش داده شود
        if (price < 100) {
            return price.toFixed(4);
        }
        
        // اگر قیمت کمتر از 10000 باشد، تا 2 رقم اعشار نمایش داده شود
        if (price < 10000) {
            return price.toFixed(2);
        }
        
        // در غیر این صورت بدون اعشار نمایش داده شود
        return Math.round(price).toString();
    }
    
    // فراخوانی خودکار برای اولین ارز
    if (currencyButtons.length > 0) {
        currencyButtons[0].click();
    }
});