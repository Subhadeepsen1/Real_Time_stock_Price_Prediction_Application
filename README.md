# Enhanced Stock Analysis Application

Stock analysis with Yahoo Finance data, technical indicators, supervised and unsupervised machine learning, interactive charts, and auto-refresh.

## Desktop application

The Tkinter application remains available locally with its existing analysis tools.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python stock_app_enhanced.py
```

## Deploy the web dashboard

The Streamlit dashboard is the hosted web entry point. It includes configurable price charts, RSI/MACD/Bollinger/Stochastic/Moving Average views, Linear Regression and Random Forest evaluation, next-price prediction, K-means clustering, PCA, and market-risk analysis.

1. Push the repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app from this repository and select the `main` branch after the dashboard changes have been merged there.
3. Set **Main file path** to `streamlit_app.py`.
4. In **Advanced settings**, choose **Python 3.11**. The pinned TensorFlow 2.15 dependency does not support Python 3.14.

The web app needs both `streamlit_app.py` and `stock_models.py`; keep them in the repository root with `requirements.txt`. Yahoo Finance provides the market data and may apply availability or rate limits.

For local web testing:

```powershell
streamlit run streamlit_app.py
```

## Documentation

- [Complete technical documentation](COMPREHENSIVE_DOCUMENTATION.md)
- [Data flow diagram](DATA_FLOW_DIAGRAM.md)
- [Additional usage documentation](DOCUMENTATION.md)
- [Analysis report template](REPORT_TEMPLATE.md)

## Disclaimer

For educational and research purposes only. Model estimates are uncertain and are not investment advice.
