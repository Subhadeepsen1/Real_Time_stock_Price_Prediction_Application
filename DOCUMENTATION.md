## Stock Prediction App — Documentation

This project provides a simple, human-written stock analysis application focused on supervised and unsupervised learning with popular real-time technical indicators.

### What to Run
- Primary app: `python stock_app_enhanced.py`
  - Includes: real-time data fetching, RSI, MACD, Bollinger Bands, Stochastic, Moving Averages, ATR, OBV
  - Supervised: Linear Regression, Random Forest
  - Unsupervised: K-means clustering, PCA

### How to Use (Quick Start)
1. Install deps: `pip install -r requirements.txt`
2. Run the app: `python stock_app_enhanced.py`
3. In the GUI:
   - Choose symbol, period, interval
   - Click “Fetch Data”
   - Use tabs: Charts, Technical Indicators, Supervised Learning, Unsupervised Learning, Market Analysis
   - Enable Auto-refresh to update periodically

### Data Source & Supported Symbols
- Source: Yahoo Finance via `yfinance.Ticker(symbol).history(...)`
- Intervals: `1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d`
- Periods: `1d, 5d, 1mo, 3mo, 6mo, 1y, 2y` (auto-adjusted for intraday)
- Example symbols (US): `AAPL, MSFT, AMZN, GOOGL, NVDA, TSLA, META, JPM, BAC, V, MA`
- Example indices/ETFs: `^GSPC (S&P 500), ^IXIC (Nasdaq), SPY, QQQ`
- Example crypto (if available via Yahoo): `BTC-USD, ETH-USD`
- Note: Some regional tickers need exchange suffixes (e.g., `RELIANCE.NS` for NSE India)

### Real-Time Settings
- Interval: 1m–1d supported
- Intraday safe period is handled automatically (e.g., 1m uses up to 5d)
- Auto-refresh: toggle enabled, set refresh seconds

### Indicators Included
- Momentum: RSI, Stochastic (%K/%D)
- Trend: MACD (with safe fallback), SMA(20/50), EMA(12/26)
- Volatility: Bollinger Bands, ATR
- Volume: OBV
- Returns/Volatility features for ML

### Supervised Learning
- Models: Linear Regression, Random Forest
- Target: future return over configurable horizon (days)
- Metrics: R², MSE; feature importance for Random Forest
 - One-step forecast: use the "Predict Next Price" button to estimate and plot the next closing price

### Unsupervised Learning
- K-means clustering (3 clusters) on standardized features
- PCA with explained variance and top-component loadings

### Minimal File Inventory
- Core (keep):
  - `stock_app_enhanced.py` — single GUI application (recommended entry point)
  - `requirements.txt` — dependencies
  - `README.md` — project overview
  - `DOCUMENTATION.md` — this guide

- Optional (keep if you want modular code examples):
  - `data_preprocessing.py` — indicator engineering utilities
  - `supervised_models.py` — classic supervised models
  - `unsupervised_models.py` — clustering/PCA helpers
  - `visualization.py` — plotting helpers
  - `main.py` — legacy pipeline script (CLI, non-GUI)

- Safe to remove (legacy/duplicates/demo):
  - `run_gui.py`, `stock_analysis_gui.py` — older GUI
  - `stock_analysis_app.py` — CLI app
  - `multi_stock_dashboard.py` — old dashboard
  - `simple_demo.py`, `test_plots.py` — demos/tests
  - `run_app.py`, `check_requirements.py` — legacy helpers
  - `outputs/` (generated images)
  - `PROJECT_SUMMARY.md`, `README_SIMPLE.md`, `README_GUI.md`, `system_status.txt`

### Notes on Symbols
- If you see “possibly delisted; no price data found,” the symbol may be invalid or delisted for the selected exchange. Try a well-known ticker (e.g., AAPL, MSFT, TSLA) or adjust period/interval.

### Troubleshooting
- No window / terminal “stuck”: the GUI is running; interact with the window. Close it to return to the terminal.
- MACD issues: the app includes a safe fallback when `ta.macd_diff` is incompatible.
- Intraday data limits: Yahoo limits history for minute intervals; the app auto-adjusts period.

### Roadmap (kept minimal)
- Optional: add alerts, watchlists, or simple screener without increasing complexity.

### Visualization Quality
- Higher DPI charts for sharper rendering
- Colorful palette for price/volume/indicators
- Better date formatting on the x-axis and legends for clarity


