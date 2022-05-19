from typing import Awaitable

from binance.futures import Futures

class Bot:

    _precision: int
    percent_loss: float
    position: bool
    percent_profit: float
    _balance: float
    _daily_target: float
    _recvWindow: int
    _leverage: int
    symbol: str
    base_url: str
    _sell: str
    _buy: str
    _secret_key: str
    _api_key: str
    _client: Futures
    _asset_precision: int
    _starting_capital: int
    trades: list
    current_signal: dict
    prev_signal: str

    @staticmethod
    def place_long_order(initial_margin: float, quantity: float):
        pass

    @staticmethod
    def place_short_order(initial_margin: float, quantity: float):
        pass

    @staticmethod
    def init() -> Futures: pass

    @staticmethod
    def get_signal(rsi_10: float) -> str: pass

    @staticmethod
    def implement_strategy(current_price: float, rsi_10: float) -> Awaitable: pass

    @staticmethod
    def get_assets() -> list: pass

    @staticmethod
    def get_balance() -> float:
        pass

    @staticmethod
    def get_position():
        pass

    @staticmethod
    def get_entry_price():
        pass

    @staticmethod
    def buy(quantity: float):
        pass

    @staticmethod
    def take_longed_profit(stop_price: float) -> dict:
        pass

    @staticmethod
    def stop_longed_loss(stop_price: float) -> dict:
        pass

    @staticmethod
    def sell(quantity):
        pass

    @staticmethod
    def take_shorted_profit(stop_price: float) -> dict:
        pass

    @staticmethod
    def stop_shorted_loss(stop_price: float)-> dict:
        pass

    @staticmethod
    def position_filter() -> bool:
        pass

    @staticmethod
    def has_position():
        pass

    @staticmethod
    def get_prev_data():
        pass

    @staticmethod
    def get_last_trade():
        pass

    @staticmethod
    def get_daily_target() -> float:
        pass