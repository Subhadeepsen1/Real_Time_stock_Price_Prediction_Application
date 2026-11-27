# Data Flow Diagram - Enhanced Stock Analysis Application

## Overview
This diagram illustrates the complete data flow and function relationships within the stock prediction application.

## Main Application Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              StockApp Class                                  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │   __init__()    │───▶│  create_gui()   │───▶│  GUI Components Setup   │  │
│  │                 │    │                 │    │                         │  │
│  └─────────────────┘    └─────────────────┘    │  • Control Panel        │  │
│                                                │  • Tabbed Interface     │  │
│                                                │  • Status Indicators    │  │
│                                                │  • Auto-refresh Controls│  │
│                                                └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Control Panel                             │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Symbol Input│  │ Period Combo│  │Interval Combo│  │   Fetch Data Button │ │
│  │             │  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ Auto-refresh Toggle │  │ Refresh Interval    │  │   Status Display    │ │
│  │                     │  │                     │  │                     │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              fetch_data()                                   │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ _derive_safe_   │───▶│  Background     │───▶│  yfinance.Ticker()      │  │
│  │ period()        │    │  Thread         │    │                         │  │
│  │                 │    │                 │    │  • history() method     │  │
│  └─────────────────┘    └─────────────────┘    │  • period & interval    │  │
│                                                │  • OHLCV data           │  │
│                                                └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        add_technical_indicators()                          │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Moving Averages │    │  Momentum       │    │  Volatility Indicators  │  │
│  │                 │    │  Indicators     │    │                         │  │
│  │ • SMA_20        │    │ • RSI (14)      │    │ • Bollinger Bands       │  │
│  │ • SMA_50        │    │ • MACD          │    │ • ATR                   │  │
│  │ • EMA_12        │    │ • Stochastic    │    │ • Volatility            │  │
│  │ • EMA_26        │    │   (%K, %D)      │    │   (rolling std)         │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Volume          │    │  Price-Based    │    │  Returns & Changes      │  │
│  │ Indicators      │    │  Indicators     │    │                         │  │
│  │                 │    │                 │    │ • Returns (pct_change)  │  │
│  │ • OBV           │    │ • High/Low      │    │ • Price changes         │  │
│  │ • Volume        │    │ • Open/Close    │    │ • Target variables      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              update_display()                               │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ create_chart()  │───▶│  Chart Types    │───▶│  Visualization          │  │
│  │                 │    │                 │    │                         │  │
│  └─────────────────┘    │ • Candlestick   │    │ • Matplotlib Figures    │  │
│                         │ • Line          │    │ • FigureCanvasTkAgg     │  │
│                         │ • Volume        │    │ • High DPI (140)        │  │
│                         │ • Returns       │    │ • Color Themes          │  │
│                         └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tab-Specific Function Flows

