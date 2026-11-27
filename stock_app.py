#!/usr/bin/env python3
"""
Enhanced Stock Analysis App with Real-Time Features
==================================================

Popular real-time stock analysis with:
- Technical indicators (RSI, MACD, Bollinger Bands, Stochastic, Moving Averages)
- Supervised learning (Linear Regression, Random Forest)
- Unsupervised learning (K-means, PCA)
- Real-time data fetching and auto-refresh
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
import threading
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Use a clean, colorful style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except Exception:
    plt.style.use('ggplot')

COLOR = {
    'price': '#2E86DE',       # blue
    'highlow_fill': '#48C9B0',# teal
    'volume': '#F39C12',      # orange
    'returns': '#27AE60',     # green
    'rsi': '#8E44AD',         # purple
    'macd_pos': '#2ECC71',    # green
    'macd_neg': '#E74C3C',    # red
    'bb_price': '#2C3E50',    # dark
    'bb_band': '#E74C3C',     # red
    'stoch_k': '#2980B9',     # blue
    'stoch_d': '#C0392B',     # red
    'sma20': '#1ABC9C',       # teal
    'sma50': '#E67E22',       # orange
}

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Stock Analysis App")
        self.root.geometry("1400x900")
        
        self.data = None
        self.symbol = None
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        self.refresh_seconds_var = tk.StringVar(value="60")
        self.interval_var = tk.StringVar(value="1d")
        self.refresh_job_id = None
        self.predicted_future = None  # (timestamp, predicted_price)
        
        self.create_gui()
        # Ensure background timers are cancelled on window close to avoid Tk errors
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        except Exception:
            pass
        
    def create_gui(self):
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Data Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Symbol input
        ttk.Label(control_frame, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_var = tk.StringVar(value="AAPL")
        ttk.Entry(control_frame, textvariable=self.symbol_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Period selection
        ttk.Label(control_frame, text="Period:").pack(side=tk.LEFT, padx=(10, 0))
        self.period_var = tk.StringVar(value="1y")
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var,
                                   values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"], width=8, state="readonly")
        period_combo.pack(side=tk.LEFT, padx=5)
        
        # Interval selection
        ttk.Label(control_frame, text="Interval:").pack(side=tk.LEFT, padx=(10, 0))
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var,
                                      values=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"],
                                      width=6, state="readonly")
        interval_combo.pack(side=tk.LEFT, padx=5)
        
        # Fetch button
        self.fetch_btn = ttk.Button(control_frame, text="Fetch Data", command=self.fetch_data)
        self.fetch_btn.pack(side=tk.LEFT, padx=10)
        
        # Auto-refresh controls
        ttk.Checkbutton(control_frame, text="Auto-refresh", variable=self.auto_refresh_enabled,
                        command=self.on_toggle_auto_refresh).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(control_frame, text="every (s):").pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.refresh_seconds_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_charts_tab()
        self.create_technical_tab()
        self.create_supervised_tab()
        self.create_unsupervised_tab()
        self.create_analysis_tab()
        
    def create_charts_tab(self):
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="Charts")
        
        controls = ttk.Frame(charts_frame)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls, text="Chart Type:").pack(side=tk.LEFT)
        self.chart_type = tk.StringVar(value="Candlestick")
        chart_combo = ttk.Combobox(controls, textvariable=self.chart_type,
                                  values=["Candlestick", "Line", "Volume", "Returns"], state="readonly")
        chart_combo.pack(side=tk.LEFT, padx=5)
        chart_combo.bind('<<ComboboxSelected>>', self.update_chart)
        
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_technical_tab(self):
        tech_frame = ttk.Frame(self.notebook)
        self.notebook.add(tech_frame, text="Technical Indicators")
        
        controls = ttk.Frame(tech_frame)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls, text="Indicator:").pack(side=tk.LEFT)
        self.tech_indicator = tk.StringVar(value="RSI")
        tech_combo = ttk.Combobox(controls, textvariable=self.tech_indicator,
                                 values=["RSI", "MACD", "Bollinger Bands", "Stochastic", "Moving Averages"], 
                                 state="readonly")
        tech_combo.pack(side=tk.LEFT, padx=5)
        tech_combo.bind('<<ComboboxSelected>>', self.update_technical_chart)
        
        ttk.Button(controls, text="Show All Indicators", command=self.show_all_indicators).pack(side=tk.LEFT, padx=10)
        
        self.tech_chart_frame = ttk.Frame(tech_frame)
        self.tech_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_supervised_tab(self):
        sup_frame = ttk.Frame(self.notebook)
        self.notebook.add(sup_frame, text="Supervised Learning")
        
        controls = ttk.Frame(sup_frame)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls, text="Model:").pack(side=tk.LEFT)
        self.model_type = tk.StringVar(value="Linear Regression")
        model_combo = ttk.Combobox(controls, textvariable=self.model_type,
                                  values=["Linear Regression", "Random Forest", "All Models"], state="readonly")
        model_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls, text="Horizon (days):").pack(side=tk.LEFT, padx=(10, 0))
        self.horizon_var = tk.StringVar(value="1")
        ttk.Entry(controls, textvariable=self.horizon_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls, text="Train & Predict", command=self.train_supervised).pack(side=tk.LEFT, padx=10)
        ttk.Button(controls, text="Predict Next Price", command=self.predict_next_price).pack(side=tk.LEFT, padx=5)
        
        self.sup_text = tk.Text(sup_frame, wrap=tk.WORD)
        self.sup_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_unsupervised_tab(self):
        unsup_frame = ttk.Frame(self.notebook)
        self.notebook.add(unsup_frame, text="Unsupervised Learning")
        
        controls = ttk.Frame(unsup_frame)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls, text="Method:").pack(side=tk.LEFT)
        self.unsup_method = tk.StringVar(value="K-means Clustering")
        unsup_combo = ttk.Combobox(controls, textvariable=self.unsup_method,
                                  values=["K-means Clustering", "PCA Analysis", "Both"], state="readonly")
        unsup_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls, text="Run Analysis", command=self.run_unsupervised).pack(side=tk.LEFT, padx=10)
        
        self.unsup_text = tk.Text(unsup_frame, wrap=tk.WORD)
        self.unsup_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_analysis_tab(self):
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Market Analysis")
        
        ttk.Button(analysis_frame, text="Run Complete Analysis", command=self.run_complete_analysis).pack(pady=10)
        
        self.analysis_text = tk.Text(analysis_frame, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def _derive_safe_period(self, period: str, interval: str) -> str:
        intraday = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
        if interval in intraday:
            if interval in {"1m", "2m", "5m", "15m", "30m"}:
                return "5d" if period not in {"1d", "5d"} else period
            else:
                return "30d" if period not in {"1d", "5d", "1mo", "3mo"} else period
        return period
        
    def fetch_data(self):
        symbol = self.symbol_var.get().upper()
        period = self.period_var.get()
        interval = self.interval_var.get()
        safe_period = self._derive_safe_period(period, interval)
        
        self.status_var.set(f"Fetching {symbol} ({safe_period}, {interval})...")
        self.fetch_btn.config(state='disabled')
        
        def fetch():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=safe_period, interval=interval)
                
                if data.empty:
                    self.root.after(0, lambda: messagebox.showerror("Error", "No data found"))
                    return
                
                data = self.add_technical_indicators(data)
                self.data = data
                self.symbol = symbol
                
                self.root.after(0, self.update_display)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.fetch_btn.config(state='normal'))
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=fetch, daemon=True).start()
        
    def add_technical_indicators(self, data):
        try:
            # Moving averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            
            # Momentum indicators
            data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
            
            # MACD with fallback
            try:
                data['MACD'] = ta.trend.macd_diff(data['Close'])
            except:
                macd_line = data['EMA_12'] - data['EMA_26']
                signal_line = macd_line.ewm(span=9).mean()
                data['MACD'] = macd_line - signal_line
            
            # Bollinger Bands
            data['BB_upper'] = data['SMA_20'] + (data['Close'].rolling(window=20).std() * 2)
            data['BB_lower'] = data['SMA_20'] - (data['Close'].rolling(window=20).std() * 2)
            
            # Stochastic
            data['Stoch_K'] = ta.momentum.stoch(data['High'], data['Low'], data['Close'])
            data['Stoch_D'] = data['Stoch_K'].rolling(window=3).mean()
            
            # Volume indicators
            data['OBV'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
            
            # Volatility
            data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'])
            
            # Price changes
            data['Returns'] = data['Close'].pct_change()
            data['Volatility'] = data['Returns'].rolling(window=20).std()
            
        except Exception as e:
            print(f"Error adding indicators: {e}")
            
        return data
        
    def on_toggle_auto_refresh(self):
        if self.auto_refresh_enabled.get():
            self.schedule_next_refresh()
        else:
            if self.refresh_job_id is not None:
                try:
                    self.root.after_cancel(self.refresh_job_id)
                except Exception:
                    pass
                self.refresh_job_id = None
            self.status_var.set("Auto-refresh stopped")
        
    def schedule_next_refresh(self):
        try:
            seconds = max(5, int(self.refresh_seconds_var.get()))
        except ValueError:
            seconds = 60
            self.refresh_seconds_var.set(str(seconds))
        
        self.fetch_data()
        self.refresh_job_id = self.root.after(seconds * 1000, self.schedule_next_refresh)
        self.status_var.set(f"Auto-refresh every {seconds}s active")
        # Clear any previously plotted forecast if data refreshes
        self.predicted_future = None
        
    def update_display(self):
        if self.data is not None:
            self.create_chart()
            
    def create_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        if self.data is None:
            return
            
        fig, ax = plt.subplots(figsize=(12, 8), dpi=140)
        
        chart_type = self.chart_type.get()
        
        if chart_type == "Candlestick":
            self._plot_candles(ax, self.data)
            ax.set_title(f'{self.symbol} Stock Price (Candlestick View)')
            
        elif chart_type == "Line":
            ax.plot(self.data.index, self.data['Close'], color=COLOR['price'], linewidth=2, label='Close')
            ax.set_title(f'{self.symbol} Stock Price')
            ax.legend(loc='upper left')
            
        elif chart_type == "Volume":
            ax2 = ax.twinx()
            ax.plot(self.data.index, self.data['Close'], color=COLOR['price'], linewidth=2, label='Close')
            ax2.bar(self.data.index, self.data['Volume'], alpha=0.4, color=COLOR['volume'], label='Volume')
            ax.set_title(f'{self.symbol} Price & Volume')
            ax2.set_ylabel('Volume', color='orange')
            ax.legend(loc='upper left')
            
        elif chart_type == "Returns":
            returns = self.data['Returns'].dropna()
            ax.plot(returns.index, returns, color=COLOR['returns'], linewidth=1.2, label='Returns')
            ax.axhline(y=0, color=COLOR['macd_neg'], linestyle='--', alpha=0.5)
            ax.set_title(f'{self.symbol} Daily Returns')
            ax.set_ylabel('Returns')
            ax.legend(loc='upper left')
            
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.yaxis.labelpad = 14
        ax.grid(True, alpha=0.3)
        # Improve date formatting and reduce x tick label size
        # Datetime-aware x-axis formatting. Fallback to default if index is not datetime-like
        try:
            locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
            fig.autofmt_xdate(rotation=30)
            ax.tick_params(axis='x', labelsize=9)
        except Exception:
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            ax.tick_params(axis='x', labelsize=9)

        # Add extra bottom padding so labels don't get clipped
        fig.subplots_adjust(left=0.16, bottom=0.22, right=0.98)

        # Overlay predicted future point if available
        if self.predicted_future is not None and chart_type in ("Candlestick", "Line", "Returns", "Volume"):
            future_ts, future_price = self.predicted_future
            last_close = float(self.data['Close'].iloc[-1])
            ax.plot([self.data.index[-1], future_ts], [last_close, future_price],
                    color='#8e44ad', linestyle='--', linewidth=1.5, label='Forecast')
            ax.scatter([future_ts], [future_price], color='#8e44ad', s=50, zorder=5, marker='X', label='Predicted')
            ax.legend(loc='upper left')
        # Do not call tight_layout here; custom subplots_adjust maintains label visibility
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _plot_candles(self, ax, df):
        """Plot OHLC candlesticks using rectangles and wicks."""
        data = df[['Open', 'High', 'Low', 'Close']].dropna()
        if data.empty:
            return
        dates = pd.to_datetime(data.index).to_pydatetime()
        x = mdates.date2num(dates)
        o = data['Open'].to_numpy()
        h = data['High'].to_numpy()
        l = data['Low'].to_numpy()
        c = data['Close'].to_numpy()

        # Candle width from spacing
        width = 0.6 * np.median(np.diff(x)) if len(x) > 1 else 0.6

        for xi, oi, hi, li, ci in zip(x, o, h, l, c):
            up = ci >= oi
            color = COLOR['macd_pos'] if up else COLOR['macd_neg']
            ax.vlines(xi, li, hi, color=color, linewidth=1)
            lower = min(oi, ci)
            height = max(abs(ci - oi), 1e-6)
            rect = Rectangle((xi - width/2, lower), width, height, facecolor=color, edgecolor=color, alpha=0.85)
            ax.add_patch(rect)

        ax.xaxis_date()
        ax.set_xlim(x[0] - width, x[-1] + width)

    def update_chart(self, event=None):
        self.create_chart()
        
    def update_technical_chart(self, event=None):
        for widget in self.tech_chart_frame.winfo_children():
            widget.destroy()
            
        if self.data is None:
            return
            
        fig, ax = plt.subplots(figsize=(12, 8), dpi=140)
        
        indicator = self.tech_indicator.get()
        
        if indicator == "RSI":
            ax.plot(self.data.index, self.data['RSI'], color=COLOR['rsi'], linewidth=2, label='RSI')
            ax.axhline(y=70, color=COLOR['macd_neg'], linestyle='--', alpha=0.5, label='Overbought')
            ax.axhline(y=30, color=COLOR['returns'], linestyle='--', alpha=0.5, label='Oversold')
            ax.set_title(f'{self.symbol} RSI (14)')
            ax.set_ylabel('RSI')
            ax.legend()
            
        elif indicator == "MACD":
            macd = self.data['MACD']
            ax.bar(self.data.index, macd.clip(lower=0), color=COLOR['macd_pos'], alpha=0.7, label='MACD +')
            ax.bar(self.data.index, macd.clip(upper=0), color=COLOR['macd_neg'], alpha=0.7, label='MACD -')
            ax.axhline(y=0, color=COLOR['bb_band'], linestyle='--', alpha=0.5)
            ax.set_title(f'{self.symbol} MACD')
            ax.set_ylabel('MACD')
            ax.legend()
            
        elif indicator == "Bollinger Bands":
            ax.plot(self.data.index, self.data['Close'], color=COLOR['bb_price'], linewidth=2, label='Price')
            ax.plot(self.data.index, self.data['BB_upper'], color=COLOR['bb_band'], linestyle='--', alpha=0.8, label='Upper BB')
            ax.plot(self.data.index, self.data['BB_lower'], color=COLOR['bb_band'], linestyle='--', alpha=0.8, label='Lower BB')
            ax.fill_between(self.data.index, self.data['BB_upper'], self.data['BB_lower'], alpha=0.08, color=COLOR['bb_band'])
            ax.set_title(f'{self.symbol} Bollinger Bands')
            ax.legend()
            
        elif indicator == "Stochastic":
            ax.plot(self.data.index, self.data['Stoch_K'], color=COLOR['stoch_k'], linewidth=2, label='%K')
            ax.plot(self.data.index, self.data['Stoch_D'], color=COLOR['stoch_d'], linewidth=2, label='%D')
            ax.axhline(y=80, color=COLOR['macd_neg'], linestyle='--', alpha=0.5)
            ax.axhline(y=20, color=COLOR['returns'], linestyle='--', alpha=0.5)
            ax.set_title(f'{self.symbol} Stochastic Oscillator')
            ax.set_ylabel('Stochastic')
            ax.legend()
            
        elif indicator == "Moving Averages":
            ax.plot(self.data.index, self.data['Close'], color=COLOR['bb_price'], linewidth=2, label='Price')
            ax.plot(self.data.index, self.data['SMA_20'], color=COLOR['sma20'], linewidth=2, label='SMA 20')
            ax.plot(self.data.index, self.data['SMA_50'], color=COLOR['sma50'], linewidth=2, label='SMA 50')
            ax.plot(self.data.index, self.data['EMA_12'], color=COLOR['price'], linewidth=2, label='EMA 12')
            ax.set_title(f'{self.symbol} Moving Averages')
            ax.legend()
            
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        try:
            locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
            fig.autofmt_xdate(rotation=30)
            ax.tick_params(axis='x', labelsize=9)
        except Exception:
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            ax.tick_params(axis='x', labelsize=9)

        # Ensure y-label is visible
        ax.yaxis.labelpad = 14
        fig.subplots_adjust(left=0.16, bottom=0.22, right=0.98)

        canvas = FigureCanvasTkAgg(fig, self.tech_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_close(self):
        # Cancel scheduled refresh to avoid "invalid command name" errors, then close window
        try:
            if self.refresh_job_id is not None:
                self.root.after_cancel(self.refresh_job_id)
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        
    def show_all_indicators(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please fetch data first")
            return
            
        fig, axes = plt.subplots(4, 1, figsize=(12, 12))
        
        # Price and BB
        axes[0].plot(self.data.index, self.data['Close'], 'black', linewidth=2)
        axes[0].plot(self.data.index, self.data['BB_upper'], 'r--', alpha=0.7)
        axes[0].plot(self.data.index, self.data['BB_lower'], 'r--', alpha=0.7)
        axes[0].set_title(f'{self.symbol} Price & Bollinger Bands')
        axes[0].grid(True, alpha=0.3)
        
        # RSI
        axes[1].plot(self.data.index, self.data['RSI'], 'purple', linewidth=2)
        axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.5)
        axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.5)
        axes[1].set_title('RSI (14)')
        axes[1].grid(True, alpha=0.3)
        
        # MACD
        axes[2].plot(self.data.index, self.data['MACD'], 'blue', linewidth=2)
        axes[2].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[2].set_title('MACD')
        axes[2].grid(True, alpha=0.3)
        
        # Volume
        axes[3].bar(self.data.index, self.data['Volume'], alpha=0.7, color='orange')
        axes[3].set_title('Volume')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    def train_supervised(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please fetch data first")
            return
            
        try:
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 
                       'RSI', 'MACD', 'Returns', 'Volatility']
            
            horizon = int(self.horizon_var.get())
            self.data['Target'] = self.data['Close'].shift(-horizon).pct_change(horizon)
            
            clean_data = self.data[features + ['Target']].dropna()
            
            X = clean_data[features]
            y = clean_data['Target']
            
            split = int(0.8 * len(X))
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]
            
            model_type = self.model_type.get()
            results = {}
            
            if model_type in ["Linear Regression", "All Models"]:
                lr = LinearRegression()
                lr.fit(X_train, y_train)
                lr_pred = lr.predict(X_test)
                results['Linear Regression'] = {
                    'predictions': lr_pred,
                    'r2': r2_score(y_test, lr_pred),
                    'mse': mean_squared_error(y_test, lr_pred)
                }
                
            if model_type in ["Random Forest", "All Models"]:
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X_train, y_train)
                rf_pred = rf.predict(X_test)
                results['Random Forest'] = {
                    'predictions': rf_pred,
                    'r2': r2_score(y_test, rf_pred),
                    'mse': mean_squared_error(y_test, rf_pred)
                }
            
            results_text = f"""
