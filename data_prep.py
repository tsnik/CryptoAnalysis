import pandas as pd

from data_prep_utils import spread_calc, google_trend, coins_number, spread, google_trend_all

dfs = pd.read_excel('data\\raw\\BITFINEX.xlsx', sheet_name=None, index_col=0)
for k in dfs:
    dfs[k] = dfs[k].sort_index()
spread_calc(dfs, "data\\BITFINEX.xlsx")

google_trend_all(dfs, "data\\GoogleTrend.xlsx")

dfs = pd.read_excel('data\\raw\\BitFinexB.xlsx', sheet_name=None, index_col=0)
for k in dfs:
    dfs[k] = dfs[k].sort_index()
spread_calc(dfs, "data\\BITFINEXB.xlsx")
