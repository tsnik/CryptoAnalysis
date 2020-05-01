from datetime import datetime
import time

from bitfinex.rest.restv2 import Client
import pandas as pd

bfx_client = Client()

config = bfx_client.configs_list([{"action": "list", "obj": "pair", "detail": "exchange"},
                             {"action": "map", "obj": "currency", "detail": "sym"},
                             {"action": "map", "obj": "currency", "detail": "label"}])
t = config[0]
t = ["t"+i for i in t if "USD" in i and "DUSK" not in i and "XAUT" not in i]
names = {i[0]: i[1] for i in config[2]}
names["EOS"] = "EOS"

t = bfx_client.tickers(t)
t = [{"name": i[0], "realName": names[i[0][1:-3]], "volume": i[8], "last": i[7]} for i in t]
df = pd.DataFrame(t)
df["VolumeUSD"] = df["volume"] * df["last"]
df.sort_values("VolumeUSD", inplace=True, ascending=False)
df = df[df["VolumeUSD"] > 1000]

results = {}
for i in df.index:
    time.sleep(1)
    r = df.loc[i]
    dft = bfx_client.candles("1D", r["name"], "hist", limit=1500, end=int(datetime(2020, 3, 2).timestamp() * 1000))
    dft = pd.DataFrame(dft)
    dft.rename(columns={0: "OpenTime", 1: "Open", 2: "Close", 3: "High", 4: "Low", 5: "Volume"}, inplace=True)
    dft["OpenTime"] = pd.to_datetime(dft['OpenTime'], unit='ms')
    dft.set_index("OpenTime", inplace=True)
    dft.sort_index(inplace=True)
    if len(dft[:datetime(2018, 1, 1)]) > 0:
        results[r["realName"]] = dft[datetime(2018, 1, 1):]

with pd.ExcelWriter('data\\raw\\BITFINEX.xlsx') as writer:
    for ticker in results:
        results[ticker].to_excel(writer, sheet_name=ticker)
