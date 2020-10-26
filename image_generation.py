import string

import pandas as pd
from matplotlib import pyplot
import matplotlib.dates as mdates
import datetime

dfs = pd.read_excel('data\\BITFINEXB.xlsx', sheet_name=None, index_col=0)
fig = pyplot.figure(figsize=(27, 16))
for i, c in enumerate(dfs):
    # df = (dfs[c]["TwoDayCorrected"] - 1) * 100
    df = (dfs[c]["CRSP"]) * 100
    df = df[datetime.datetime(2018, 4, 1):]
    #fig, r = pyplot.subplots(figsize=(9, 4))
    r = pyplot.subplot(3, 3, i + 1)
    r.plot(df.index.astype('O').values, df)
    r.set_title(c, fontsize=32)
    r.set_ylabel("Spread, %", fontsize=28)
    pyplot.gca().spines['right'].set_visible(False)
    pyplot.gca().spines['top'].set_visible(False)
    formatter = mdates.DateFormatter('%b %y')
    r.xaxis.set_major_formatter(formatter)
    r.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1]))
    r.tick_params(axis='both', labelsize=18)
    r.tick_params(axis='x', rotation=70)
    r.set_xlim(datetime.date(2018, 1, 1), datetime.date(2020, 3, 1))
    r.set_xticks(r.get_xticks()[::2])
    # t = "\n".join([" ".join(str(df.describe().round(3)).split("\n")[i].split()) for i in [1, 2, 3, 7]])\
    #    .replace(" ", ": ")
    # pyplot.plot([], [], ' ', label=t)
    # pyplot.legend(loc="upper left", bbox_to_anchor=(1.04, 1))
    #pyplot.savefig("images\\" + c + ".png", bbox_inches='tight')
    #pyplot.show()

pyplot.show()
fig.savefig("images\\Spreads.png")