Supervised Learning Results for {self.symbol}
============================================

Data: {len(X_train)} training, {len(X_test)} test samples
Horizon: {horizon} days

Model Performance:
"""
            
            for name, result in results.items():
                results_text += f"""
{name}:
• R² Score: {result['r2']:.4f}
• MSE: {result['mse']:.6f}
• Avg Prediction: {np.mean(result['predictions']) * 100:.3f}%
• Actual Avg: {np.mean(y_test) * 100:.3f}%
"""
            
            if "Random Forest" in results:
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X_train, y_train)
                importance = pd.DataFrame({
                    'feature': features,
                    'importance': rf.feature_importances_
                }).sort_values('importance', ascending=False)
                
                results_text += f"\nFeature Importance (Random Forest):\n"
                for _, row in importance.head(5).iterrows():
                    results_text += f"• {row['feature']}: {row['importance']:.4f}\n"
            
            self.sup_text.delete(1.0, tk.END)
            self.sup_text.insert(1.0, results_text)
            
        except Exception as e:
            messagebox.showerror("Training Error", str(e))
            
    def predict_next_price(self):
        """Predict the next closing price using a simple supervised model and plot it."""
        if self.data is None:
            messagebox.showwarning("No Data", "Please fetch data first")
            return
        try:
            # Use last N rows to build a simple supervised regression for next close
            lookback = min(200, len(self.data))
            if lookback < 60:
                messagebox.showwarning("Not Enough Data", "Need at least 60 rows for a stable prediction")
                return
            recent = self.data.iloc[-lookback:].copy()

            # Features similar to train_supervised
            recent['SMA_20'] = recent['Close'].rolling(window=20).mean()
            recent['SMA_50'] = recent['Close'].rolling(window=50).mean()
            recent['RSI'] = ta.momentum.rsi(recent['Close'], window=14)
            # MACD fallback if not present
            if 'MACD' not in recent.columns:
                ema12 = recent['Close'].ewm(span=12).mean()
                ema26 = recent['Close'].ewm(span=26).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9).mean()
                recent['MACD'] = macd_line - signal_line

            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'MACD']
            # Target is next close (level prediction, not return)
            recent['NextClose'] = recent['Close'].shift(-1)
            dataset = recent[features + ['NextClose']].dropna()
            X = dataset[features]
            y = dataset['NextClose']

            # Train simple model on recent data and predict one step ahead from the last row
            model = RandomForestRegressor(n_estimators=200, random_state=42)
            model.fit(X, y)
            last_features = recent[features].iloc[[-1]]
            next_price = float(model.predict(last_features)[0])

            # Estimate future timestamp based on interval
            interval = self.interval_var.get()
            last_ts = self.data.index[-1]
            if interval.endswith('m'):
                minutes = int(interval[:-1])
                future_ts = last_ts + pd.Timedelta(minutes=minutes)
            elif interval in ('60m', '90m', '1h'):
                # Normalize to 1h for plotting consistency
                future_ts = last_ts + pd.Timedelta(hours=1)
            else:
                future_ts = last_ts + pd.Timedelta(days=1)

            self.predicted_future = (future_ts, next_price)
            # Refresh chart to show forecast
            self.create_chart()

            # Also show a quick note in supervised tab if present
            note = f"\nForecast: next {interval} close ≈ ${next_price:.2f} at {future_ts}"
            try:
                self.sup_text.insert(tk.END, note)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))
            
    def run_unsupervised(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please fetch data first")
            return
            
        try:
            method = self.unsup_method.get()
            results_text = f"Unsupervised Learning Analysis for {self.symbol}\n"
            results_text += "=" * 50 + "\n\n"
            
            features = ['Returns', 'Volatility', 'RSI', 'MACD', 'Volume']
            clean_data = self.data[features].dropna()
            
            if method in ["K-means Clustering", "Both"]:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(clean_data)
                
                kmeans = KMeans(n_clusters=3, random_state=42)
                clusters = kmeans.fit_predict(X_scaled)
                
                clean_data['Cluster'] = clusters
                
                results_text += "K-means Clustering Results:\n"
                results_text += "-" * 30 + "\n"
                results_text += f"Cluster sizes: {np.bincount(clusters)}\n\n"
                
                for cluster in range(3):
                    cluster_data = clean_data[clean_data['Cluster'] == cluster]
                    results_text += f"Cluster {cluster}:\n"
                    results_text += f"• Size: {len(cluster_data)} samples\n"
                    results_text += f"• Avg Return: {cluster_data['Returns'].mean() * 100:.3f}%\n"
                    results_text += f"• Avg Volatility: {cluster_data['Volatility'].mean() * 100:.3f}%\n"
                    results_text += f"• Avg RSI: {cluster_data['RSI'].mean():.2f}\n\n"
                    
            if method in ["PCA Analysis", "Both"]:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(clean_data[features])
                
                pca = PCA()
                pca_result = pca.fit_transform(X_scaled)
                
                results_text += "PCA Analysis Results:\n"
                results_text += "-" * 25 + "\n"
                results_text += f"Explained variance ratio:\n"
                for i, var in enumerate(pca.explained_variance_ratio_):
                    results_text += f"• PC{i+1}: {var:.3f} ({var*100:.1f}%)\n"
                
                results_text += f"\nCumulative variance: {np.cumsum(pca.explained_variance_ratio_)}\n"
                
                results_text += f"\nFeature importance in first 2 PCs:\n"
                for i, feature in enumerate(features):
                    results_text += f"• {feature}: PC1={pca.components_[0][i]:.3f}, PC2={pca.components_[1][i]:.3f}\n"
                    
            self.unsup_text.delete(1.0, tk.END)
            self.unsup_text.insert(1.0, results_text)
            
        except Exception as e:
            messagebox.showerror("Unsupervised Analysis Error", str(e))
            
    def run_complete_analysis(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please fetch data first")
            return
            
        try:
            analysis_text = f"""
