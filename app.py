import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from streamlit_autorefresh import st_autorefresh
from datetime import datetime


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Real-Time Market Analytics",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# AUTO REFRESH - 30 SECONDS
# =========================================================

st_autorefresh(
    interval=30 * 1000,
    key="market_refresh"
)


# =========================================================
# TITLE
# =========================================================

st.title("📊 Real-Time Market Analytics Dashboard")

st.caption(
    "Live cryptocurrency market monitoring using Binance API, "
    "Pandas, Plotly and Technical Analysis"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Dashboard Settings")

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
    "Select Time Interval",
    [
        "1m",
        "5m",
        "15m",
        "1h",
        "4h",
        "1d"
    ]
)

period = st.sidebar.selectbox(
    "Historical Data",
    [
        50,
        100,
        200
    ],
    index=1
)


# =========================================================
# BINANCE API - LIVE MARKET DATA
# =========================================================

ticker_url = (
    f"https://api.binance.com/api/v3/ticker/24hr"
    f"?symbol={symbol}"
)

try:

    ticker_response = requests.get(
        ticker_url,
        timeout=10
    )

    ticker_response.raise_for_status()

    ticker = ticker_response.json()

except Exception as e:

    st.error(f"Unable to fetch live market data: {e}")
    st.stop()


# =========================================================
# EXTRACT LIVE VALUES
# =========================================================

last_price = float(ticker["lastPrice"])

price_change = float(
    ticker["priceChangePercent"]
)

high_price = float(
    ticker["highPrice"]
)

low_price = float(
    ticker["lowPrice"]
)

volume = float(
    ticker["volume"]
)


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📌 Live Market Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Current Price",
        f"${last_price:,.2f}"
    )

with col2:

    st.metric(
        "24H Change",
        f"{price_change:.2f}%"
    )

with col3:

    st.metric(
        "24H High",
        f"${high_price:,.2f}"
    )

with col4:

    st.metric(
        "24H Low",
        f"${low_price:,.2f}"
    )

with col5:

    st.metric(
        "24H Volume",
        f"{volume:,.2f}"
    )


# =========================================================
# HISTORICAL KLINE DATA
# =========================================================

kline_url = (
    f"https://api.binance.com/api/v3/klines"
    f"?symbol={symbol}"
    f"&interval={interval}"
    f"&limit={period}"
)

try:

    kline_response = requests.get(
        kline_url,
        timeout=10
    )

    kline_response.raise_for_status()

    klines = kline_response.json()

except Exception as e:

    st.error(f"Unable to fetch historical data: {e}")
    st.stop()


# =========================================================
# CREATE DATAFRAME
# =========================================================

columns = [
    "Open Time",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Close Time",
    "Quote Asset Volume",
    "Number of Trades",
    "Taker Buy Base Volume",
    "Taker Buy Quote Volume",
    "Ignore"
]

df = pd.DataFrame(
    klines,
    columns=columns
)


# =========================================================
# DATA TYPE CONVERSION
# =========================================================

df["Open"] = pd.to_numeric(
    df["Open"]
)

df["High"] = pd.to_numeric(
    df["High"]
)

df["Low"] = pd.to_numeric(
    df["Low"]
)

df["Close"] = pd.to_numeric(
    df["Close"]
)

df["Volume"] = pd.to_numeric(
    df["Volume"]
)

df["Open Time"] = pd.to_datetime(
    df["Open Time"],
    unit="ms"
)


# =========================================================
# MOVING AVERAGE
# =========================================================

df["MA20"] = (
    df["Close"]
    .rolling(window=20)
    .mean()
)


# =========================================================
# RSI
# =========================================================

rsi_indicator = RSIIndicator(
    close=df["Close"],
    window=14
)

df["RSI"] = rsi_indicator.rsi()


# =========================================================
# PRICE CHANGE
# =========================================================

df["Price Change"] = (
    df["Close"].pct_change() * 100
)


# =========================================================
# VOLATILITY
# =========================================================

volatility = (
    df["Price Change"]
    .std()
)


# =========================================================
# MARKET TREND
# =========================================================

latest_close = df["Close"].iloc[-1]

latest_ma = df["MA20"].iloc[-1]

if pd.isna(latest_ma):

    trend = "Not enough data"

elif latest_close > latest_ma:

    trend = "📈 Bullish"

elif latest_close < latest_ma:

    trend = "📉 Bearish"

else:

    trend = "➡️ Sideways"


# =========================================================
# TECHNICAL ANALYSIS
# =========================================================

st.subheader("📈 Technical Analysis")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Market Trend",
        trend
    )

