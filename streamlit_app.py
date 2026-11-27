"""Deployable Streamlit dashboard for stock analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
from stock_models import (
    KMeans,
    LinearRegression,
    PCA,
    RandomForestRegressor,
    StandardScaler,
    mean_squared_error,
    r2_score,
)


st.set_page_config(
    page_title="Northstar — Market intelligence",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --ink: #172b3a; --muted: #718096; --green: #138a72;
        --line: #e8edf0; --surface: #ffffff; --canvas: #f5f7f7;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #102b38; }
    [data-testid="stSidebar"] * { color: #eaf3f3; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b7c9cd; }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #183946; border-color: #31505b; border-radius: 9px;
    }
    [data-testid="stSidebar"] button[kind="primary"] {
        background: #45c6a6; border: 0; color: #102b38; font-weight: 700;
        border-radius: 9px; width: 100%;
    }
    .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; color: var(--ink); }
    .eyebrow { color: var(--green); text-transform: uppercase; letter-spacing: .14em;
        font-size: .72rem; font-weight: 700; margin-bottom: .35rem; }
    .hero-title { font-family: 'Manrope', sans-serif; font-size: clamp(2rem, 3.3vw, 3rem);
        line-height: 1.08; letter-spacing: -.055em; font-weight: 800; color: var(--ink); }
    .hero-copy { color: var(--muted); font-size: 1rem; margin-top: .65rem; }
    .surface { background: var(--surface); border: 1px solid var(--line); border-radius: 16px;
        padding: 1.1rem 1.25rem; }
    .ticker-pill { display: inline-block; background: #e5f5f0; color: #08745f;
        border-radius: 99px; padding: .35rem .7rem; font-size: .75rem; font-weight: 700; }
    [data-testid="stMetric"] { background: white; border: 1px solid var(--line);
        border-radius: 14px; padding: 1rem 1.1rem; }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
    [data-testid="stMetricValue"] { color: var(--ink); font-family: 'Manrope', sans-serif;
        font-weight: 700; font-size: 1.55rem; }
    [data-testid="stTabs"] button { font-weight: 600; }
    [data-testid="stAlert"] { border-radius: 12px; }
    .footer-note { color: #8a969d; font-size: .78rem; border-top: 1px solid var(--line);
        margin-top: 2rem; padding-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


PERIODS = {
    "1 day": "1d",
    "5 days": "5d",
    "1 month": "1mo",
    "3 months": "3mo",
    "6 months": "6mo",
    "1 year": "1y",
    "2 years": "2y",
}
INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d"]


def safe_period(period: str, interval: str) -> str:
    intraday = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
    if interval in intraday:
        if interval in {"1m", "2m", "5m", "15m", "30m"}:
            return period if period in {"1d", "5d"} else "5d"
        return period if period in {"1d", "5d", "1mo", "3mo"} else "30d"
    return period


@st.cache_data(ttl=300, show_spinner=False)
def load_history(symbol: str, period: str, interval: str = "1d") -> pd.DataFrame:
    """Fetch and prepare a ticker's historical data."""
    data = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=True)
    if data.empty:
        raise ValueError(f"No historical data was returned for {symbol}. Check the symbol and try again.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(data.columns):
        raise ValueError("The data provider returned an unexpected set of price columns.")

    data = data.dropna(subset=["Close"]).copy()
    data["Returns"] = data["Close"].pct_change()
    data["SMA 20"] = data["Close"].rolling(20).mean()
    data["SMA 50"] = data["Close"].rolling(50).mean()
    data["EMA 12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA 26"] = data["Close"].ewm(span=26, adjust=False).mean()
    delta = data["Close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    relative_strength = gain / loss.replace(0, np.nan)
    data["RSI"] = 100 - (100 / (1 + relative_strength))
    macd_line = data["EMA 12"] - data["EMA 26"]
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    data["MACD"] = macd_line - macd_signal
    data["MACD signal"] = macd_signal
    rolling_std = data["Close"].rolling(20).std()
    data["BB upper"] = data["SMA 20"] + 2 * rolling_std
    data["BB lower"] = data["SMA 20"] - 2 * rolling_std
    low14 = data["Low"].rolling(14).min()
    high14 = data["High"].rolling(14).max()
    data["Stoch K"] = 100 * (data["Close"] - low14) / (high14 - low14).replace(0, np.nan)
    data["Stoch D"] = data["Stoch K"].rolling(3).mean()
    direction = np.sign(data["Close"].diff()).fillna(0)
    data["OBV"] = (direction * data["Volume"]).cumsum()
    previous_close = data["Close"].shift(1)
    true_range = pd.concat(
        [
            data["High"] - data["Low"],
            (data["High"] - previous_close).abs(),
            (data["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    data["ATR"] = true_range.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    data["Volatility"] = data["Returns"].rolling(20).std()
    return data


def money(value: float, currency: str) -> str:
    """Format a price with the ticker's trading currency."""
    return f"{currency} {value:,.2f}" if currency else f"{value:,.2f}"


def make_price_chart(data: pd.DataFrame, symbol: str, chart_type: str = "Candlestick") -> go.Figure:
    chart = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.76, 0.24],
    )
    if chart_type == "Candlestick":
        chart.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name=symbol,
                increasing_line_color="#159a7c",
                decreasing_line_color="#e27669",
            ),
            row=1,
            col=1,
        )
    elif chart_type == "Returns":
        chart.add_trace(
            go.Scatter(x=data.index, y=data["Returns"] * 100, name="Returns",
                       line={"color": "#159a7c", "width": 1.5}),
            row=1,
            col=1,
        )
        chart.add_hline(y=0, line_dash="dot", line_color="#e27669", row=1, col=1)
    else:
        chart.add_trace(
            go.Scatter(x=data.index, y=data["Close"], name=f"{symbol} close",
                       line={"color": "#159a7c", "width": 2}),
            row=1,
            col=1,
        )
    if chart_type != "Returns":
        chart.add_trace(
            go.Scatter(x=data.index, y=data["SMA 20"], name="20-day average",
                       line={"color": "#e6a14a", "width": 1.5}),
            row=1,
            col=1,
        )
        chart.add_trace(
            go.Scatter(x=data.index, y=data["SMA 50"], name="50-day average",
                       line={"color": "#7489c6", "width": 1.5}),
            row=1,
            col=1,
        )
    chart.add_trace(
        go.Bar(x=data.index, y=data["Volume"], name="Volume",
               marker_color="#b7d8d0", opacity=0.8),
        row=2,
        col=1,
    )
    chart.update_layout(
        height=490,
        margin={"l": 8, "r": 8, "t": 25, "b": 8},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "DM Sans, sans-serif", "color": "#52616b", "size": 11},
        legend={"orientation": "h", "y": 1.04, "x": 0, "bgcolor": "rgba(255,255,255,0)"},
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )
    if chart_type == "Returns":
        chart.update_yaxes(title="Return (%)", row=1, col=1)
    chart.update_xaxes(showgrid=False, linecolor="#edf0f1")
    chart.update_yaxes(showgrid=True, gridcolor="#edf0f1", zeroline=False)
    return chart


def build_forecast(data: pd.DataFrame) -> tuple[float, float]:
    """Fit a time-ordered linear return baseline and estimate the next close."""
    features = pd.DataFrame(index=data.index)
    features["return_1d"] = data["Close"].pct_change()
    features["return_5d"] = data["Close"].pct_change(5)
    features["return_20d"] = data["Close"].pct_change(20)
    features["rsi"] = data["RSI"]
    features["volume_change"] = data["Volume"].pct_change().replace([np.inf, -np.inf], np.nan)
    features["target"] = data["Close"].pct_change().shift(-1)
    training = features.dropna()
    if len(training) < 60:
        raise ValueError("At least 80 daily prices are needed to train a forecast model.")

    split = int(len(training) * 0.8)
    x_train = training.drop(columns="target").iloc[:split]
    y_train = training["target"].iloc[:split]
    x_test = training.drop(columns="target").iloc[split:]
    y_test = training["target"].iloc[split:]
    train_mean = x_train.mean()
    train_scale = x_train.std().replace(0, 1)
    x_train_scaled = (x_train - train_mean) / train_scale
    design = np.column_stack([np.ones(len(x_train_scaled)), x_train_scaled.to_numpy()])
    coefficients, _, _, _ = np.linalg.lstsq(design, y_train.to_numpy(), rcond=None)

    x_test_scaled = (x_test - train_mean) / train_scale
    test_design = np.column_stack([np.ones(len(x_test_scaled)), x_test_scaled.to_numpy()])
    test_prediction = test_design @ coefficients
    current_features = features.drop(columns="target").dropna().iloc[[-1]]
    current_scaled = (current_features - train_mean) / train_scale
    current_design = np.column_stack([np.ones(len(current_scaled)), current_scaled.to_numpy()])
    forecast_return = float((current_design @ coefficients)[0])
    next_close = float(data["Close"].iloc[-1]) * (1 + forecast_return)
    return next_close, float(np.mean(np.abs(y_test.to_numpy() - test_prediction)))


ML_FEATURES = [
    "Open", "High", "Low", "Close", "Volume", "SMA 20", "SMA 50",
    "RSI", "MACD", "Returns", "Volatility",
]
UNSUPERVISED_FEATURES = ["Returns", "Volatility", "RSI", "MACD", "Volume"]


def supervised_frame(data: pd.DataFrame, horizon: int) -> tuple[pd.DataFrame, pd.Series]:
    target = data["Close"].shift(-horizon) / data["Close"] - 1
    dataset = data[ML_FEATURES].copy()
    dataset["target"] = target
    dataset = dataset.replace([np.inf, -np.inf], np.nan).dropna()
    return dataset[ML_FEATURES], dataset["target"]


def evaluate_supervised_models(
    data: pd.DataFrame, model_choice: str, horizon: int
) -> tuple[dict, pd.DataFrame, pd.Series]:
    features, target = supervised_frame(data, horizon)
    if len(features) < 30:
        raise ValueError("Not enough clean observations for model training. Choose a longer history.")

    split = int(len(features) * 0.8)
    if split == 0 or split == len(features):
        raise ValueError("The selected history is too short for a chronological train/test split.")
    x_train, x_test = features.iloc[:split], features.iloc[split:]
    y_train, y_test = target.iloc[:split], target.iloc[split:]
    results = {}

    if model_choice in {"Linear Regression", "All Models"}:
        model = LinearRegression().fit(x_train, y_train)
        prediction = model.predict(x_test)
        results["Linear Regression"] = {
            "actual": y_test,
            "predicted": prediction,
            "r2": r2_score(y_test, prediction),
            "mse": mean_squared_error(y_test, prediction),
        }

    if model_choice in {"Random Forest", "All Models"}:
        model = RandomForestRegressor(n_estimators=100, random_state=42).fit(x_train, y_train)
        prediction = model.predict(x_test)
        results["Random Forest"] = {
            "actual": y_test,
            "predicted": prediction,
            "r2": r2_score(y_test, prediction),
            "mse": mean_squared_error(y_test, prediction),
            "importance": pd.Series(model.feature_importances_, index=features.columns)
            .sort_values(ascending=False),
        }
    return results, x_train, y_train


def predict_next_close(data: pd.DataFrame) -> float:
    features = data[ML_FEATURES].replace([np.inf, -np.inf], np.nan)
    target = data["Close"].shift(-1)
    training = features.copy()
    training["target"] = target
    training = training.dropna()
    current = features.dropna().iloc[[-1]]
    if len(training) < 60 or current.empty:
        raise ValueError("At least 60 usable price rows are needed for a next-price estimate.")
    model = RandomForestRegressor(n_estimators=200, random_state=42).fit(
        training[ML_FEATURES], training["target"]
    )
    return float(model.predict(current)[0])


def make_technical_chart(data: pd.DataFrame, symbol: str, indicator: str) -> go.Figure:
    if indicator == "All Indicators":
        figure = make_subplots(
            rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.045,
            row_heights=[0.38, 0.2, 0.2, 0.22],
            subplot_titles=("Price & Bollinger Bands", "RSI (14)", "MACD", "Volume"),
        )
        figure.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close",
                                    line={"color": "#172b3a", "width": 1.5}), row=1, col=1)
        for column, label, color in [
            ("BB upper", "Upper band", "#d88b81"),
            ("BB lower", "Lower band", "#d88b81"),
        ]:
            figure.add_trace(go.Scatter(x=data.index, y=data[column], name=label,
                                        line={"color": color, "dash": "dot", "width": 1}), row=1, col=1)
        figure.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI",
                                    line={"color": "#7d71c8"}), row=2, col=1)
        figure.add_hline(y=70, line_dash="dot", line_color="#d58e83", row=2, col=1)
        figure.add_hline(y=30, line_dash="dot", line_color="#70b7a3", row=2, col=1)
        figure.add_trace(go.Bar(x=data.index, y=data["MACD"], name="MACD histogram",
                                marker_color="#159a7c"), row=3, col=1)
        figure.add_trace(go.Scatter(x=data.index, y=data["MACD signal"], name="Signal",
                                    line={"color": "#e6a14a"}), row=3, col=1)
        figure.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Volume",
                                marker_color="#b7d8d0"), row=4, col=1)
    else:
        figure = go.Figure()
        if indicator == "RSI":
            figure.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI (14)",
                                        line={"color": "#7d71c8", "width": 2}))
            figure.add_hrect(y0=70, y1=100, fillcolor="#f9e9e7", opacity=0.7, line_width=0)
            figure.add_hrect(y0=0, y1=30, fillcolor="#e8f5f0", opacity=0.7, line_width=0)
            figure.add_hline(y=70, line_dash="dot", line_color="#d58e83")
            figure.add_hline(y=30, line_dash="dot", line_color="#70b7a3")
            figure.update_yaxes(range=[0, 100])
        elif indicator == "MACD":
            figure.add_trace(go.Bar(x=data.index, y=data["MACD"], name="MACD histogram",
                                    marker_color="#159a7c"))
            figure.add_trace(go.Scatter(x=data.index, y=data["MACD signal"], name="Signal",
                                        line={"color": "#e6a14a"}))
            figure.add_hline(y=0, line_dash="dot", line_color="#9aa6aa")
        elif indicator == "Bollinger Bands":
            figure.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close",
                                        line={"color": "#172b3a", "width": 1.7}))
            figure.add_trace(go.Scatter(x=data.index, y=data["BB upper"], name="Upper band",
                                        line={"color": "#d88b81", "dash": "dot"}))
            figure.add_trace(go.Scatter(x=data.index, y=data["BB lower"], name="Lower band",
                                        line={"color": "#d88b81", "dash": "dot"},
                                        fill="tonexty", fillcolor="rgba(216,139,129,.10)"))
        elif indicator == "Stochastic":
            figure.add_trace(go.Scatter(x=data.index, y=data["Stoch K"], name="%K",
                                        line={"color": "#467bb5"}))
            figure.add_trace(go.Scatter(x=data.index, y=data["Stoch D"], name="%D",
                                        line={"color": "#d16d67"}))
            figure.add_hline(y=80, line_dash="dot", line_color="#d58e83")
            figure.add_hline(y=20, line_dash="dot", line_color="#70b7a3")
        else:
            for column, label, color in [
                ("Close", "Close", "#172b3a"),
                ("SMA 20", "SMA 20", "#159a7c"),
                ("SMA 50", "SMA 50", "#e6a14a"),
                ("EMA 12", "EMA 12", "#7d71c8"),
                ("EMA 26", "EMA 26", "#d16d67"),
            ]:
                figure.add_trace(go.Scatter(x=data.index, y=data[column], name=label,
                                            line={"color": color, "width": 1.5}))

    figure.update_layout(
        height=570 if indicator == "All Indicators" else 360,
        margin={"l": 8, "r": 8, "t": 35, "b": 8},
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "DM Sans, sans-serif", "color": "#52616b", "size": 11},
        legend={"orientation": "h", "y": 1.04, "x": 0},
        hovermode="x unified",
    )
    figure.update_xaxes(showgrid=False, linecolor="#edf0f1")
    figure.update_yaxes(showgrid=True, gridcolor="#edf0f1", zeroline=False)
    return figure