Complete Market Analysis for {self.symbol}
=========================================

Current Market Data:
• Current Price: ${self.data['Close'].iloc[-1]:.2f}
• 52-Week High: ${self.data['High'].max():.2f}
• 52-Week Low: ${self.data['Low'].min():.2f}
• Average Volume: {self.data['Volume'].mean():,.0f}

Technical Analysis:
• RSI (14): {self.data['RSI'].iloc[-1]:.2f} {'(Overbought)' if self.data['RSI'].iloc[-1] > 70 else '(Oversold)' if self.data['RSI'].iloc[-1] < 30 else '(Neutral)'}
• MACD: {self.data['MACD'].iloc[-1]:.4f}
• Price vs SMA20: {'Above' if self.data['Close'].iloc[-1] > self.data['SMA_20'].iloc[-1] else 'Below'} (${self.data['SMA_20'].iloc[-1]:.2f})
• Price vs SMA50: {'Above' if self.data['Close'].iloc[-1] > self.data['SMA_50'].iloc[-1] else 'Below'} (${self.data['SMA_50'].iloc[-1]:.2f})

Volatility Analysis:
• Current Volatility: {self.data['Volatility'].iloc[-1] * 100:.2f}%
• Average Volatility: {self.data['Volatility'].mean() * 100:.2f}%
• ATR: ${self.data['ATR'].iloc[-1]:.2f}

