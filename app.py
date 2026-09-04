import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from streamlit_autorefresh import st_autorefresh
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Real-Time Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 16px;
        opacity: 0.7;
        margin-bottom: 25px;
    }

    .status-box {
        padding: 10px 16px;
        border-radius: 10px;
        border: 1px solid #2d333b;
        background: #161b22;
        display: inline-block;
        font-size: 14px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #2d333b;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 25px;
        font-weight: 700;
    }

    .info-card {
        background: #161b22;
        border: 1px solid #2d333b;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .footer {
        text-align: center;
        opacity: 0.55;
        font-size: 13px;
        margin-top: 35px;
        padding: 20px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=30 * 1000,
    key="market_refresh"
)


# =========================================================
# BINANCE API
# =========================================================

BASE_URL = "https://data-api.binance.vision"


def get_api_data(endpoint, params=None):

    url = BASE_URL + endpoint

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="dashboard-title">📊 Real-Time Market Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Live cryptocurrency market monitoring and technical analysis '
    'using Binance public market data.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="status-box">🟢 Live Market Data • Auto Refresh: 30 Seconds</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Dashboard Settings")

st.sidebar.markdown("---")

symbol = st.sidebar.selectbox(
    "🪙 Cryptocurrency",
    [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "SOLUSDT",
        "XRPUSDT"
    ]
)

interval = st.sidebar.selectbox(
    "⏱️ Time Interval",
    [
        "1m",
        "5m",
        "15m",
        "1h",
        "4h",
        "1d"
    ],
    index=2
)

period = st.sidebar.selectbox(
    "📅 Historical Data",
    [50, 100, 200],
    index=1
)

st.sidebar.markdown("---")

st.sidebar.info(
    "This dashboard uses public Binance market data "
    "for educational and analytical purposes."
)


# =========================================================
# LIVE TICKER
# =========================================================

try:

    ticker = get_api_data(
        "/api/v3/ticker/24hr",
        {"symbol": symbol}
    )

except Exception as e:

    st.error(f"Unable to fetch live market data: {e}")
    st.stop()


last_price = float(ticker["lastPrice"])
price_change = float(ticker["priceChangePercent"])
high_price = float(ticker["highPrice"])
low_price = float(ticker["lowPrice"])
volume = float(ticker["volume"])


# =========================================================
# MARKET OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">📌 Live Market Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 Current Price",
        f"${last_price:,.2f}"
    )

with col2:
    st.metric(
        "📈 24H Change",
        f"{price_change:.2f}%"
    )

with col3:
    st.metric(
        "⬆️ 24H High",
        f"${high_price:,.2f}"
    )

with col4:
    st.metric(
        "⬇️ 24H Low",
        f"${low_price:,.2f}"
    )

with col5:
    st.metric(
        "📦 24H Volume",
        f"{volume:,.2f}"
    )


# =========================================================
# HISTORICAL DATA
# =========================================================

try:

    klines = get_api_data(
        "/api/v3/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": period
        }
    )

except Exception as e:

    st.error(f"Unable to fetch historical data: {e}")
    st.stop()


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
# DATA PROCESSING
# =========================================================

numeric_columns = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df["Open Time"] = pd.to_datetime(
    df["Open Time"],
    unit="ms"
)


# =========================================================
# TECHNICAL INDICATORS
# =========================================================

df["MA20"] = (
    df["Close"]
    .rolling(window=20)
    .mean()
)

rsi_indicator = RSIIndicator(
    close=df["Close"],
    window=14
)

df["RSI"] = rsi_indicator.rsi()

df["Price Change"] = (
    df["Close"]
    .pct_change()
    * 100
)

volatility = df["Price Change"].std()

latest_close = df["Close"].iloc[-1]
latest_ma = df["MA20"].iloc[-1]
latest_rsi = df["RSI"].iloc[-1]


# =========================================================
# MARKET TREND
# =========================================================

if pd.isna(latest_ma):

    trend = "⏳ Calculating"

elif latest_close > latest_ma:

    trend = "📈 Bullish"

elif latest_close < latest_ma:

    trend = "📉 Bearish"