def market_analysis(data: pd.DataFrame, currency: str) -> tuple[list, pd.DataFrame]:
    close = data["Close"]
    returns = data["Returns"].dropna()
    latest = data.iloc[-1]
    average_return = returns.mean()
    return_std = returns.std()
    sharpe = average_return / return_std * np.sqrt(252) if return_std else np.nan
    drawdown = close / close.cummax() - 1
    obv_trend = "Increasing" if len(data) >= 5 and latest["OBV"] > data["OBV"].iloc[-5] else "Decreasing"
    readings = [
        ("RSI (14)", f"{latest['RSI']:.2f}", "Overbought" if latest["RSI"] > 70 else "Oversold" if latest["RSI"] < 30 else "Neutral"),
        ("MACD histogram", f"{latest['MACD']:.4f}", "Positive" if latest["MACD"] > 0 else "Negative"),
        ("Price vs SMA 20", "Above" if latest["Close"] > latest["SMA 20"] else "Below", money(latest["SMA 20"], currency)),
        ("Price vs SMA 50", "Above" if latest["Close"] > latest["SMA 50"] else "Below", money(latest["SMA 50"], currency)),
        ("ATR (14)", money(latest["ATR"], currency), "Average true range"),
        ("OBV trend", obv_trend, "Recent five observations"),
        ("Annualized Sharpe ratio", f"{sharpe:.3f}" if np.isfinite(sharpe) else "—", "Historical estimate"),
        ("Maximum drawdown", f"{drawdown.min() * 100:.2f}%", "From period peak"),
        ("Value at Risk (95%)", f"{returns.quantile(.05) * 100:.2f}%", "Historical daily return"),
        ("Trend", "Bullish" if latest["SMA 20"] > latest["SMA 50"] else "Bearish", "SMA 20 vs SMA 50"),
        ("Volatility", f"{latest['Volatility'] * 100:.2f}%", "20-period daily standard deviation"),
    ]
    return readings, pd.DataFrame(
        {
            "Measure": ["Period high", "Period low", "Average volume", "Latest volume"],
            "Value": [
                money(data["High"].max(), currency),
                money(data["Low"].min(), currency),
                f"{data['Volume'].mean():,.0f}",
                f"{latest['Volume']:,.0f}",
            ],
        }
    )