Volume Analysis:
• Current Volume: {self.data['Volume'].iloc[-1]:,.0f}
• Volume vs Average: {'Above' if self.data['Volume'].iloc[-1] > self.data['Volume'].mean() else 'Below'} average
• OBV Trend: {'Increasing' if self.data['OBV'].iloc[-1] > self.data['OBV'].iloc[-5] else 'Decreasing'}

Risk Metrics:
• Sharpe Ratio: {(self.data['Returns'].mean() / self.data['Returns'].std()) * np.sqrt(252):.3f}
• Max Drawdown: {((self.data['Close'] / self.data['Close'].expanding().max()) - 1).min() * 100:.2f}%
• VaR (95%): {np.percentile(self.data['Returns'].dropna(), 5) * 100:.2f}%

Market Regime:
• Trend: {'Bullish' if self.data['SMA_20'].iloc[-1] > self.data['SMA_50'].iloc[-1] else 'Bearish'}
• Momentum: {'Positive' if self.data['RSI'].iloc[-1] > 50 else 'Negative'}
• Volatility: {'High' if self.data['Volatility'].iloc[-1] > self.data['Volatility'].quantile(0.75) else 'Low' if self.data['Volatility'].iloc[-1] < self.data['Volatility'].quantile(0.25) else 'Normal'}

Support/Resistance Levels:
• Support (SMA50): ${self.data['SMA_50'].iloc[-1]:.2f}
• Resistance (BB Upper): ${self.data['BB_upper'].iloc[-1]:.2f}
• Support (BB Lower): ${self.data['BB_lower'].iloc[-1]:.2f}
            """
            
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, analysis_text)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

def main():
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
