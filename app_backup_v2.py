import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Real-Time Market Analytics",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------

st.title("📊 Real-Time Market Analytics Dashboard")
st.caption("Live cryptocurrency market analysis using Binance API")

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("⚙️ Dashboard Controls")

symbol = st.sidebar.selectbox(
    "Select Cryptocurrency",
    [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "SOLUSDT",
        "XRPUSDT"
    ]
)

interval = st.sidebar.selectbox(
    "Chart Interval",
    [
        "1m",
        "5m",
        "15m",
        "1h",
        "4h",
        "1d"
    ]
)

# -----------------------------
# 24 Hour Market Data
# -----------------------------

ticker_url = "https://api.binance.com/api/v3/ticker/24hr"

ticker_response = requests.get(
    ticker_url,
    params={"symbol": symbol},
    timeout=10
)

ticker_data = ticker_response.json()

price = float(ticker_data["lastPrice"])
change = float(ticker_data["priceChangePercent"])
high = float(ticker_data["highPrice"])
low = float(ticker_data["lowPrice"])
volume = float(ticker_data["volume"])

# -----------------------------
# KPI Cards
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Current Price",
    f"${price:,.2f}"
)

col2.metric(
    "📈 24H Change",
    f"{change:.2f}%"
)

col3.metric(
    "🔺 24H High",
    f"${high:,.2f}"
)

col4.metric(
    "🔻 24H Low",
    f"${low:,.2f}"
)

st.divider()

# -----------------------------
# Historical Market Data
# -----------------------------

klines_url = "https://api.binance.com/api/v3/klines"

params = {
    "symbol": symbol,
    "interval": interval,
    "limit": 100
}

response = requests.get(
    klines_url,
    params=params,
    timeout=10
)

data = response.json()

# -----------------------------
# Create DataFrame
# -----------------------------

columns = [
    "Open Time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close Time",
    "Quote Volume",
    "Trades",
    "Buy Base Volume",
    "Buy Quote Volume",
    "Ignore"
]

df = pd.DataFrame(data, columns=columns)

df["Open"] = df["Open"].astype(float)
df["High"] = df["High"].astype(float)
df["Low"] = df["Low"].astype(float)
df["Close"] = df["Close"].astype(float)
df["Volume"] = df["Volume"].astype(float)

df["Open Time"] = pd.to_datetime(
    df["Open Time"],
    unit="ms"
)

# -----------------------------
# Moving Average
# -----------------------------

df["MA_20"] = df["Close"].rolling(20).mean()

# -----------------------------
# Price Chart
# -----------------------------

st.subheader("📈 Price Analysis")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["Open Time"],
        y=df["Close"],
        mode="lines",
        name="Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["Open Time"],
        y=df["MA_20"],
        mode="lines",
        name="20 Period Moving Average"
    )
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# Volume Chart
# -----------------------------

st.subheader("📊 Trading Volume")

volume_fig = go.Figure()

volume_fig.add_trace(
    go.Bar(
        x=df["Open Time"],
        y=df["Volume"],
        name="Volume"
    )
)

volume_fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Volume",
    height=400
)

st.plotly_chart(
    volume_fig,
    use_container_width=True
)

# -----------------------------
# Market Analysis
# -----------------------------

st.subheader("🔎 Market Analysis")

latest_ma = df["MA_20"].iloc[-1]

analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

analysis_col1.metric(
    "20 Period Moving Average",
    f"${latest_ma:,.2f}"
)

volatility = df["Close"].pct_change().std() * 100

analysis_col2.metric(
    "Price Volatility",
    f"{volatility:.2f}%"
)

analysis_col3.metric(
    "24H Volume",
    f"{volume:,.2f}"
)

# -----------------------------
# Trend Detection
# -----------------------------

st.subheader("📌 Market Trend")

if price > latest_ma:

    st.success(
        f"🟢 {symbol} is currently above its 20-period moving average — bullish trend."
    )

else:

    st.error(
        f"🔴 {symbol} is currently below its 20-period moving average — bearish trend."
    )

# -----------------------------
# Data Preview
# -----------------------------

with st.expander("🔍 View Market Data"):

    st.dataframe(
        df[
            [
                "Open Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "MA_20"
            ]
        ],
        use_container_width=True
    )

st.divider()

st.caption(
    "Data Source: Binance Public Market API | "
    "Built with Python, Pandas, Plotly and Streamlit"
)