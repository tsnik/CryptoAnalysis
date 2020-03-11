import pandas as pd
import statsmodels.api as sm
import numpy as np

df = pd.read_excel('data\\BTC_BITFINEX.xlsx', index_col=0)[1:]
dfSP = pd.read_excel('data\\SP500.xlsx', index_col=0)
dfTrend = pd.read_excel('data\\GoogleTrends.xlsx', index_col=0)

df["Volume"] = df["Volume"] / 1000000
dfTrend["GoogleTrend"] = dfTrend["GoogleTrend"] / 1000
y = df["TwoDayCorrected"]
X = df[["Volume", "Return", "Close"]]
X = X.join(dfTrend["GoogleTrend"])
X = X.join(dfSP[["TwoDayCorrected", "Volume", "Return", "Close"]], rsuffix="SP500")
X = X[["GoogleTrend"]]
y = y.diff()[1:]
X = X.diff()[1:]
X = X.join(y.shift(), rsuffix="Lag")[1:]
y = y[1:]
# X = sm.add_constant(X)

# model = sm.OLS(y, X, hasconst=True).fit().get_robustcov_results()
model = sm.RLM(y, X, M=sm.robust.norms.AndrewWave()).fit()

model.summary()
