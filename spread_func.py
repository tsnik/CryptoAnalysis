import numpy as np
import pandas as pd


def ARAMonthlyCorrected(month):
    mid_range = month['MidRange']
    close_l = month['CloseL']
    summm = np.sum((close_l - mid_range) * (close_l - mid_range.shift(-1)))
    summm = max([summm, 0])
    s = np.sqrt(summm * 4 / (len(mid_range) - 1))
    return s


def ARATwoDayCorrected(month):
    mid_range = month['MidRange'][:-1]
    mid_range1 = month['MidRange'].shift(-1)[:-1]
    close_l = month['CloseL'][:-1]
    two_days = (close_l - mid_range) * (close_l - mid_range1)
    two_days[two_days < 0] = 0
    two_days.dropna(inplace=True)
    two_days = np.sqrt(two_days * 4)
    summm = np.sum(two_days)
    s = summm / len(two_days)
    return s


def HL(month):
    ht = month["HighL"][:-1]
    ht1 = month["HighL"].shift(-1)[:-1]
    lt = month["LowL"][:-1]
    lt1 = month["LowL"].shift(-1)[:-1]
    ct = month["CloseL"][:-1]
    ht1[lt1 > ct] = ht1 - (lt1 - ct)
    lt1[lt1 > ct] = lt1 - (lt1 - ct)
    ht1[ht1 < ct] = ht1 + (ct - ht1)
    lt1[ht1 < ct] = lt1 + (ct - ht1)
    hm = pd.concat([ht, ht1], axis=1).max(axis=1)
    lm = pd.concat([lt, lt1], axis=1).min(axis=1)
    y = np.power(hm - lm, 2)
    b = (np.power(ht1 - lt1, 2) + np.power(ht - lt, 2))
    a = ((np.sqrt(2 * b) - np.sqrt(b)) / (3 - 2 * np.sqrt(2))) - np.sqrt(y / (3 - 2 * np.sqrt(2)))
    s = 2 * (np.exp(a) - 1) / (1 + np.exp(a))
    s[s < 0] = 0
    return np.sum(s) / len(s)


def ROLLMonthlyCorrected(month):
    close = month["Close"]
    returns = close / close.shift()
    s = 4 * -returns.autocorr() * returns.var()
    s = max([s, 0])
    s = np.sqrt(s)
    s2 = ROLLMonthlyCorrectedManual(month)
    print("{0} == {1} - {2}".format(s, s2, s == s2))
    return s


def ROLLMonthlyCorrectedManual(month):
    close = month["Close"]
    returns = close / close.shift()
    returns.dropna(inplace=True)
    returns_m = returns.mean()
    returns_ms = returns.shift().mean()
    s = np.sum((returns[1:] - returns_m) * (returns.shift()[1:] - returns_ms))
    s = s / (len(returns) - 1)
    s = max([-s, 0])
    s = 2 * np.sqrt(s)
    return s


def ROLLTwoDayCorrected(month):
    close = month["Close"]
    returns = close / close.shift()
    returns.dropna(inplace=True)
    returns_m = returns.mean()
    two_days = (returns - returns_m) * (returns.shift(-1) - returns_m)
    two_days[two_days > 0] = 0
    summm = np.sum(two_days)
    s = 2 * np.sqrt(-summm / (len(close) - 1))
    return s


def amihud(month):
    close = month["Close"]
    returns = close / close.shift() - 1
    returns = returns[1:]
    month = month[1:]
    returns = returns.abs() * month["Volume"]
    return returns.sum() / len(returns)


def crsp(month):
    spread = month["PX_ASK"] - month["PX_BID"]
    spread = 2 * spread / (month["PX_ASK"] + month["PX_BID"])
    spread.loc[spread < 0] = 0
    spread = spread.mean()
    return spread
