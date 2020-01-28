from datetime import datetime, date

from spread_func import ARAMonthlyCorrected, ARATwoDayCorrected, ROLLMonthlyCorrectedManual, ROLLTwoDayCorrected
from utils import add_months

import pandas as pd
import numpy as np

df = pd.read_excel('pandas_simple.xlsx', sheet_name='ETHUSDT', index_col=0)

df.set_index('OpenTime', inplace=True)
df['HighL'] = np.log(df['High'])
df['LowL'] = np.log(df['Low'])
df['CloseL'] = np.log(df['Close'])
df['MidRange'] = (df['HighL'] + df['LowL']) / 2


start = date(2017, 9, 1)
results = []
while start != df.last_valid_index():
    end = add_months(start, 1)
    month = df[start:end]
    results.append({"Month": start, "MonthlyCorrected": np.exp(ARAMonthlyCorrected(month)),
                    "TwoDayCorrected": np.exp(ARATwoDayCorrected(month)),
                    # "ROLLMonthlyCorrected": 1 + ROLLMonthlyCorrectedManual(month),
                    "ROLLTwoDayCorrected": 1 + ROLLTwoDayCorrected(month)})
    start = end

res = pd.DataFrame(results)
res.set_index("Month")
print(res)
# print(s2**2)
# print(MidRange.autocorr(lag=1))
#
# print(df[start:end])