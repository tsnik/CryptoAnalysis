import datetime

import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import PanelOLS, RandomEffects, FamaMacBeth

from utils import diff_and_lag, hausman, create_panel_data, log

dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)
dfGTrends = pd.read_excel('data\\GoogleTrendB.xlsx', sheet_name=None, index_col=0)
dfCoins = pd.read_excel('data\\raw\\Coins.xlsx', sheet_name=None, index_col=0)
df = pd.DataFrame()
for k in dfs:
    tmp = dfs[k].join(dfGTrends[k]/100)
    tmp = tmp.join(dfGTrends["Bitcoin"] / 100, rsuffix="BTC")
    coins = dfCoins[k]
    coins = coins.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).max()
    tmp = tmp.join(coins)
    tmp["Size"] = tmp["Coins"] * tmp["Close"]
    log(tmp, ["Size"])
    tmp = diff_and_lag(tmp)
    tmp["CoinsDiff"] = tmp["CoinsDiff"] / tmp["CoinsDiff"].mean()
    print(sm.tsa.adfuller((tmp["VolumeUSD"]).diff().diff().dropna()))
    dfs[k] = tmp

df = create_panel_data(dfs)
#df["Size"] = df["Coins"] * df["Close"]
log(df, ["CRSP", "TwoDayCorrected", "VolumeUSD", "Size", "GoogleTrend", "HL"])

y = df["CRSPLog"]
X = df[["const", "GoogleTrendLog", "VolumeUSDLog", "SizeDiff"]]

# mod = PanelOLS(y, X, entity_effects=True, time_effects=False)
# modr = RandomEffects(y, X)
modfb = FamaMacBeth(y, X)
resfb = modfb.fit(cov_type='kernel')
# resr = modr.fit(cov_type='clustered', cluster_entity=True)
# res = mod.fit(cov_type='clustered', cluster_entity=True)
# print(hausman(res, resr))