with col2:

    st.metric(
        "Volatility",
        f"{volatility:.2f}%"
    )

with col3:

    latest_rsi = df["RSI"].iloc[-1]

    st.metric(
        "RSI",
        f"{latest_rsi:.2f}"
    )


# =========================================================
# PRICE CHART
# =========================================================

st.subheader(
    f"📊 {symbol} Price Chart"
)

fig_price = go.Figure()


fig_price.add_trace(
    go.Candlestick(
        x=df["Open Time"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    )
)


fig_price.add_trace(
    go.Scatter(
        x=df["Open Time"],
        y=df["MA20"],
        mode="lines",
        name="MA20"
    )
)


fig_price.update_layout(
    title=f"{symbol} - Price & Moving Average",
    xaxis_title="Time",
    yaxis_title="Price",
    height=550,
    xaxis_rangeslider_visible=False
)


st.plotly_chart(
    fig_price,
    use_container_width=True
)


# =========================================================
# VOLUME CHART
# =========================================================

st.subheader("📦 Trading Volume")

fig_volume = go.Figure()


fig_volume.add_trace(
    go.Bar(
        x=df["Open Time"],
        y=df["Volume"],
        name="Volume"
    )
)


fig_volume.update_layout(
    title=f"{symbol} - Trading Volume",
    xaxis_title="Time",
    yaxis_title="Volume",
    height=350
)


st.plotly_chart(
    fig_volume,
    use_container_width=True
)


# =========================================================
# RSI CHART
# =========================================================

st.subheader("📉 RSI Indicator")

fig_rsi = go.Figure()


fig_rsi.add_trace(
    go.Scatter(
        x=df["Open Time"],
        y=df["RSI"],
        mode="lines",
        name="RSI"
    )
)


fig_rsi.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="Overbought (70)"
)


fig_rsi.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="Oversold (30)"
)


fig_rsi.update_layout(
    title="Relative Strength Index (RSI)",
    xaxis_title="Time",
    yaxis_title="RSI",
    yaxis_range=[0, 100],
    height=350
)


st.plotly_chart(
    fig_rsi,
    use_container_width=True
)


# =========================================================
# RSI INTERPRETATION
# =========================================================

latest_rsi = df["RSI"].iloc[-1]

st.subheader("🧠 RSI Interpretation")

if latest_rsi >= 70:

    st.warning(
        "RSI is above 70 → Market may be Overbought."
    )

elif latest_rsi <= 30:

    st.info(
        "RSI is below 30 → Market may be Oversold."
    )

else:

    st.success(
        "RSI is between 30 and 70 → Market is in a normal range."
    )


# =========================================================
# TOP GAINERS & LOSERS
# =========================================================

st.subheader("🔥 Top Gainers & Losers")

crypto_symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT"
]

market_data = []


for crypto in crypto_symbols:

    try:

        url = (
            f"https://api.binance.com/api/v3/ticker/24hr"
            f"?symbol={crypto}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        market_data.append(
            {
                "Symbol": crypto,
                "Price": float(
                    data["lastPrice"]
                ),
                "Change %": float(
                    data["priceChangePercent"]
                ),
                "Volume": float(
                    data["volume"]
                )
            }
        )

    except Exception:

        pass


market_df = pd.DataFrame(
    market_data
)


if not market_df.empty:

    gainers = (
        market_df
        .sort_values(
            "Change %",
            ascending=False
        )
        .head(5)
    )

    losers = (
        market_df
        .sort_values(
            "Change %",
            ascending=True
        )
        .head(5)
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write("🚀 Top Gainers")

        st.dataframe(
            gainers,
            use_container_width=True,
            hide_index=True
        )

    with col2:

        st.write("🔻 Top Losers")

        st.dataframe(
            losers,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# RAW MARKET DATA
# =========================================================

st.subheader("📋 Detailed Market Data")

display_df = df[
    [
        "Open Time",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA20",
        "RSI",
        "Price Change"
    ]
].copy()


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# CSV DOWNLOAD
# =========================================================

st.subheader("⬇️ Download Data")

csv_data = df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name=f"{symbol}_market_data.csv",
    mime="text/csv"
)


# =========================================================
# LAST UPDATED
# =========================================================

current_time = datetime.now().strftime(
    "%d-%m-%Y %I:%M:%S %p"
)

st.caption(
    f"🕒 Last updated: {current_time}"
)

st.caption(
    "🔄 Dashboard automatically refreshes every 30 seconds."
)

st.caption(
    "⚠️ This dashboard is for educational and analytical purposes only."
)