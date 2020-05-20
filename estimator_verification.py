import datetime

import pandas as pd
import statsmodels.api as sm
import numpy as np
from linearmodels import PanelOLS, RandomEffects, FamaMacBeth

from utils import hausman, diff_and_lag, create_panel_data, check_volume

dfs = pd.read_excel('data\\BITFINEX.xlsx', sheet_name=None, index_col=0)

df = create_panel_data(dfs)
resfbCHL = check_volume(df, "TwoDayCorrected")
resfbHL = check_volume(df, "HL")
resfbRoll = check_volume(df, "RollMonthlyCorrected")

# y = df["TwoDayCorrectedLog"]
# X = df[["const", "CRSP"]]
# # X = sm.add_constant(X)
# #
# mod = PanelOLS(y, X, entity_effects=True, time_effects=False)
# modr = RandomEffects(y, X)
# resr = modr.fit(cov_type='clustered', cluster_entity=True)
# resf = mod.fit(cov_type='clustered', cluster_entity=True)
#
# print(hausman(resf, resr))

dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)

df = create_panel_data(dfs)

dfSpread = df[["CRSP", "TwoDayCorrected", "Volume", "RollMonthlyCorrected", "HL"]]

res = [None, None]
for level in [0, 1]:
    for i in dfSpread.reset_index().set_index(["Currency", "Month"]).index.levels[level]:
        tmp = dfSpread.xs(key=i, level=level).corr()
        tmp["Level"] = i
        tmp.reset_index(inplace=True)
        tmp.set_index(["Level", "index"], inplace=True)
        if res[level] is None:
            res[level] = tmp
            continue
        if not tmp.isnull().values.any():
            res[level] = res[level].append(tmp)