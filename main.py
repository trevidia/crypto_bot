from time import timezone
from datetime import datetime

from binance.futures import Futures
import json
import tzlocal

datetime.utcfromtimestamp()


api_key = "5bde34b8cb1f6ac88398fb363e3f21369304b249e1266390c37d7f4cf4d7104c"
secret_key = "31428c096feb383319eaf617c2ec4fc010e82077bbd98a8808e755614a996fdf"

client = Futures(key=api_key, secret=secret_key)
client.base_url = "https://testnet.binancefuture.com/"
client.ac
client.mark_price_klines('ETHUSDT', '1m', )
# client.get_income_history(incomeType=)
# set leverage first before ordering
leverage_param = {
    "symbol": "ETHUSDT",
    "leverage": 50,
    "recvWindow": 50000,
}
# res = client.change_leverage(**leverage_param)
# client.new_order()