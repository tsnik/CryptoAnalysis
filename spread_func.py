import numpy as np


def ARAMonthlyCorrected(month):
    mid_range = month['MidRange']
    close_l = month['CloseL']
    summm = np.sum((close_l - mid_range) * (close_l - mid_range.shift(-1)))
    summm = max([summm, 0])
    s = np.sqrt(summm * 4 / (len(mid_range) - 1))
    return s


def ARATwoDayCorrected(month):
    mid_range = month['MidRange']
    close_l = month['CloseL']
    two_days = (close_l - mid_range) * (close_l - mid_range.shift(-1))
    two_days[two_days < 0] = 0
    summm = np.sum(two_days)
    s = np.sqrt(summm * 4 / (len(mid_range) - 1))
    return s


def ROLLMonthlyCorrected(month):
    close = month["Close"]
    returns = close / close.shift()
    s = 4 * returns.autocorr() * returns.var()
    s = max([s, 0])
    s = np.sqrt(s)
    s2 = ROLLMonthlyCorrectedManual(month)
    print("{0} == {1} - {2}".format(s, s2, s == s2))
    return s


def ROLLMonthlyCorrectedManual(month):
    close = month["Close"]
    returns = close / close.shift()
    returns_m = returns.mean()
    s = np.sum((returns - returns_m) * (returns.shift() - returns_m))
    s = s * 4 / (len(close) - 2)
    s = max([s, 0])
    s = np.sqrt(s)
    return s


def ROLLTwoDayCorrected(month):
    close = month["Close"]
    returns = close / close.shift()
    returns_m = returns.mean()
    two_days = (returns - returns_m) * (returns.shift(-1) - returns_m)
    two_days[two_days < 0] = 0
    summm = np.sum(two_days)
    s = np.sqrt(summm * 4 / (len(close) - 1))
    return s
