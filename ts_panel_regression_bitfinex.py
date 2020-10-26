import pandas as pd
import numpy as np
from linearmodels import PanelOLS, RandomEffects
import statsmodels.api as sm

from utils import diff_and_lag, create_panel_data, log, hausman

dfs = pd.read_excel('data\\BITFINEX.xlsx', sheet_name=None, index_col=0)
dfGTrends = pd.read_excel('data\\GoogleTrend.xlsx', sheet_name=None, index_col=0)
df = pd.DataFrame()
dfBTC = dfs["Bitcoin"].copy()
for k in dfs:
    tmp = dfs[k].join(dfGTrends[k]/100)
    tmp = tmp.join(dfGTrends["Bitcoin"] / 100, rsuffix="BTC")
    tmp = tmp.join(dfBTC, rsuffix="BTC")
    tmp["VolumeUSDMean"] = tmp["VolumeUSD"].mean()
    log(tmp, ["TwoDayCorrected", "VolumeUSD", "TwoDayCorrectedBTC", "GoogleTrend", "VolumeUSDMean"])
    tmp = diff_and_lag(tmp)
    dfs[k] = tmp

dfs.pop("Monero")
dfs.pop("EOS")
dfs.pop("Zcash")
dfs.pop("Bitcoin")
df = create_panel_data(dfs)

y = df["TwoDayCorrectedDiff"]
X = df[["TwoDayCorrectedBTCDiff", "const", "GoogleTrendDiff"]]

modf = PanelOLS(y, X, entity_effects=False, time_effects=False)
modr = RandomEffects(y, X)

resr = modr.fit(cov_type='clustered', cluster_entity=True)
resf = modf.fit(cov_type='clustered', cluster_entity=True)
#print(hausman(resf, resr))
