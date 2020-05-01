import pandas as pd
import numpy as np

from spread_func import ARAMonthlyCorrected, ARATwoDayCorrected, ROLLTwoDayCorrected, ROLLMonthlyCorrectedManual
from utils import month_conv, gtrend_conv, add_months, logarize, find_first_day, find_next_month


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


def spread_calc(df, outfile):
    logarize(df)

    start = find_first_day(df.index)
    results = []
    while start != df.last_valid_index():
        end = find_next_month(df[start:].index)
        month = df[start:end]
        if month.count()[0] < 15:
            start = end
            continue
        m = start.replace(day=1)
        results.append({"Month": m, "MonthlyCorrected": np.exp(ARAMonthlyCorrected(month)),
                        "TwoDayCorrected": np.exp(ARATwoDayCorrected(month)),
                        "ROLLMonthlyCorrected": 1 + ROLLMonthlyCorrectedManual(month),
                        "ROLLTwoDayCorrected": 1 + ROLLTwoDayCorrected(month),
                        "Volume": np.sum(month["Volume"][:-1]),
                        "Return": month.iloc[-2]["Close"] / month.iloc[0]["Close"],
                        "Open": month.iloc[0]["Open"], "Close": month.iloc[-2]["Close"],
                        "MidPrice": (month.iloc[-2]["Close"] + month.iloc[0]["Close"]) / 2,
                        })
        start = end

    res = pd.DataFrame(results)
    res = res.set_index("Month")

    with pd.ExcelWriter(outfile) as writer:
        res.to_excel(writer)
