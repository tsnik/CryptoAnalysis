import datetime

import pandas as pd
import statsmodels.api as sm
import numpy as np
from linearmodels import PanelOLS, RandomEffects, FamaMacBeth

from utils import hausman

dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)

df = None
for k in dfs:
    tmp = dfs[k]
    tmp["Currency"] = k
    tmp.reset_index(inplace=True)
    tmp = sm.tsa.add_trend(tmp, trend="ct")
    if df is None:
        df = tmp
        continue
    df = df.append(tmp)

df.set_index(["Currency", "Month"], inplace=True)
df.sort_index(level=['Currency', 'Month'], ascending=True, inplace=True)
df["Volume"] = df["Volume"] / 1000 / 1000 / 1000
df["VolumeLog"] = np.log(df["Volume"])

y = (df["TwoDayCorrected"] - 1) * 100
X = df[["const", "Volume"]]

modfb = FamaMacBeth(y, X)
resfb = modfb.fit(cov_type="robust")

dfspreads = pd.read_excel('data\\SpreadB.xlsx', sheet_name=None, index_col=0)
dfSpread = None
first_date = None
for k in dfspreads:
    tmp = dfspreads[k]
    tmp = tmp.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).mean()
    tmp = tmp.iloc[10:]
    tmp.reset_index(inplace=True)
    tmp.rename(columns={tmp.columns[0]: "Month"}, inplace=True)
    tmp.dropna(inplace=True)
    if first_date is None or first_date < tmp.iloc[0]["Month"]:
        first_date = tmp.iloc[0]["Month"]
    tmp["Currency"] = k
    if dfSpread is None:
        dfSpread = tmp
        continue
    dfSpread = dfSpread.append(tmp)

indexNames = dfSpread[dfSpread['Month'] < first_date].index
dfSpread.drop(indexNames, inplace=True)

dfSpread.set_index(["Currency", "Month"], inplace=True)
dfSpread.sort_index(level=['Currency', 'Month'], ascending=True, inplace=True)

dfSpread = df.join(dfSpread)[["Spread", "TwoDayCorrected", "ROLLMonthlyCorrected", "Amihud", "Volume"]]
dfSpread["Spread"][dfSpread["Spread"] <= 1] = np.NaN
dfSpread.dropna(inplace=True)

y = dfSpread["Spread"]
X = dfSpread[["TwoDayCorrected"]]
X = sm.add_constant(X)

mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
modr = RandomEffects(y, X)
resr = modr.fit(cov_type='clustered', cluster_entity=True)
resf = mod.fit(cov_type='clustered', cluster_entity=True)

print(hausman(resf, resr))

res = [None, None]
for level in [0, 1]:
    for i in dfSpread.reset_index().set_index(["Currency", "Month"]).index.levels[level]:
        tmp = dfSpread.xs(key=i, level=level).corr()
        if res[level] is None:
            res[level] = tmp
            continue
        if not tmp.isnull().values.any():
            res[level] = res[level] + tmp