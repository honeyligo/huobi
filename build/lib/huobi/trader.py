from huobi import RequestClient
from huobi.constant.test import *
from huobi.constant.trade_opt import *
from huobi.model import *

class Trader():
    def __init__(self, logger):
        self.logger = logger
        self.api = RequestClient(url="https://api-aws.huobi.pro", api_key=g_api_key, secret_key=g_secret_key)
        self.buy_price = 7314
        self.profit = 100
        self.avg_price = 0
        self.open_price = 0
        self.ask = 0
        self.bid = 0
        self.second_max = 0
        self.second_min = 0
        self.max = 0
        self.min = 0

    def trade(self):
        self.init_candles()
        result = self.desicion()
        self.do_trade(result)


    def get_current_price(self, symbol="btcusdt"):
        return self.api.get_best_quote(symbol)

    def update_second(self, high, low):
        if high > self.max:
            self.second_max = self.max
            self.max = high
        if low < self.min:
            self.second_min = self.min
            self.min = low

    def init_candles(self):
        candles = self.api.get_candlestick("btcusdt", CandlestickInterval.MIN60, 7)
        for candle in candles:
            high = candle.high
            low = candle.low
            if self.max == 0:
                self.max = high
                self.min = low
            self.update_second(high, low)


    def desicion(self, symbol="btcusdt"):
        current = self.get_current_price(symbol)
        self.ask = current.ask_price #卖1
        self.bid = current.bid_price #买1
        self.logger.info("买1：" + str(self.bid))
        self.logger.info("卖1：" + str(self.ask))

        self.update_second(self.bid, self.ask)
        print(self.second_max)
        print(self.second_min)

        if self.ask >= self.second_max and self.ask - self.buy_price > self.profit:
            return TradeOpt.Sell
        elif self.bid <= self.second_min:
            return TradeOpt.Buy
        return TradeOpt.Hold


    def do_trade(self, opt, symbol="btcusdt"):
        if opt == TradeOpt.Hold:
            return
        if opt == TradeOpt.Sell:
            position = self.get_position(symbol)
            if position <= 0.01:
                return
            order = self.api.create_order(symbol=symbol, account_type=AccountType.SPOT, order_type=OrderType.SELL_LIMIT,
                                          amount=position, price=self.ask)
            # cancel if failed
        else:
            # get cash
            cash = self.get_cash()
            amount = cash / self.bid
            order = self.api.create_order(symbol=symbol, account_type=AccountType.SPOT, order_type=OrderType.BUY_LIMIT,
                                          amount=amount, price=self.bid)
            self.buy_price = self.bid

    def get_position(self, symbol="btcusdt"):
        account_balance_list = self.api.get_account_balance()
        if account_balance_list and len(account_balance_list):
            for account in account_balance_list:
                if account.account_type == "spot" or account.account_type == "SPOT":
                    if account.balances and len(account.balances):
                        for balance in account.balances:
                            if balance.balance > 0.0 and balance.currency == symbol:
                                print("\tBalance Currency", balance.currency)
                                print("\tBalance Type", balance.balance_type)
                                print("\tBalance", balance.balance)
                                return balance.balance
        return 0

    def get_cash(self):
        return self.get_position("usdt")