with st.sidebar:
    st.markdown("## ✳ Northstar")
    st.markdown("### Market intelligence")
    st.markdown("---")
    symbol = st.text_input("Ticker symbol", value="AAPL", max_chars=16).strip().upper()
    period_label = st.selectbox("History", list(PERIODS), index=5)
    interval = st.selectbox("Interval", INTERVALS, index=8)
    refresh = st.button("↻  Refresh market data", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("**Popular symbols**")
    st.caption("AAPL · MSFT · NVDA · AMZN · SPY")
    st.markdown("---")
    st.caption("Market data provided by Yahoo Finance. Prices may be delayed.")

if not symbol:
    st.warning("Enter a ticker symbol in the sidebar to get started.")
    st.stop()

if refresh:
    load_history.clear()

try:
    with st.spinner(f"Loading {symbol} market data…"):
        selected_period = PERIODS[period_label]
        effective_period = safe_period(selected_period, interval)
        prices = load_history(symbol, effective_period, interval)
        quote = yf.Ticker(symbol).info
except Exception as error:
    st.error(f"Couldn’t load market data: {error}")
    st.caption("Confirm the ticker is valid and try again in a moment.")
    st.stop()

currency = quote.get("currency", "$") or "$"
company = quote.get("shortName") or quote.get("longName") or symbol
last_price = float(prices["Close"].iloc[-1])
previous_price = float(prices["Close"].iloc[-2]) if len(prices) > 1 else last_price
change = last_price - previous_price
change_pct = (change / previous_price * 100) if previous_price else 0
period_change = (last_price / float(prices["Close"].iloc[0]) - 1) * 100
average_volume = prices["Volume"].tail(20).mean()

st.markdown('<div class="eyebrow">Your market, at a glance</div>', unsafe_allow_html=True)
title_col, tag_col = st.columns([4, 1])
with title_col:
    st.markdown(f'<div class="hero-title">{company}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-copy">{symbol} &nbsp;·&nbsp; {period_label} overview &nbsp;·&nbsp; '
        f'{interval} interval &nbsp;·&nbsp; '
        f'Updated {prices.index[-1].strftime("%b %d, %Y")}</div>',
        unsafe_allow_html=True,
    )
with tag_col:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="ticker-pill">●  MARKET SNAPSHOT</span>', unsafe_allow_html=True)

st.write("")
metric_cols = st.columns(4)
metric_cols[0].metric("Last close", money(last_price, currency), f"{change:+,.2f} ({change_pct:+.2f}%)")
metric_cols[1].metric(f"Period return · {period_label}", f"{period_change:+.2f}%")
metric_cols[2].metric("Relative strength · RSI", f"{prices['RSI'].iloc[-1]:.1f}" if pd.notna(prices["RSI"].iloc[-1]) else "—")
metric_cols[3].metric("Avg. daily volume", f"{average_volume:,.0f}" if pd.notna(average_volume) else "—")

chart_tab, indicators_tab, supervised_tab, unsupervised_tab, analysis_tab = st.tabs(
    ["  Overview  ", "  Technicals  ", "  Supervised learning  ",
     "  Unsupervised learning  ", "  Market analysis  "]
)
with chart_tab:
    chart_type = st.selectbox(
        "Chart type", ["Candlestick", "Line", "Volume", "Returns"], key="overview_chart_type"
    )
    st.markdown("### Price action")
    st.caption(f"{chart_type} chart · {interval} interval · {period_label} selected")
    st.plotly_chart(make_price_chart(prices, symbol, chart_type), use_container_width=True,
                    config={"displayModeBar": False})

with indicators_tab:
    st.markdown("### Technical picture")
    indicator = st.selectbox(
        "Indicator view",
        ["RSI", "MACD", "Bollinger Bands", "Stochastic", "Moving Averages", "All Indicators"],
    )
    left, right = st.columns([1.5, 1])
    with left:
        st.plotly_chart(make_technical_chart(prices, symbol, indicator), use_container_width=True,
                        config={"displayModeBar": False})
    with right:
        latest = prices.iloc[-1]
        st.markdown("#### Indicator readings")
        readings = [
            ("RSI (14)", f"{latest['RSI']:.1f}" if pd.notna(latest["RSI"]) else "Warming up"),
            ("MACD histogram", f"{latest['MACD']:.4f}" if pd.notna(latest["MACD"]) else "—"),
            ("20-day average", money(float(latest["SMA 20"]), currency) if pd.notna(latest["SMA 20"]) else "Warming up"),
            ("50-day average", money(float(latest["SMA 50"]), currency) if pd.notna(latest["SMA 50"]) else "Warming up"),
            ("Bollinger range", f"{money(float(latest['BB lower']), currency)} – {money(float(latest['BB upper']), currency)}"
             if pd.notna(latest["BB lower"]) and pd.notna(latest["BB upper"]) else "Warming up"),
            ("Stochastic %K / %D", f"{latest['Stoch K']:.1f} / {latest['Stoch D']:.1f}"
             if pd.notna(latest["Stoch K"]) and pd.notna(latest["Stoch D"]) else "Warming up"),
            ("ATR (14)", money(float(latest["ATR"]), currency) if pd.notna(latest["ATR"]) else "Warming up"),
            ("OBV", f"{latest['OBV']:,.0f}" if pd.notna(latest["OBV"]) else "—"),
        ]
        for label, value in readings:
            st.markdown(
                f'<div class="surface" style="margin:.45rem 0;padding:.75rem 1rem">'
                f'<span style="color:#718096">{label}</span><br>'
                f'<strong style="color:#172b3a">{value}</strong></div>',
                unsafe_allow_html=True,
            )
with supervised_tab:
    st.markdown("### Supervised learning")
    st.caption("Chronological train/test evaluation with configurable horizon and the original model choices.")
    controls = st.columns([2, 1, 1])
    model_choice = controls[0].selectbox(
        "Model", ["Linear Regression", "Random Forest", "All Models"], key="supervised_model"
    )
    horizon = controls[1].number_input("Horizon (days)", min_value=1, max_value=60, value=1, step=1)
    train_button = controls[2].button("Train & evaluate", type="primary")
    if "web_supervised_results" not in st.session_state:
        st.session_state.web_supervised_results = None
    if "web_next_price" not in st.session_state:
        st.session_state.web_next_price = None

    action_cols = st.columns([1, 3])
    if action_cols[0].button("Predict next price"):
        try:
            with st.spinner("Training the next-price model…"):
                st.session_state.web_next_price = predict_next_close(prices)
        except ValueError as error:
            st.warning(str(error))
        except Exception as error:
            st.error(f"Next-price prediction failed: {error}")

    if train_button:
        try:
            with st.spinner("Training models and scoring the chronological holdout…"):
                st.session_state.web_supervised_results = evaluate_supervised_models(
                    prices, model_choice, int(horizon)
                )[0]
        except ValueError as error:
            st.warning(str(error))
        except Exception as error:
            st.error(f"Model training failed: {error}")

    if st.session_state.web_next_price is not None:
        estimate = st.session_state.web_next_price
        st.metric("Estimated next close", money(estimate, currency),
                  f"{(estimate / last_price - 1) * 100:+.2f}% model estimate")
        st.info("Forecasts are educational estimates, not trading signals or investment advice.")

    if st.session_state.web_supervised_results:
        result_rows = [
            {"Model": name, "R²": result["r2"], "MSE": result["mse"],
             "Average predicted return": f"{np.mean(result['predicted']) * 100:.3f}%",
             "Average actual return": f"{np.mean(result['actual']) * 100:.3f}%"}
            for name, result in st.session_state.web_supervised_results.items()
        ]
        st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)
        prediction_fig = go.Figure()
        for name, result in st.session_state.web_supervised_results.items():
            prediction_fig.add_trace(go.Scatter(
                x=result["actual"].index, y=result["actual"] * 100,
                name=f"{name} · actual", mode="lines",
            ))
            prediction_fig.add_trace(go.Scatter(
                x=result["actual"].index, y=np.asarray(result["predicted"]) * 100,
                name=f"{name} · predicted", mode="lines",
            ))
        prediction_fig.update_layout(
            title=f"Holdout return predictions · {horizon}-day horizon",
            height=350, paper_bgcolor="white", plot_bgcolor="white",
            yaxis_title="Return (%)", hovermode="x unified",
        )
        st.plotly_chart(prediction_fig, use_container_width=True)
        forest_result = st.session_state.web_supervised_results.get("Random Forest")
        if forest_result:
            importance_fig = go.Figure(go.Bar(
                x=forest_result["importance"].values[:8],
                y=forest_result["importance"].index[:8],
                orientation="h", marker_color="#159a7c",
            ))
            importance_fig.update_layout(
                title="Random Forest · top feature importance",
                height=320, paper_bgcolor="white", plot_bgcolor="white",
                yaxis={"autorange": "reversed"},
            )
            st.plotly_chart(importance_fig, use_container_width=True)

