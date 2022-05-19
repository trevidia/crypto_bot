from datetime import datetime
import json
from bot import Bot
import asyncio

import websocket
import talib
import numpy as np

pair = "ethusdt"
contract = "perpetual"
interval = "1m"
stream_url = f"wss://fstream.binance.com/ws/{pair}_{contract}@continuousKline_{interval}"
close_price_list = []
orders = []
second = 0
prev_second = 0

sma_8_pair = [0, 0]
sma_50_pair = [0, 0]

Bot.init()
prev_price_list = Bot.get_prev_data()
for candle in prev_price_list:
    close_price_list.append(round(float(candle[4]), 3))


def on_close(sock):
    # todo export data to an excel spreadsheet
    total_profit = 0
    total_loss = 0
    successful = 0
    failed = 0
    for income in Bot.trades:
        if income["successful"]:
            successful += 1
            total_profit += income["income"]
        else:
            failed += 1
            total_loss += income["income"]
        total_loss -= income["commission"]
    print(f"Total successful trades: {successful}")
    print(f"Total failed trades: {failed}")
    print(f"Total profit: {total_profit}")
    print(f"Total loss: {total_loss}")
    print(Bot.trades)
    print("stream ended")


message_count = 0


def on_message(sock, msg):
    global close_price_list
    global sma_8_pair
    global sma_50_pair
    global message_count
    global second
    global prev_second

    message = json.loads(msg)
    data = message['k']
    second = datetime.utcfromtimestamp(int(message["E"]) / 1000).second
    if data['x']:
        run_strategy(data)
    # if second != prev_second:
    #     message_count += 1
    # elif message_count == 60:
    #     run_strategy(data)
    #     message_count = 0

    # print(message["E"])
    # run_strategy(data)
    # message_count += 1
    # print(message_count)
    prev_second = second


def run_strategy(data):
    global message_count
    current_close_price = round(float(data['c']), 3)

    message_count = 0
    # data for indicators
    close_price_list.append(current_close_price)
    np_close_price = np.array(close_price_list)

    # indicators

    sma_8_list = talib.SMA(np_close_price, timeperiod=50)
    sma_8 = float(sma_8_list[-1])
    sma_50_list = talib.SMA(np_close_price, timeperiod=200)
    sma_50 = float(sma_50_list[-1])

    sma_8_pair[1] = sma_8
    sma_50_pair[1] = sma_50

    rsi_10_list = talib.RSI(np_close_price, timeperiod=14)
    rsi_10 = rsi_10_list[-1]
    print(rsi_10)
    asyncio.run(
        Bot.implement_strategy(rsi_10=rsi_10, current_price=current_close_price))
    # if not np.isnan(sma_50):
    #     print(f"price: {current_close_price}")
    #     print(f"sma_50: {sma_50}, sma_8: {sma_8}")
    #     print(f"rsi_6: {rsi_6} \n")
    #     print(f"sma_8 pair: {sma_8_pair}")
    #     print(f"sma_50 pair: {sma_50_pair}")
    #     asyncio.run(
    #         Bot.implement_strategy(current_price=current_close_price,
    #                                sma_8_list=sma_8_pair, sma_50_list=sma_50_pair))
    #     sma_8_pair[0] = sma_8
    #     sma_50_pair[0] = sma_50

    # else:
    #     print(f"Loading... {sma_8} {sma_50}")


ws = websocket.WebSocketApp(stream_url, on_message=on_message, on_close=on_close)
ws.run_forever()