else:

    trend = "➡️ Sideways"


# =========================================================
# TECHNICAL ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">🧠 Technical Analysis</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "📊 Market Trend",
        trend
    )

with col2:

    st.metric(
        "🌪️ Volatility",
        f"{volatility:.2f}%"
    )

with col3:

    st.metric(
        "📉 RSI (14)",
        f"{latest_rsi:.2f}"
    )


# =========================================================
# PRICE CHART
# =========================================================

st.markdown(
    '<div class="section-title">📈 Price Analysis</div>',
    unsafe_allow_html=True
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
    title=f"{symbol} • Price & MA20",
    height=550,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    hovermode="x unified"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)


# =========================================================
# VOLUME + RSI
# =========================================================

col1, col2 = st.columns(2)


# ---------------- VOLUME ----------------

with col1:

    st.markdown(
        '<div class="section-title">📦 Trading Volume</div>',
        unsafe_allow_html=True
    )

    fig_volume = go.Figure()

    fig_volume.add_trace(
        go.Bar(
            x=df["Open Time"],
            y=df["Volume"],
            name="Volume"
        )
    )

    fig_volume.update_layout(
        title=f"{symbol} • Trading Volume",
        height=380,
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True
    )


# ---------------- RSI ----------------

with col2:

    st.markdown(
        '<div class="section-title">📉 RSI Indicator</div>',
        unsafe_allow_html=True
    )

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
        annotation_text="Overbought"
    )

    fig_rsi.add_hline(
        y=30,
        line_dash="dash",
        annotation_text="Oversold"
    )

    fig_rsi.update_layout(
        title="Relative Strength Index",
        height=380,
        template="plotly_dark",
        yaxis_range=[0, 100],
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_rsi,
        use_container_width=True
    )


# =========================================================
# RSI INTERPRETATION
# =========================================================

st.markdown(
    '<div class="section-title">🧠 Market Interpretation</div>',
    unsafe_allow_html=True
)

if latest_rsi >= 70:

    st.warning(
        "⚠️ RSI is above 70 — the market may be overbought."
    )

elif latest_rsi <= 30:

    st.info(
        "ℹ️ RSI is below 30 — the market may be oversold."
    )

else:

    st.success(
        "✅ RSI is between 30 and 70 — the market is within a normal range."
    )


# =========================================================
# TOP GAINERS & LOSERS
# =========================================================

st.markdown(
    '<div class="section-title">🔥 Market Movers</div>',
    unsafe_allow_html=True
)

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

        data = get_api_data(
            "/api/v3/ticker/24hr",
            {"symbol": crypto}
        )

        market_data.append(
            {
                "Symbol": crypto,
                "Price": float(data["lastPrice"]),
                "Change %": float(data["priceChangePercent"]),
                "Volume": float(data["volume"])
            }
        )

    except Exception:
        continue


market_df = pd.DataFrame(market_data)


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

        st.markdown("### 🚀 Top Gainers")

        st.dataframe(
            gainers,
            use_container_width=True,
            hide_index=True
        )

    with col2:

        st.markdown("### 🔻 Top Losers")

        st.dataframe(
            losers,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# DETAILED DATA
# =========================================================

st.markdown(
    '<div class="section-title">📋 Detailed Market Data</div>',
    unsafe_allow_html=True
)

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
# DOWNLOAD
# =========================================================

st.markdown(
    '<div class="section-title">⬇️ Export Data</div>',
    unsafe_allow_html=True
)

csv_data = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Market Data CSV",
    data=csv_data,
    file_name=f"{symbol}_market_data.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

current_time = datetime.now().strftime(
    "%d-%m-%Y %I:%M:%S %p"
)

st.markdown(
    f"""
    <div class="footer">
        🕒 Last Updated: {current_time}<br>
        🔄 Automatically refreshes every 30 seconds<br>
        ⚠️ Educational and analytical purposes only<br><br>
        <b>Real-Time Market Analytics Dashboard</b> •
        Developed by M. Mohana • AI & Data Science
    </div>
    """,
    unsafe_allow_html=True
)