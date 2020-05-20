import time

import pandas as pd
import numpy as np

from spread_func import ARAMonthlyCorrected, ARATwoDayCorrected, ROLLTwoDayCorrected, ROLLMonthlyCorrectedManual, \
    amihud, ROLLMonthlyCorrected, crsp, HL
from utils import month_conv, gtrend_conv, add_months, logarize, find_first_day, find_next_month, get_google_trend_month


def google_trend(files, outputfile):
    if type(files) is not list:
        files = [files]
    dfs = {}
    for file in files:
        g_trends = pd.read_csv(file, converters={1: gtrend_conv}, parse_dates=True,
                               date_parser=month_conv, index_col="Month")
        name = file.split("\\")[-1][1:].split('_')[0]
        dfs[name] = g_trends
    with pd.ExcelWriter(outputfile) as writer:
        for df in dfs:
            dfs[df].to_excel(writer, sheet_name=df)


def spread_calc(dfs, outfile, hour=False):
    if type(dfs) is not dict:
        dfs = {"Data": dfs}
    res = {}
    for k, df in dfs.items():
        logarize(df)

        start = find_first_day(df.index, hour)
        results = []
        while start != df.last_valid_index():
            end = find_next_month(df[start:].index, hour)
            month = df[start:end]
            if month.count()[0] < 15:
                start = end
                continue
            m = start
            if not hour:
                m = start.replace(day=1)
            tmp = {"Month": m, "MonthlyCorrected": ARAMonthlyCorrected(month),
                   "TwoDayCorrected": ARATwoDayCorrected(month),
                   "RollMonthlyCorrected": ROLLMonthlyCorrectedManual(month),
                   "HL": HL(month),
                   "Amihud": amihud(month),
                   "Volume": np.sum(month["Volume"][:-1]),
                   "VolumeUSD": np.sum((month["Volume"]*month["Close"])[:-1]),
                   "Return": month.iloc[-2]["Close"] / month.iloc[0]["Close"],
                   "Close": month.iloc[-2]["Close"],
                   "MidPrice": (month.iloc[-2]["Close"] + month.iloc[0]["Close"]) / 2,
                   }
            month = month.dropna()
            if "PX_ASK" in month.columns and len(month) > 15:
                tmp["CRSP"] = crsp(month)
            results.append(tmp)
            start = end

        res_t = pd.DataFrame(results)
        res_t = res_t.set_index("Month")
        res[k] = res_t

    with pd.ExcelWriter(outfile) as writer:
        for k, r in res.items():
            r.to_excel(writer, sheet_name=k)


def coins_number(files, outputfile):
    if type(files) is not list:
        files = [files]
    dfs = {}
    for file in files:
        coins = pd.read_csv(file, parse_dates=True,
                            date_parser=month_conv, index_col="Month")
        name = file.split("\\")[-1][:-9]
        coins = coins.loc[~coins.index.duplicated(keep="last")]
        dfs[name] = coins
    with pd.ExcelWriter(outputfile) as writer:
        for df in dfs:
            dfs[df].to_excel(writer, sheet_name=df)


def spread(dfs, outputfile):
    with pd.ExcelWriter(outputfile) as writer:
        for k in dfs:
            dfs[k]["Spread"] = dfs[k]["PX_ASK"] / dfs[k]["PX_BID"]
            dfs[k].loc[dfs[k]["Spread"] < 1, "Spread"] = 1
            dfs[k] = dfs[k][["Spread"]]
            dfs[k].to_excel(writer, sheet_name=k)


def google_trend_all(dfs, outputfile):
    with pd.ExcelWriter(outputfile) as writer:
        trends = {}
        keys = list(dfs.keys())
        last = None
        while len(keys) > 0:
            if last is None:
                topics = keys[:2]
                keys = keys[2:]
            else:
                topics = keys[:1]
                keys = keys[1:]
                topics.append(last)
            time.sleep(1)
            tmp = get_google_trend_month(topics)
            if last is not None:
                ratio = trends[last]["GoogleTrend"].mean() / tmp[last]["GoogleTrend"].mean()
                for k in tmp.keys():
                    if k == last:
                        continue
                    tmp[k]["GoogleTrend"] = tmp[k]["GoogleTrend"] * ratio
                    trends[k] = tmp[k]
            else:
                trends = tmp
            last = list(tmp.keys())[-1]
            for k in trends:
                if trends[k]["GoogleTrend"].mean() < trends[last]["GoogleTrend"].mean():
                    last = k
        for k in trends:
            df = trends[k]
            df[df["GoogleTrend"] == 0] = None
            df.fillna(method="ffill", inplace=True)
            df.to_excel(writer, sheet_name=k)
