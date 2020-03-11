from datetime import datetime

from binance.client import Client
import time
import pandas as pd

tickers = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BCHUSDT", "LTCUSDT"]

client = Client()
dfs = {}
for ticker in tickers:
    klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2015", "1 Jan, 2020")
    klines = [{"Open": float(c[1]), "High": float(c[2]), "Low": float(c[3]), "Close": float(c[4]),
               "Volume": float(c[5]), "Trades": int(c[8]), "VolumeQ": float(c[7]),
               "OpenTime": datetime.utcfromtimestamp(c[0]/1000)} for c in klines]
    print(klines)
    dfs[ticker] = pd.DataFrame(klines)

with pd.ExcelWriter('pandas_simple.xlsx') as writer:
    for ticker in tickers:
        dfs[ticker].to_excel(writer, sheet_name=ticker)




