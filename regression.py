import pandas as pd
import statsmodels.api as sm
from arch.unitroot import DFGLS, ZivotAndrews, VarianceRatio, KPSS
from linearmodels import IV2SLS
from matplotlib import pyplot
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.api import VAR
import numpy as np
import datetime

from utils import diff_and_lag, log


name = "Litecoin"
dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)
XC = ["VIXDiffLag", "const"]
res = pd.DataFrame(columns=XC + ["R", "corr", "mean", "stat", "coint"], index=list(dfs.keys()))
models = {}
vars = {}
for d in dfs:
    #df = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=name, index_col=0)
    name = d
    df = dfs[d]
    dfBTC = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name='Bitcoin', index_col=0)
    df = df.join(dfBTC, rsuffix="BTC")
    dfTrend = pd.read_excel('data\\GoogleTrendB_Sep.xlsx', sheet_name=name, index_col=0)
    dfCoins = pd.read_excel('data\\raw\\Coins.xlsx', sheet_name=name, index_col=0)
    dfGold = pd.read_excel('data\\Gold.xlsx', index_col=0)
    dfVIX = pd.read_excel('data\\raw\\VIX.xlsx', index_col=0)

    df = df.join(dfGold, rsuffix="Gold")
    df = df.join(dfTrend/100)
    coinsDiff = dfCoins.sort_index().diff()
    days = pd.Series([d.days for d in coinsDiff.index.to_series().diff()])
    days.index = coinsDiff.index
    coinsDiff["Coins"] = coinsDiff["Coins"] / days
    coinsDiff = coinsDiff.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).mean()
    coins = dfCoins.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).max()
    df = df.join(coins)
    vix = dfVIX.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).mean()
    df = df.join(vix)
    #df.dropna(inplace=True)
    df["Supply"] = coinsDiff["Coins"]
    df["Size"] = df["Coins"] * df["Close"]
    #df["VolumeUSDMean"] = df["VolumeUSD"].mean()
    log(df, ["CRSP", "VolumeUSD", "GoogleTrend", "Volume", "Return", "CRSPBTC"])
    df["ReturnAbs"] = np.abs(df["ReturnAvg"] - 1)
    df = diff_and_lag(df)
    df = sm.tsa.add_trend(df, trend='ct')

    qh = df["CRSPGoldDiff"].quantile(0.9)
    ql = df["CRSPGoldDiff"].quantile(0.1)
    df["CRSPGoldDiff"][(df["CRSPGoldDiff"] > qh) | (df["CRSPGoldDiff"] < ql)] = None
    df["CRSPGoldDiff"].fillna(method="ffill", inplace=True)
    df = df[datetime.datetime(2018, 4, 1):]
    #df.dropna(inplace=True)
    y = df["CRSPDiff"]
    X = df[XC]
    model = sm.GLS(y, X, hasconst=True, missing='drop').fit().get_robustcov_results()
    models[d] = model
    vars[d] = VAR(df[["CRSPDiff", "CRSPBTCDiff"]].dropna()).fit(method='gls', maxlags=1)
    for i, n in enumerate(model.model.exog_names):
        if model.pvalues[i] < 0.05:
            res.loc[d][n] = model.params[i]
    res.loc[d]["R"] = model.rsquared
    res.loc[d]["corr"] = df["CRSPDiff"].corr(df["CRSPGoldDiff"])
    res.loc[d]["mean"] = df["CRSP"].mean()
    res.loc[d]["stat"] = sm.tsa.adfuller(df["VIXDiff"].dropna(), regression="c", maxlag=6)[1]
    #res.loc[d]["coint"] = sm.tsa.coint(df["CRSPBTCDiff"][3:], df["CRSPDiff"][3:])[1]
    #res.loc[d]["stat"] = KPSS(df["VolumeUSDLogDiff"].dropna(), lags=5).pvalue
    #if d != "EOS" and d != "Monero" and d!="Zcash":
    #res.loc[d]["stat"] = DFGLS(df["VolumeUSDLogDiff"].dropna()).pvalue
    #res.loc[d]["stat"] = ZivotAndrews(df["ReturnAbsDiff"].dropna(), max_lags=2).pvalue
    #df["CRSP"].plot()
    print(len(df["CRSPDiff"].dropna()))
    #df.plot.scatter("CRSPDiff", "SupplyDiff")
    df["SupplyDiff"].plot()
    pyplot.title(d)
    #pyplot.show()
#model1 = sm.RLM(y, X, M=sm.robust.norms.AndrewWave()).fit()

# print(sm.tsa.adfuller(df["GoogleTrendDiff"]))
# print(sm.tsa.adfuller(df["ReturnLogAbs"]))
# print(sm.tsa.adfuller(df["VolumeUSDLog"]))
# #print(sm.tsa.adfuller(df["Supply"]))
# print(sm.tsa.coint(df["GoogleTrendDiff"], df["VolumeUSDLog"]))
