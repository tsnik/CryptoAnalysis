import pandas as pd

from data_prep_utils import spread_calc, google_trend

for exchange in ["BITFINEX", "Kraken", "Ibit"]:
    df = pd.read_excel('data\\raw\\BTC.xlsx', sheet_name=exchange, index_col=0)
    spread_calc(df, "data\\BTC_" + exchange + ".xlsx")

df = pd.read_excel('data\\raw\\ETH.xlsx', sheet_name="BitFinex", index_col=0)
spread_calc(df, "data\\ETH_BITFINEX.xlsx")

google_trend("data\\raw\\gBitcoin.csv", "data\\GoogleTrends.xlsx")

df = pd.read_csv('data\\raw\\SP500.csv', index_col="Date", parse_dates=True)
spread_calc(df, "data\\SP500.xlsx")
