# 📊 Real-Time Market Analytics Dashboard

A real-time cryptocurrency market analytics dashboard built using Python, Streamlit, Pandas, Plotly and Binance Public API.

The dashboard provides live market monitoring, technical indicators, interactive charts, market movers and downloadable analytical data.

---

## 🚀 Live Demo

🔗 Streamlit Cloud:  
https://real-time-market-analytics.streamlit.app/

---

## 📌 Project Overview

The Real-Time Market Analytics Dashboard collects live cryptocurrency market data from the Binance Public API and processes it using Python and Pandas.

It provides users with an interactive dashboard to monitor:

- Current cryptocurrency price
- 24-hour price change
- 24-hour high and low
- Trading volume
- Price trends
- Moving Average (MA20)
- Relative Strength Index (RSI)
- Market volatility
- Top gainers and losers
- Historical market data
- CSV data export

---

## ✨ Key Features

### 📈 Real-Time Market Monitoring
- Live cryptocurrency prices
- 24-hour percentage change
- 24-hour high and low
- Trading volume
- Automatic refresh every 30 seconds

### 🧠 Technical Analysis
- MA20 Moving Average
- RSI (Relative Strength Index)
- Volatility calculation
- Bullish / Bearish trend detection
- RSI market interpretation

### 📊 Interactive Visualization
- Candlestick price chart
- Moving Average overlay
- Trading volume chart
- RSI indicator chart
- Interactive Plotly charts

### 🔥 Market Movers
- Top cryptocurrency gainers
- Top cryptocurrency losers
- Price and percentage change comparison

### 📥 Data Export
- Detailed historical market data
- CSV download functionality

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Data processing and application logic |
| Pandas | Data analysis and manipulation |
| NumPy | Numerical processing |
| Streamlit | Dashboard development |
| Plotly | Interactive visualization |
| Binance API | Real-time cryptocurrency market data |
| TA-Lib / ta | Technical indicators |
| Git & GitHub | Version control and project hosting |

---

## 🏗️ Project Architecture

```text
Binance Public API
        ↓
   Data Collection
        ↓
      Pandas
        ↓
 Data Processing
        ↓
Technical Indicators
(MA20, RSI, Volatility)
        ↓
     Plotly
        ↓
 Streamlit Dashboard
        ↓
 User Analysis