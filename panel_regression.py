import pandas as pd
from linearmodels import PanelOLS, RandomEffects
import statsmodels.api as sm
import numpy as np

from utils import diff_and_lag, compare_two_exchanges

df = pd.read_excel('data\\BTC_BITFINEX.xlsx', index_col=0)[30:]
df2 = pd.read_excel('data\\BTC_KRAKEN.xlsx', index_col=0)[17:]
df3 = pd.read_excel('data\\BTC_Ibit.xlsx', index_col=0)[1:]
dfGTrend = pd.read_excel('data\\GoogleTrends.xlsx', index_col=0)
dfGTrend["GoogleTrend"] = dfGTrend["GoogleTrend"] / 100
df = diff_and_lag(df.join(dfGTrend))
df2 = diff_and_lag(df2.join(dfGTrend))
df3 = diff_and_lag(df3.join(dfGTrend))
df["Exchange"] = "BitFinex"
df2["Exchange"] = "Kraken"
df2["GK"] = df2["GoogleTrend"]
df2["IK"] = 1
df3["Exchange"] = "ItBit"
df3["GI"] = df3["GoogleTrend"]
df3["II"] = 1

df = df.append([df2, df3])
df.fillna(0, inplace=True)
df.reset_index(inplace=True)
df.set_index(["Exchange", "Month"], inplace=True)

df.sort_index(level=['Exchange', 'Month'], ascending=[1, 1], inplace=True)
y = df["TwoDayCorrected"]
X = df[["GoogleTrend", "TwoDayCorrectedLag", "GI", "GK"]]

X = sm.add_constant(X)

mod = PanelOLS(y, X)
modr = RandomEffects(y, X)
resr = modr.fit(cov_type='clustered', cluster_entity=True)
res = mod.fit(cov_type='clustered', cluster_entity=True)

test = compare_two_exchanges(df.loc["BitFinex"], df.loc["Kraken"], "TwoDayCorrected", ["GoogleTrend"])