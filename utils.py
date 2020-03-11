import datetime
import calendar
import numpy as np
import statsmodels.api as sm

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


def month_conv(value):
    year, month = value.split('-')
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


def find_first_day(index):
    for ind in index:
        if ind.day <= 4:
            return ind


def find_next_month(index):
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
