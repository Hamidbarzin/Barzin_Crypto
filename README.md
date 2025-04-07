# Cryptocurrency Trading Bot

A sophisticated cryptocurrency trading assistant that performs technical analysis and provides real-time market insights, trading signals, and price alerts through Telegram.

## Key Features

- **Real-time Market Analysis**: Monitors cryptocurrency prices and provides timely market overviews
- **Technical Analysis**: Calculates key technical indicators (RSI, MACD, Moving Averages) to identify trading opportunities
- **Trading Signals**: Generates buy/sell signals based on technical analysis
- **Price Alerts**: Notifies about significant price movements and market volatility
- **Automated Reporting**: Sends scheduled reports about market conditions
- **AI-powered Analysis**: Provides intelligent market insights using OpenAI API (optional feature)
- **Telegram Integration**: Delivers all alerts and reports through Telegram for maximum convenience

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token
- Telegram Chat ID
- OpenAI API Key (optional, for AI-powered features)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/crypto-trading-bot.git
cd crypto-trading-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
export TELEGRAM_BOT_TOKEN=your_telegram_bot_token
export DEFAULT_CHAT_ID=your_telegram_chat_id
export OPENAI_API_KEY=your_openai_api_key  # Optional
```

### Usage

#### Quick Start

To start the bot with default settings, run:
```bash
./start_smart_robot.sh
```

To stop the bot:
```bash
./stop_smart_robot.sh
```

#### Manual Commands

- Send test message:
```bash
python simple_ai_mode.py --test
```

- Get market overview:
```bash
python simple_ai_mode.py --overview
```

- Analyze specific coin:
```bash
python simple_ai_mode.py --coin BTC
```

- Get trading opportunities:
```bash
python simple_ai_mode.py --opportunities
```

#### AI-Powered Analysis (requires OpenAI API key)

- Smart market analysis:
```bash
python telegram_smart_reporter.py market
```

- Smart coin analysis:
```bash
python telegram_smart_reporter.py coin BTC
```

## Documentation

For detailed documentation, please refer to:
- [User Guide (English)](./GUIDE.md)
- [User Guide (Persian)](./راهنمای_استفاده.md)
- [Smart Bot Guide (Persian)](./راهنمای_ربات_هوشمند.md)

## Running 24/7

For continuous operation, it's recommended to:
1. Deploy on a dedicated Linux server or VPS
2. Use cloud services like Heroku or Railway
3. Set up cron jobs for periodic execution

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for informational purposes only. Do not make financial decisions based solely on its signals. Always consult with financial professionals before trading.