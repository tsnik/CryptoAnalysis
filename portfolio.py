import datetime

import pandas as pd
import numpy as np
from matplotlib import pyplot
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from math import sqrt, floor


def rebalance_portfolio(amounts: pd.Series, weights: pd.Series, costs: pd.Series):
    curr_weights = amounts / amounts.sum()
    base_const = amounts.sum()
    base_arr_coefs = {}
    for i in weights.index:
        sign = -1  # Sell
        if weights[i] > curr_weights[i]:  # Buy
            sign = 1
        base_const = base_const + sign * amounts[i] * costs[i]
        base_arr_coefs[i] = sign * costs[i]
        # base_arr_coefs[i] = 0
    base_arr_coefs = pd.Series(base_arr_coefs)
    coefs = []
    consts = []
    for i in weights.index:
        consts.append(base_const * weights[i])
        tmp = base_arr_coefs * weights[i]
        tmp[i] = tmp[i] + 1
        coefs.append(tmp.to_numpy())
    n_amounts = np.linalg.solve(coefs, consts)
    return n_amounts


def calc_sharpe(dfs, start, weights, rebalance_condition):
    df = pd.DataFrame()  # Dataframe with returns
    for k in dfs:
        df[k] = dfs[k]["Return"] - 1
        df.fillna(0, inplace=True)
    dfRB = pd.DataFrame()  # Dataframe with portfolio
    dfRB["Date"] = df.loc[start:].reset_index()["Month"]  # Dates
    dfRB["Total_after"] = 0
    for k in weights:
        dfRB[k + "_amount_after"] = 10000 * weights[k]
        dfRB["Total_after"] = dfRB["Total_after"] + dfRB[k + "_amount_after"]
        dfRB[k + "_weight"] = weights[k]

    dfRB["Total_Before"] = 0
    for i, d in enumerate(dfRB["Date"][1:], start=1):
        for k in weights:
            dfRB.loc[i, k + "_amount_before"] = dfs[k].loc[d, "Return"] * dfRB.loc[i-1, k+"_amount_after"]
            dfRB.loc[i, "Total_Before"] = dfRB.loc[i, "Total_Before"] + dfRB.loc[i, k + "_amount_before"]
        dfRB.loc[i, "Total_after"] = dfRB.loc[i, "Total_Before"]
        for e, k in enumerate(weights):
            dfRB.loc[i, k + "_amount_after"] = dfRB.loc[i, k + "_amount_before"]
        if rebalance_condition(i):
            amounts_r = pd.Series({k: dfRB.loc[i, k + "_amount_before"] for k in weights})
            weights_r = pd.Series(weights)
            costs = pd.Series({k: sqrt(1 + dfs[k].loc[d, "CRSP"]) - 1 for k in weights})
            amounts_n = rebalance_portfolio(amounts_r, weights_r, costs)
            dfRB.loc[i, "Total_after"] = 0
            for e, k in enumerate(weights):
                dfRB.loc[i, k + "_amount_after"] = amounts_n[e]
                dfRB.loc[i, "Total_after"] = dfRB.loc[i, "Total_after"] + amounts_n[e]

    dfRB.set_index("Date", inplace=True)

    # returns_nrb = df["Total"].pct_change().dropna()
    returns_rb = dfRB["Total_after"].pct_change().dropna()

    # print(returns_nrb.mean() / returns_nrb.std())
    print(rebalance_condition.__name__ + ": " + str(round(returns_rb.mean() / returns_rb.std(), 4)))

    # df["Total"].reset_index().dropna().set_index("Month").plot()
    # pyplot.show()
    dfRB["Total_after"].reset_index().set_index("Date").plot()
    pyplot.show()


def monthly(x):
    return x % 1 == 0


def three_monhly(x):
    return x % 3 == 0


def six_monthly(x):
    return x % 6 == 0


def no_rebalance(x):
    return False


def equal_weights(dfs, start):
    weights = {}
    for k in dfs:
        weights[k] = floor(1 / len(dfs) * 100) / 100
    first = list(weights.keys())[0]
    weights[first] = 0
    weights[first] = 1 - sum(weights.values())
    return weights


def norm_weights(weights):
    sum_w = sum(weights.values())
    for k in weights:
        weights[k] = floor(weights[k] / sum_w * 100) / 100
        if weights[k] < 0.01:
            weights[k] = 0.01
    first = list(weights.keys())[0]
    weights[first] = 0
    weights[first] = 1 - sum(weights.values())
    return weights


def liqudity_weights(dfs, start):
    weights = {}
    for k in dfs:
        weights[k] = 1 / dfs[k].loc[start, "CRSP"]
    return norm_weights(weights)


def size_weights(dfs, start):
    weights = {}
    for k in dfs:
        weights[k] = dfs[k].loc[start, "Size"]
    return norm_weights(weights)


dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)
dfCoins = pd.read_excel('data\\raw\\Coins.xlsx', sheet_name=None, index_col=0)
for k in dfs:
    coins = dfCoins[k]
    coins = coins.resample("M", label="left", closed="left", loffset=datetime.timedelta(days=1)).max()
    dfs[k]["Size"] = coins["Coins"] * dfs[k]["Close"]
# weights = equal_weights(dfs)
# weights = liqudity_weights(dfs, datetime.datetime(2018, 5, 1))
# weights = size_weights(dfs, datetime.datetime(2018, 6, 1))
weight_calcs = [equal_weights, size_weights, liqudity_weights]
for w in weight_calcs:
    print(w.__name__)
    weights = w(dfs, datetime.datetime(2018, 6, 1))
    print(weights)
    calc_sharpe(dfs, datetime.datetime(2018, 6, 1), weights, monthly)
    calc_sharpe(dfs, datetime.datetime(2018, 6, 1), weights, three_monhly)
    calc_sharpe(dfs, datetime.datetime(2018, 6, 1), weights, six_monthly)
    calc_sharpe(dfs, datetime.datetime(2018, 6, 1), weights, no_rebalance)
