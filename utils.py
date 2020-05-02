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
        for ind in index:
            if ind.month != month:
                return ind


def diff_and_lag(df):
    df = df.diff()[1:]
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
