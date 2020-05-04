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
    two_days = np.sqrt(two_days * 4)
    summm = np.sum(two_days)
    s = summm / (len(mid_range) - 1)
    return s


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
    spread = month["PX_ASK"] / month["PX_BID"]
    spread.loc[spread < 1] = 1
    spread = spread.mean()
    return spread
