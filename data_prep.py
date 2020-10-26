import pandas as pd

from data_prep_utils import spread_calc, google_trend, coins_number, spread, google_trend_all, google_trend_all_separate

# dfs = pd.read_excel('data\\raw\\BITFINEX.xlsx', sheet_name=None, index_col=0)
# for k in dfs:
#     dfs[k] = dfs[k].sort_index()
# spread_calc(dfs, "data\\BITFINEX.xlsx")

# google_trend_all(dfs, "data\\GoogleTrend.xlsx")
#google_trend_all_separate(dfs, "data\\GoogleTrend_Sep.xlsx")

dfs = pd.read_excel('data\\raw\\BitFinexB.xlsx', sheet_name=None, index_col=0)
for k in dfs:
    dfs[k] = dfs[k].sort_index()
spread_calc(dfs, "data\\BITFINEXB.xlsx")

# dfGold = pd.read_excel('data\\raw\\Gold.xlsx', index_col=0)
# spread_calc(dfGold, "data\\Gold.xlsx")
#
# dfSP = pd.read_excel('data\\raw\\SP500.xlsx', index_col=0)
# spread_calc(dfSP, "data\\SP500.xlsx")


#google_trend_all(dfs, "data\\GoogleTrendB.xlsx")
#google_trend_all_separate(dfs, "data\\GoogleTrendB_Sep.xlsx")
