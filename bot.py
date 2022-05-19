from binance.futures import Futures


class Bot:
    _buy = "BUY"
    _sell = "SELL"
    _balance = 0
    position = False
    _leverage = 50
    base_url = "https://testnet.binancefuture.com/"
    _api_key = "7b86f65d26c3faa35198fb8925ea1a3dd6823094be2d05d2767ee4a8a8cfec95"
    _secret_key = "7fdce981f38682dc338c7923d3351a31136f4c308d19863ef05066221e351aeb"
    _client = None
    symbol = "ETHUSDT"
    percent_profit = 0.8
    percent_loss = -0.1
    _recvWindow = 50000
    _daily_target = 0
    _starting_capital = 0
    _precision = 2
    _asset_precision = 3
    trades = []
    last_signal = ""
    current_signal = {
        "new": False,
        "signal": ""
    }

    @staticmethod
    def init():
        Bot._client = Futures(key=Bot._api_key, secret=Bot._secret_key, base_url=Bot.base_url)
        leverage_param = {
            "symbol": Bot.symbol,
            "leverage": Bot._leverage,
            "recvWindow": Bot._recvWindow,
        }
        Bot._client.change_leverage(**leverage_param)
        Bot.get_balance()
        Bot._starting_capital = Bot._balance
        Bot._daily_target = Bot._balance * 2
        print(f"Daily Target: {Bot._daily_target}")
        return Bot._client

    @staticmethod
    def get_signal(rsi_10):
        if rsi_10 <= 30:
            return Bot._sell
        elif rsi_10 >= 50:
            return Bot._buy
        # if sma_8_list[1] > sma_50_list[1]:
        #     Bot.current_signal["signal"] = Bot._buy
        #     Bot.current_signal["new"] = False
        # else:
        #     Bot.current_signal["signal"] = Bot._sell
        #     Bot.current_signal["new"] = False
        # if sma_8_list[1] > sma_50_list[1] and sma_8_list[0] < sma_50_list[0]:
        #     Bot.current_signal["signal"] = Bot._buy
        #     Bot.current_signal["new"] = True
        #     return Bot._buy
        # elif sma_8_list[1] < sma_50_list[1] and sma_8_list[0] > sma_50_list[0]:
        #     Bot.current_signal["signal"] = Bot._sell
        #     Bot.current_signal["new"] = True
        #     return Bot._sell

    @staticmethod
    async def implement_strategy(current_price, rsi_10):
        # todo: if balance is greater than the daily target use capital to invest more
        # till the balance
        if Bot._balance >= Bot._daily_target:
            initial_margin = Bot._starting_capital
        else:
            initial_margin = Bot._balance * 0.8
        quantity = round((initial_margin * Bot._leverage), Bot._precision) / current_price
        quantity = round(quantity, Bot._asset_precision)
        signal = Bot.get_signal(rsi_10)
        if Bot.position is False:
            if signal == Bot._buy:
                await Bot.place_long_order(initial_margin, quantity)

            elif signal == Bot._sell:
                await Bot.place_short_order(initial_margin, quantity)
        else:
            has_position = await Bot.has_position()
            print(f"Has positions {has_position}")
            if not has_position:
                Bot.get_last_trade()
                Bot.get_balance()
                Bot.position = False
                # if not Bot.current_signal["new"] and Bot.trades[-1]["successful"]:
                #     if Bot.current_signal["signal"] == Bot._buy:
                #         await Bot.place_long_order(initial_margin, quantity)
                #     else:
                #         await Bot.place_short_order(initial_margin, quantity)
                # else:
                #     Bot.position = False

    @staticmethod
    async def place_short_order(initial_margin, quantity):
        response = await Bot.sell(quantity)
        print(response)
        if response:
            print("sold")
            Bot.position = True
            entry = await Bot.get_entry_price()
            print(f"got entry {entry}")
            tp = round(short_stop_price(initial_margin, quantity, entry, Bot.percent_profit), Bot._precision)
            sl = round(short_stop_price(initial_margin, quantity, entry, Bot.percent_loss), Bot._precision)
            print(f"take profit: {tp}")
            print(f"stop loss: {sl}")
            Bot.take_shorted_profit(tp)
            Bot.stop_shorted_loss(sl)
            print(f"entry: {entry}")

    @staticmethod
    async def place_long_order(initial_margin, quantity):
        response = await Bot.buy(quantity)
        print(response)
        if response:
            print("bought")
        Bot.position = True
        entry = await Bot.get_entry_price()
        print(f"got entry {entry}")
        tp = round(
            long_stop_price(balance=initial_margin, qty=quantity, entry=entry,
                            percentage=Bot.percent_profit))
        sl = round(
            long_stop_price(balance=initial_margin, qty=quantity, entry=entry, percentage=Bot.percent_loss))
        print(f"take profit: {tp}")
        print(f"stop loss: {sl}")
        Bot.take_longed_profit(tp)
        Bot.stop_longed_loss(sl)
        print(f"entry: {entry}")

    @staticmethod
    def get_balance():
        Bot._balance = round(float(list(filter(lambda x: x["asset"] == "USDT", Bot.get_assets()))[0]['walletBalance']),
                             Bot._precision)
        return Bot._balance

    @staticmethod
    def get_assets():
        assets = Bot._client.account(recvWindow=Bot._recvWindow)
        return assets["assets"]

    @staticmethod
    async def buy(quantity):
        buy_param = {
            "symbol": Bot.symbol.capitalize(),
            "side": Bot._buy,
            "type": "MARKET",
            "recvWindow": Bot._recvWindow,
            "quantity": quantity,
        }
        return Bot._client.new_order(**buy_param)

    @staticmethod
    async def sell(quantity):
        sell_param = {
            "symbol": Bot.symbol.capitalize(),
            "side": Bot._sell,
            "type": "MARKET",
            "recvWindow": Bot._recvWindow,
            "quantity": quantity,
        }
        return Bot._client.new_order(**sell_param)

    @staticmethod
    def take_shorted_profit(stop_price=None):
        params = {
            "symbol": Bot.symbol.capitalize(),
            "side": Bot._buy,
            "type": "TAKE_PROFIT_MARKET",
            "timeInForce": "GTE_GTC",
            "recvWindow": Bot._recvWindow,
            "closePosition": True,
            "stopPrice": stop_price
        }
        return Bot._client.new_order(**params)

    @staticmethod
    def take_longed_profit(stop_price=None):
        params = {
            "symbol": Bot.symbol.capitalize(),
            "side": Bot._sell,
            "type": "TAKE_PROFIT_MARKET",
            "timeInForce": "GTE_GTC",
            "recvWindow": Bot._recvWindow,
            "closePosition": True,
            "stopPrice": stop_price
        }
        return Bot._client.new_order(**params)

    @staticmethod
    def stop_shorted_loss(stop_price=None):
        stop_loss = {
            "symbol": Bot.symbol.capitalize(),
            "side": Bot._buy,
            "type": "STOP_MARKET",
            "timeInForce": "GTE_GTC",
            "recvWindow": Bot._recvWindow,
            "closePosition": True,
            "stopPrice": stop_price
        }
        return Bot._client.new_order(**stop_loss)

    @staticmethod
    def stop_longed_loss(stop_price=None):
        stop_loss = {
            "symbol": "ETHUSDT",
            "side": Bot._sell,
            "type": "STOP_MARKET",
            "timeInForce": "GTE_GTC",
            "recvWindow": Bot._recvWindow,
            "closePosition": True,
            "stopPrice": stop_price
        }
        return Bot._client.new_order(**stop_loss)

    @staticmethod
    async def get_position():
        positions = Bot._client.account(recvWindow=Bot._recvWindow)["positions"]
        return positions

    @staticmethod
    def get_prev_data():
        return Bot._client.continuous_klines(Bot.symbol.capitalize(), "PERPETUAL", "1m")

    @staticmethod
    async def has_position():
        positions = await Bot.get_position()
        return float(list(filter(Bot.position_filter, positions))[0].get("initialMargin")) != 0

    @staticmethod
    async def get_entry_price():
        gotten_pos = await Bot.get_position()
        position = list(filter(Bot.position_filter, gotten_pos))[0]
        return float(position.get("entryPrice"))

    @staticmethod
    def get_daily_target():
        Bot._daily_target = Bot._balance * 2
        return Bot._daily_target

    @staticmethod
    def position_filter(x):
        if x.get('symbol') == Bot.symbol:
            return True
        else:
            return False

    @staticmethod
    def get_last_trade():
        income = Bot._client.get_account_trades(recvWindow=Bot._recvWindow, symbol=Bot.symbol, )[-1]
        profit = float(income['realizedPnl'])
        commission = float(income['commission'])
        trade = {
            "balance": Bot._balance,
            "successful": True if profit > 0 else False,
            "income": profit,
            "commission": commission
        }
        Bot.trades.append(trade)


def long_stop_price(balance, qty, entry, percentage):
    total_cost = qty * entry
    gain_or_loss = balance * percentage
    gain_cost = total_cost + gain_or_loss
    stop_price = gain_cost / qty
    return stop_price


def short_stop_price(balance, qty, entry, percentage):
    total_cost = qty * entry
    gain_or_loss = balance * percentage
    gain_cost = total_cost - gain_or_loss
    stop_price = gain_cost / qty
    return stop_price
