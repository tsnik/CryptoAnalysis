import datetime

import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import PanelOLS, RandomEffects, FamaMacBeth

from utils import diff_and_lag, hausman, create_panel_data, log

dfs = pd.read_excel('data\\BITFINEX.xlsx', sheet_name=None, index_col=0)
dfGTrends = pd.read_excel('data\\GoogleTrend.xlsx', sheet_name=None, index_col=0)
df = pd.DataFrame()
for k in dfs:
    tmp = dfs[k].join(dfGTrends[k]/100)
    tmp = tmp.join(dfGTrends["Bitcoin"] / 100, rsuffix="BTC")
    tmp = diff_and_lag(tmp)
    dfs[k] = tmp

df = create_panel_data(dfs)
log(df, ["TwoDayCorrected", "VolumeUSD", "GoogleTrend", "HL"])

y = df["HLLog"]
X = df[["const", "GoogleTrendLog"]]


modfb = FamaMacBeth(y, X)
resfb = modfb.fit(cov_type='kernel')

