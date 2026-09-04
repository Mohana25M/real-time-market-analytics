import requests

url = "https://api.binance.com/api/v3/ticker/24hr"

params = {
    "symbol": "BTCUSDT"
}

response = requests.get(url, params=params)

data = response.json()

print(data)