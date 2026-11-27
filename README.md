# Enhanced Stock Analysis Application

A Python stock-analysis application with live market data, technical indicators, supervised and unsupervised machine learning, interactive charts, and configurable auto-refresh.

## Desktop app (original entry point)

The Tkinter application remains the primary app and retains its existing features.

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python stock_app_enhanced.py
```

In the app, enter a ticker, choose a period and interval, then select **Fetch Data**. Use the tabs for charts, technical indicators, supervised learning, unsupervised learning, and market analysis.

`stock_app.py` is also available as the original desktop app copy.

## Optional web dashboard

The browser dashboard is an additional interface; it does not replace the desktop app.

```bash
streamlit run streamlit_app.py
```

To deploy the dashboard on [Streamlit Community Cloud](https://share.streamlit.io/), create an app from this repository, set the main file to `streamlit_app.py`, and choose Python 3.11. The shared `requirements.txt` keeps the desktop dependencies and adds Streamlit so both entry points can be installed from the same project setup.

## Features

- Yahoo Finance price data and configurable intervals
- Candlestick, line, volume, and returns charts
- RSI, MACD, Bollinger Bands, Stochastic, moving averages, ATR, and OBV
- Linear Regression and Random Forest prediction tools
- K-means clustering and PCA market-regime analysis
- Optional one-day forecast in the web dashboard
- Background data fetching and auto-refresh in the desktop app

## Documentation

- [Complete technical documentation](COMPREHENSIVE_DOCUMENTATION.md)
- [Application data flow](DATA_FLOW_DIAGRAM.md)
- [Additional usage documentation](DOCUMENTATION.md)
- [Analysis report template](REPORT_TEMPLATE.md)

## Disclaimer

For educational and research purposes only. Predictions are uncertain and are not investment advice or recommendations.