with unsupervised_tab:
    st.markdown("### Unsupervised learning")
    method = st.selectbox("Method", ["K-means Clustering", "PCA Analysis", "Both"])
    if "web_unsupervised_results" not in st.session_state:
        st.session_state.web_unsupervised_results = None
    if st.button("Run analysis", type="primary", key="run_unsupervised"):
        try:
            clean = prices[UNSUPERVISED_FEATURES].replace([np.inf, -np.inf], np.nan).dropna()
            if len(clean) < 3:
                raise ValueError("Not enough clean observations. Choose a longer history.")
            scaled = StandardScaler().fit_transform(clean)
            results = {"index": clean.index}
            if method in {"K-means Clustering", "Both"}:
                results["clusters"] = KMeans(n_clusters=3, random_state=42).fit_predict(scaled)
                results["cluster_summary"] = clean.assign(Cluster=results["clusters"]).groupby("Cluster").agg(
                    Samples=("Returns", "size"),
                    Average_Return=("Returns", "mean"),
                    Average_Volatility=("Volatility", "mean"),
                    Average_RSI=("RSI", "mean"),
                ).reset_index()
            if method in {"PCA Analysis", "Both"}:
                pca = PCA()
                results["components"] = pca.fit_transform(scaled)
                results["variance"] = pca.explained_variance_ratio_
                results["loadings"] = pd.DataFrame(
                    pca.components_[:2].T,
                    index=UNSUPERVISED_FEATURES,
                    columns=["PC1", "PC2"],
                )
            st.session_state.web_unsupervised_results = results
        except ValueError as error:
            st.warning(str(error))
        except Exception as error:
            st.error(f"Unsupervised analysis failed: {error}")

    unsupervised_results = st.session_state.web_unsupervised_results
    if unsupervised_results:
        if "cluster_summary" in unsupervised_results:
            summary = unsupervised_results["cluster_summary"].copy()
            summary["Average_Return"] *= 100
            summary["Average_Volatility"] *= 100
            st.markdown("#### K-means cluster profile")
            st.dataframe(summary, use_container_width=True, hide_index=True)
        if "components" in unsupervised_results:
            components = unsupervised_results["components"]
            variance = unsupervised_results["variance"]
            st.markdown("#### PCA variance explained")
            st.dataframe(pd.DataFrame({
                "Component": [f"PC{i + 1}" for i in range(len(variance))],
                "Explained variance": variance,
                "Cumulative variance": np.cumsum(variance),
            }), use_container_width=True, hide_index=True)
            st.markdown("#### First two component loadings")
            st.dataframe(unsupervised_results["loadings"], use_container_width=True)
            scatter = go.Figure(go.Scatter(
                x=components[:, 0], y=components[:, 1], mode="markers",
                marker={
                    "color": unsupervised_results.get(
                        "clusters", np.zeros(len(components), dtype=int)
                    ),
                    "colorscale": "Teal",
                    "showscale": "clusters" in unsupervised_results,
                    "size": 7,
                    "opacity": 0.75,
                },
                text=unsupervised_results["index"].astype(str),
                hovertemplate="%{text}<br>PC1 %{x:.2f}<br>PC2 %{y:.2f}<extra></extra>",
            ))
            scatter.update_layout(
                title="Market regimes · PCA projection",
                xaxis_title="PC1", yaxis_title="PC2", height=400,
                paper_bgcolor="white", plot_bgcolor="white",
            )
            st.plotly_chart(scatter, use_container_width=True)

with analysis_tab:
    st.markdown("### Complete market analysis")
    st.caption("Technical, volatility, volume, risk, and regime readings for the selected history.")
    readings, market_table = market_analysis(prices, currency)
    analysis_cols = st.columns(3)
    analysis_cols[0].metric("52-week high", money(float(prices["High"].tail(252).max()), currency))
    analysis_cols[1].metric("52-week low", money(float(prices["Low"].tail(252).min()), currency))
    analysis_cols[2].metric("Average volume", f"{prices['Volume'].mean():,.0f}")
    st.dataframe(
        pd.DataFrame(readings, columns=["Measure", "Reading", "Context"]),
        use_container_width=True, hide_index=True,
    )
    st.markdown("#### Market data")
    st.dataframe(market_table, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="footer-note">Northstar is for educational purposes only. Historical performance and model estimates '
    'do not guarantee future results. This dashboard is not investment advice.</div>',
    unsafe_allow_html=True,
)
