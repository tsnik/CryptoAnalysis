import pandas as pd
from pytrends.request import TrendReq
from datetime import date

from utils import get_gtrend, convert_trend

currencies = ["Bitcoin", "Ethereum", "Bitcoin SV", "Bitcoin Cash", "Tether USDt",
              "Ripple", "Litecoin", "Tezos", "Iota", "Dash", "Ethereum Classic",
              "Monero", "Zcash", "NEO"]
start = date(2019, 1, 1)
end = date(2020, 3, 1)

with pd.ExcelWriter("data\\GoogleTrendsAdj2_d.xlsx") as writer:
    reserve_k = None
    for c in currencies:
        ts = get_gtrend(c, start, end)
        ts, k = convert_trend(ts, c, "Bitcoin", "Monero", reserve_k)
        if c == "Monero":
            reserve_k = k
        #ts = convert_trend(ts, "Monero", "Bitcoin")
        df = pd.DataFrame({"GoogleTrend": ts}, index=ts.index)
        #df = df.round(4)
        df.to_excel(writer, sheet_name=c)