### 1. Charts Tab Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Charts Tab                                     │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Chart Type      │───▶│  create_chart() │───▶│  _plot_candles()        │  │
│  │ Selection       │    │                 │    │                         │  │
│  │                 │    │                 │    │ • OHLC Data Processing  │  │
│  └─────────────────┘    └─────────────────┘    │ • Candle Drawing        │  │
│                                                │ • Color Logic           │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ update_chart()  │───▶│  Chart          │───▶│  Future Price           │  │
│  │                 │    │  Refresh        │    │  Prediction Overlay     │  │
│  └─────────────────┘    └─────────────────┘    │                         │  │
│                                                │ • Predicted Point       │  │
│                                                │ • Forecast Line         │  │
│                                                │ • X Marker              │  │
│                                                └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Technical Indicators Tab Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Technical Indicators Tab                             │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Indicator       │───▶│ update_technical│───▶│  RSI Chart              │  │
│  │ Selection       │    │ _chart()        │    │                         │  │
│  │                 │    │                 │    │ • RSI Line (14-period)  │  │
│  └─────────────────┘    └─────────────────┘    │ • Overbought (70)       │  │
│                                                │ • Oversold (30)         │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ show_all_       │───▶│  Multi-Plot     │───▶│  Comprehensive          │  │
│  │ indicators()    │    │  Generation     │    │  Indicator View         │  │
│  │                 │    │                 │    │                         │  │
│  └─────────────────┘    └─────────────────┘    │ • Price + BB            │  │
│                                                │ • RSI                   │  │
│                                                │ • MACD                  │  │
│                                                │ • Volume                │  │
│                                                └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Supervised Learning Tab Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Supervised Learning Tab                           │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Model Selection │───▶│ train_supervised│───▶│  Feature Engineering    │  │
│  │                 │    │ ()              │    │                         │  │
│  │ • Linear        │    │                 │    │ • OHLCV + Indicators    │  │
│  │   Regression    │    │                 │    │ • Target Creation       │  │
│  │ • Random Forest │    │                 │    │ • Data Cleaning         │  │
│  │ • All Models    │    │                 │    │ • Train/Test Split      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ predict_next_   │───▶│  Future Price   │───▶│  Model Training         │  │
│  │ price()         │    │  Prediction     │    │                         │  │
│  │                 │    │                 │    │ • Random Forest         │  │
│  └─────────────────┘    │                 │    │ • Recent Data Focus     │  │
│                         │                 │    │ • One-step-ahead        │  │
│                         │                 │    │ • Level Prediction      │  │
│                         │                 │    └─────────────────────────┘  │
│                         └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Unsupervised Learning Tab Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Unsupervised Learning Tab                          │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Method          │───▶│ run_unsupervised│───▶│  K-means Clustering     │  │
│  │ Selection       │    │ ()              │    │                         │  │
│  │                 │    │                 │    │ • 3 Clusters            │  │
│  │ • K-means       │    │                 │    │ • Market Regimes        │  │
│  │ • PCA           │    │                 │    │ • Feature Scaling       │  │
│  │ • Both          │    │                 │    │ • Cluster Analysis      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Feature         │───▶│  PCA Analysis   │───▶│  Dimensionality         │  │
│  │ Selection       │    │                 │    │  Reduction              │  │
│  │                 │    │                 │    │                         │  │
│  │ • Returns       │    │                 │    │ • Explained Variance    │  │
│  │ • Volatility    │    │                 │    │ • Component Analysis    │  │
│  │ • RSI           │    │                 │    │ • Feature Importance    │  │
│  │ • MACD          │    │                 │    │ • Cumulative Variance   │  │
│  │ • Volume        │    │                 │    └─────────────────────────┘  │
│  └─────────────────┘    └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5. Market Analysis Tab Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Market Analysis Tab                             │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Run Complete    │───▶│ run_complete_   │───▶│  Current Market Data    │  │
│  │ Analysis        │    │ analysis()      │    │                         │  │
│  │ Button          │    │                 │    │ • Current Price         │  │
│  │                 │    │                 │    │ • 52-Week High/Low      │  │
│  └─────────────────┘    └─────────────────┘    │ • Average Volume        │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Technical       │───▶│  Risk Metrics   │───▶│  Market Regime          │  │
│  │ Analysis        │    │                 │    │  Analysis               │  │
│  │                 │    │                 │    │                         │  │
│  │ • RSI Status    │    │ • Sharpe Ratio  │    │ • Trend (Bullish/Bearish)│  │
│  │ • MACD Value    │    │ • Max Drawdown  │    │ • Momentum (Positive/   │  │
│  │ • SMA Comparison│    │ • VaR (95%)     │    │   Negative)             │  │
│  │ • Volatility    │    │ • Support/      │    │ • Volatility (High/     │  │
│  │   Analysis      │    │   Resistance    │    │   Low/Normal)           │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Auto-Refresh Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Auto-Refresh System                            │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ on_toggle_auto_ │───▶│ schedule_next_  │───▶│  Background Thread      │  │
│  │ refresh()       │    │ refresh()       │    │                         │  │
│  │                 │    │                 │    │ • fetch_data()          │  │
│  └─────────────────┘    └─────────────────┘    │ • update_display()      │  │
│                                                │ • Clear predictions     │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ root.after()    │───▶│  Timer          │───▶│  Scheduled Refresh      │  │
│  │                 │    │  Management     │    │                         │  │
│  │ • Job ID        │    │                 │    │ • Configurable Interval │  │
│  │ • Cancellation  │    │                 │    │ • Minimum 5 seconds     │  │
│  │ • Cleanup       │    │                 │    │ • Status Updates        │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Error Handling                                 │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ try-except      │───▶│  Error          │───▶│  User-Friendly          │  │
│  │ Blocks          │    │  Detection      │    │  Messages               │  │
│  │                 │    │                 │    │                         │  │
│  └─────────────────┘    └─────────────────┘    │ • messagebox.showerror()│  │
│                                                │ • Graceful Degradation  │  │
│                                                │ • Status Updates        │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ on_close()      │───▶│  Clean          │───▶│  Resource Cleanup       │  │
│  │                 │    │  Shutdown       │    │                         │  │
│  │ • Cancel Jobs   │    │                 │    │ • Cancel after() jobs   │  │
│  │ • Destroy Window│    │                 │    │ • Close Threads         │  │
│  │ • Exception     │    │                 │    │ • Free Memory           │  │
│  │   Handling      │    │                 │    │ • Prevent Tkinter       │  │
│  │                 │    │                 │    │   Errors                │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Transformation Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Transformation                            │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Raw OHLCV       │───▶│  Technical      │───▶│  Feature Matrix         │  │
│  │ Data            │    │  Indicators     │    │                         │  │
│  │                 │    │                 │    │ • 11 Features           │  │
│  │ • Open          │    │ • 10+ Indicators│    │ • Cleaned Data          │  │
│  │ • High          │    │ • Rolling       │    │ • No Missing Values     │  │
│  │ • Low           │    │   Calculations  │    │ • Scaled Features       │  │
│  │ • Close         │    │ • Statistical   │    │ • Target Variables      │  │
│  │ • Volume        │    │   Measures      │    │ • Train/Test Split      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Feature         │───▶│  Model          │───▶│  Predictions            │  │
│  │ Engineering     │    │  Training       │    │                         │  │
│  │                 │    │                 │    │ • Future Returns        │  │
│  │ • Target        │    │ • Linear        │    │ • Next Price            │  │
│  │   Creation      │    │   Regression    │    │ • Confidence            │  │
│  │ • Data          │    │ • Random Forest │    │ • Feature Importance    │  │
│  │   Cleaning      │    │ • Cross-        │    │ • Model Metrics         │  │
│  │ • Scaling       │    │   Validation    │    │ • Performance           │  │
│  │ • Validation    │    │ • Hyperparameter│    │   Evaluation            │  │
│  │                 │    │   Tuning        │    │                         │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Function Dependencies

### Core Dependencies
- `__init__()` → `create_gui()` → All tab creation functions
- `fetch_data()` → `add_technical_indicators()` → `update_display()`
- `update_display()` → `create_chart()` → `_plot_candles()`
- `train_supervised()` → Feature engineering → Model training → Results display
- `predict_next_price()` → Model training → Future prediction → Chart overlay
- `run_unsupervised()` → Data preprocessing → Clustering/PCA → Results display
- `run_complete_analysis()` → Data aggregation → Analysis → Report generation

### Utility Dependencies
- `_derive_safe_period()` → Used by `fetch_data()`
- `on_toggle_auto_refresh()` → `schedule_next_refresh()` → `fetch_data()`
- `on_close()` → Cleanup all scheduled jobs and threads

### Event Dependencies
- Chart type selection → `update_chart()` → `create_chart()`
- Indicator selection → `update_technical_chart()`
- Model selection → `train_supervised()`
- Method selection → `run_unsupervised()`
- Auto-refresh toggle → `on_toggle_auto_refresh()`

This data flow diagram provides a comprehensive view of how data moves through the application and how different functions interact with each other to provide the complete stock analysis experience.
