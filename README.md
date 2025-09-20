# 🚀 SalamMessenger - Real-time Crypto Trading Bot

<div align="center">

![SalamMessenger Logo](static/logo.svg)

**A powerful Persian/Farsi cryptocurrency trading bot with real-time updates and AI-powered analysis**

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/hamidbarzin/salam-messenger)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## ✨ Features

### 🔥 Real-time Features
- **Live Price Updates** - Real-time cryptocurrency price tracking
- **Smart AI Assistant** - Interactive AI-powered trading advice
- **Server-Sent Events** - Vercel-compatible real-time updates
- **Price Alerts** - Customizable price notifications

### 📊 Trading & Analysis
- **Technical Analysis** - Advanced charting and indicators
- **Market Sentiment** - AI-powered market analysis
- **Trading Signals** - Buy/sell recommendations
- **Portfolio Tracking** - Real-time portfolio monitoring

### 🌍 Multi-language Support
- **Persian/Farsi** - Full RTL support
- **English** - Complete translation
- **French** - Localized interface

### 🤖 AI-Powered Features
- **Smart Chat Assistant** - Interactive trading advice
- **Price Predictions** - AI-based price forecasting
- **Market Analysis** - Automated technical analysis
- **Risk Assessment** - Intelligent risk management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for Vercel CLI)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/hamidbarzin/salam-messenger.git
   cd salam-messenger
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Open your browser**
   ```
   http://localhost:8000
   ```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

3. **Add custom domain** (optional)
   - Go to Vercel Dashboard
   - Add your domain in Settings > Domains
   - Configure DNS records

## 📱 Screenshots

<div align="center">

### Dashboard
![Dashboard](attached_assets/Screenshot%202025-04-12%20at%201.39.15%20PM.png)

### Real-time Updates
![Real-time](attached_assets/Screenshot%202025-04-12%20at%201.52.51%20PM.png)

### AI Assistant
![AI Assistant](attached_assets/Screenshot%202025-04-12%20at%201.57.43%20PM.png)

</div>

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **Flask-SocketIO** - Real-time communication
- **SQLAlchemy** - Database ORM
- **Pandas** - Data analysis
- **NumPy** - Numerical computing

### Frontend
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **JavaScript ES6+** - Modern JavaScript
- **Server-Sent Events** - Real-time updates

### AI & Analysis
- **OpenAI API** - AI-powered analysis
- **Technical Analysis** - Trading indicators
- **Market Data APIs** - Real-time prices
- **News Analysis** - Sentiment analysis

### Deployment
- **Vercel** - Serverless deployment
- **PostgreSQL** - Cloud database
- **Redis** - Caching layer

## 📊 Supported Cryptocurrencies

- **Bitcoin (BTC)** - Digital gold
- **Ethereum (ETH)** - Smart contracts platform
- **Solana (SOL)** - High-performance blockchain
- **Ripple (XRP)** - Cross-border payments
- **And many more...**

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# API Keys
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_token
CRYPTO_NEWS_API_KEY=your_news_api_key

# Security
SESSION_SECRET=your_secret_key
FLASK_ENV=production
```

### Customization

- **Languages**: Add new languages in `locales/` directory
- **Cryptocurrencies**: Modify `DEFAULT_CURRENCIES` in `config.py`
- **Themes**: Customize CSS in `static/css/`
- **API Endpoints**: Add new routes in `api_routes.py`

## 📈 API Endpoints

### Real-time Updates
- `GET /api/stream` - Server-Sent Events stream
- `GET /api/price/{symbol}` - Get current price
- `POST /api/ai-advice` - Get AI trading advice

### Trading
- `GET /api/signals` - Get trading signals
- `POST /api/alerts` - Set price alerts
- `GET /api/portfolio` - Portfolio data

### Analysis
- `GET /api/analysis/{symbol}` - Technical analysis
- `GET /api/news` - Crypto news
- `POST /api/chat` - AI chat assistant

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CoinGecko API** - Cryptocurrency price data
- **Binance API** - Trading data
- **OpenAI** - AI-powered analysis
- **Vercel** - Hosting platform
- **Bootstrap** - UI framework

## 📞 Support

- **Documentation**: [Wiki](https://github.com/hamidbarzin/salam-messenger/wiki)
- **Issues**: [GitHub Issues](https://github.com/hamidbarzin/salam-messenger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hamidbarzin/salam-messenger/discussions)
- **Email**: support@salamcrypto.com

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hamidbarzin/salam-messenger&type=Date)](https://star-history.com/#hamidbarzin/salam-messenger&Date)

---

<div align="center">

**Made with ❤️ by [Hamidreza Zebardast](https://github.com/hamidbarzin)**

[Website](https://salamcrypto.com) • [Twitter](https://twitter.com/hamidbarzin) • [LinkedIn](https://linkedin.com/in/hamidbarzin)

</div>