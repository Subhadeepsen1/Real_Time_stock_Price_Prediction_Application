# Enhanced Stock Analysis Application

A comprehensive Python-based stock analysis tool that combines real-time data fetching, technical analysis, and machine learning for stock price prediction.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python stock_app_enhanced.py
   ```

3. **Use the application:**
   - Enter a stock symbol (e.g., AAPL, MSFT, TSLA)
   - Select period and interval
   - Click "Fetch Data"
   - Explore different tabs for analysis

## 📊 Features

- **Real-time Data:** Live stock data from Yahoo Finance
- **Technical Analysis:** 10+ popular indicators (RSI, MACD, Bollinger Bands, etc.)
- **Supervised Learning:** Linear Regression and Random Forest for price prediction
- **Unsupervised Learning:** K-means clustering and PCA for market regime analysis
- **Interactive Charts:** Candlestick, line, volume, and returns charts
- **Auto-refresh:** Real-time updates with configurable intervals
- **Future Price Prediction:** One-step-ahead price forecasting

## 📁 Project Structure

```
stock prediction model/
├── stock_app_enhanced.py          # Main application
├── requirements.txt               # Python dependencies
├── COMPREHENSIVE_DOCUMENTATION.md # Complete technical documentation
├── DATA_FLOW_DIAGRAM.md          # Function relationships and data flow
├── REPORT_TEMPLATE.md            # Analysis report template
└── README.md                     # This file
```

## 📚 Documentation

### 📖 [Complete Documentation](COMPREHENSIVE_DOCUMENTATION.md)
Comprehensive guide covering:
- Application overview and architecture
- Function reference and technical details
- Machine learning models and indicators
- Installation, usage, and troubleshooting
- Performance metrics and future enhancements

### 🔄 [Data Flow Diagram](DATA_FLOW_DIAGRAM.md)
Detailed visualization of:
- Main application flow
- Tab-specific function relationships
- Data transformation processes
- Function dependencies and interactions

### 📋 [Report Template](REPORT_TEMPLATE.md)
Professional report framework including:
- Executive summary and market overview
- Technical and ML analysis sections
- Risk assessment and recommendations
- Portfolio considerations and monitoring plans

## 🎯 Supported Symbols

- **US Stocks:** AAPL, MSFT, GOOGL, TSLA, AMZN
- **Indices:** ^GSPC (S&P 500), ^DJI (Dow Jones)
- **Cryptocurrencies:** BTC-USD, ETH-USD
- **International:** Add country suffix (e.g., AAPL.L)
- **ETFs:** SPY, QQQ, VTI

## 🔧 Technical Stack

- **GUI:** Tkinter
- **Data:** Yahoo Finance (yfinance)
- **Analysis:** Pandas, NumPy, TA-Lib
- **ML:** Scikit-learn
- **Visualization:** Matplotlib
- **Concurrency:** Threading

## 📈 Key Capabilities

### Technical Indicators
- Moving Averages (SMA, EMA)
- Momentum (RSI, MACD, Stochastic)
- Volatility (Bollinger Bands, ATR)
- Volume (OBV)

### Machine Learning
- **Supervised:** Price return prediction
- **Unsupervised:** Market regime identification
- **Feature Engineering:** 11+ technical features
- **Model Evaluation:** R², MSE, feature importance

### Real-time Features
- Live data fetching
- Auto-refresh capabilities
- Background processing
- Error handling and recovery

## 🚨 Important Notes

- **Data Source:** Yahoo Finance (free tier)
- **Market Hours:** Real-time during trading hours
- **Gaps:** Normal during non-trading periods
- **Predictions:** For educational purposes only

## 📞 Support

For issues or questions:
1. Check the [Complete Documentation](COMPREHENSIVE_DOCUMENTATION.md)
2. Review the [Data Flow Diagram](DATA_FLOW_DIAGRAM.md)
3. Use the [Report Template](REPORT_TEMPLATE.md) for analysis

## ⚠️ Disclaimer

This application is for educational and research purposes. Stock predictions are not guaranteed and should not be used as investment advice. Always conduct your own research and consult financial professionals before making investment decisions.

---

*Built with Python, focused on supervised and unsupervised learning for stock market analysis.*


