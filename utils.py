import datetime
import calendar
import time

import numpy as np
import statsmodels.api as sm
import pandas as pd
import numpy.linalg as la
from scipy import stats
from pytrends.request import TrendReq


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


def month_conv(value):
    tmp = value.split('-')
    if len(tmp) == 3:
        year, month, day = tmp
        return datetime.date(int(year), int(month), int(day))
    else:
        year, month = tmp
        return datetime.date(int(year), int(month), 1)


def gtrend_conv(value):
    if value == "<1":
        return 0.5
    return int(value)


def logarize(df):
    df['HighL'] = np.log(df['High'])
    df['LowL'] = np.log(df['Low'])
    df['CloseL'] = np.log(df['Close'])
    df['MidRange'] = (df['HighL'] + df['LowL']) / 2
    return df


def find_first_day(index, hour=False):
    if hour:
        for ind in index:
            if ind.hour == 0:
                return ind
    else:
        for ind in index:
            if ind.day <= 4:
                return ind


def find_next_month(index, hour=False):
    if hour:
        day = index[0].day
        for ind in index:
            if ind.day != day:
                return ind
    else:
        month = index[0].month
        ind = None
        for ind in index:
            if ind.month != month:
                return ind
        return ind


def diff_and_lag(df):
    df = df.join(np.log(df), rsuffix="Log")
    df = df.join(df.diff(), rsuffix="Diff")[1:]
    #df["GoogleTrendS"] = np.power(df["GoogleTrend"], 2)
    return df.join(df.shift(), rsuffix="Lag")[1:]


def compare_two_exchanges(df1, df2, y, x):
    df1 = df1.reset_index()
    df2 = df2.reset_index()
    df1.set_index("Month", inplace=True)
    df2.set_index("Month", inplace=True)
    dfd = df2[[y]]-df1[[y]]
    dfd = dfd.join(df1[x])
    dfd.dropna(inplace=True)
    y = dfd[y]
    X = dfd[x]
    return sm.RLM(y, X, M=sm.robust.norms.AndrewWave()).fit()


def gtrend_combine(ts1: pd.Series, ts2:pd.Series):
    tsu = ts1.index.intersection(ts2.index)
    if len(tsu) == 0:
        pass
    ts1S = None
    ts2S = None
    for t in tsu:
        ts1S = ts1[t]
        ts2S = ts2[t]
        if ts1S != 0 and ts2S != 0:
            break
    if ts1S is None:
        raise Exception()
    ratio = ts1S/ts2S
    if ratio > 1:
        ts1 = ts1/ratio
        ts1.drop(tsu, inplace=True)
    else:
        ts2 = ts2*ratio
        ts2.drop(tsu, inplace=True)
    return ts1.append(ts2)


def get_gtrend(topic, start: datetime.date, end: datetime.date):
    res = None
    pytrends = TrendReq(hl='en-US', tz=0)
    kw_list = [topic]
    while start < end:
        time.sleep(1)
        tmp = add_months(start, 1)
        if tmp > end:
            tmp = end
        if res is not None:
            start = add_months(start, -1)
            start = start.replace(day=15)
        start_str = start.strftime("%Y-%m-%d")
        end_str = tmp.strftime("%Y-%m-%d")
        pytrends.build_payload(kw_list, timeframe=start_str + " " + end_str)
        df = pytrends.interest_over_time()
        if res is None:
            res = df[topic]
        else:
            res = gtrend_combine(res, df[topic])
        start = tmp
    return res


def convert_trend(ts: pd.Series, base, to, reserve=None, reserve_k=None):
    """

    :type ts: pandas.Series
    """
    if base == to:
        return ts
    pytrends = TrendReq(hl='en-US', tz=0)
    kw_list = [base, to]
    start = ts.index[ts.argmax()]
    end = start + datetime.timedelta(days=2)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    pytrends.build_payload(kw_list, timeframe=start_str + " " + end_str)
    df = pytrends.interest_over_time()
    k = df.loc[start][base] / ts[start]
    if k == 0 and reserve_k is not None:
        ts = convert_trend(ts, base, reserve)
        k = reserve_k
    ts = ts * k
    return ts, k


def hausman(fe, re):
    """
    Compute hausman test for fixed effects/random effects models
    b = beta_fe
    B = beta_re
    From theory we have that b is always consistent, but B is consistent
    under the alternative hypothesis and efficient under the null.
    The test statistic is computed as
    z = (b - B)' [V_b - v_B^{-1}](b - B)
    The statistic is distributed z \sim \chi^2(k), where k is the number
    of regressors in the model.
    Parameters
    ==========
    fe : statsmodels.regression.linear_panel.PanelLMWithinResults
        The results obtained by using sm.PanelLM with the
        method='within' option.
    re : statsmodels.regression.linear_panel.PanelLMRandomResults
        The results obtained by using sm.PanelLM with the
        method='swar' option.
    Returns
    =======
    chi2 : float
        The test statistic
    df : int
        The number of degrees of freedom for the distribution of the
        test statistic
    pval : float
        The p-value associated with the null hypothesis
    Notes
    =====
    The null hypothesis supports the claim that the random effects
    estimator is "better". If we reject this hypothesis it is the same
    as saying we should be using fixed effects because there are
    systematic differences in the coefficients.
    """

    # Pull data out
    b = fe.params
    B = re.params
    v_b = fe.cov
    v_B = re.cov

    # NOTE: find df. fe should toss time-invariant variables, but it
    #       doesn't. It does return garbage so we use that to filter
    df = b[np.abs(b) < 1e8].size

    # compute test statistic and associated p-value
    chi2 = np.dot((b - B).T, la.inv(v_b - v_B).dot(b - B))
    pval = stats.chi2.sf(chi2, df)

    return chi2, df, pval


def get_google_trend_month(topic):
    pytrends = TrendReq(hl='en-US', tz=0)
    kw_list = [topic]
    pytrends.build_payload(kw_list, timeframe="all")
    df = pytrends.interest_over_time()
    return pd.DataFrame({"GoogleTrend": df[topic]})
