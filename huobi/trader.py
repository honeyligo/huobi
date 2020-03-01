from huobi import RequestClient
from huobi.constant.test import *
from huobi.constant.trade_opt import *
from huobi.model import *
from huobi.status_thread import *
import queue
import time
import datetime

class Trader():
    def __init__(self, logger, wechat):
        self.logger = logger
        self.api = RequestClient(url="https://api-aws.huobi.pro", api_key=g_api_key, secret_key=g_secret_key)
        self.buy_price = 7314
        self.profit = 100
        self.init_balance = 1.257
        self.update_interval = 6 * 60
        self.avg_price = 0
        self.open_price = 0
        self.ask = 0
        self.bid = 0
        self.second_max = 0
        self.second_min = 0
        self.second_max_t = datetime.datetime.now()
        self.second_min_t = datetime.datetime.now()
        self.wechat = wechat
        self.orders = queue.Queue()
        self.status_thread = StatusThread(self.api, self.init_balance, self.orders, logger, wechat)
        self.status_thread.start()

    def get_float(self, f_str, n):
        f_str = str(f_str)
        a, b, c = f_str.partition('.')
        c = (c + "0" * n)[:n]
        tmp = ".".join([a, c])
        return float(tmp)

    def trade(self):
        self.update_candles()
        time.sleep(6)
        result = self.desicion()
        self.do_trade(result)

    def get_current_price(self, symbol="btcusdt"):
        return self.api.get_best_quote(symbol)

    def update_candles(self):
        ct = datetime.datetime.now()
        if self.ask > 0 and (ct - self.second_max_t).seconds < self.update_interval and (ct - self.second_min_t).seconds < self.update_interval:
            return

        candles = self.api.get_candlestick("btcusdt", CandlestickInterval.MIN60, 7)
        highs = [candle.high for candle in candles]
        lows = [candle.low for candle in candles]
        highs.sort()
        lows.sort()
        self.second_max = highs[-2]
        self.second_min = lows[1]
        self.logger.info("【更新】second_max：" + str(self.second_max))
        self.logger.info("【更新】second_min：" + str(self.second_min))

    def desicion(self, symbol="btcusdt"):
        current = self.get_current_price(symbol)
        self.ask = current.ask_price #卖1
        self.bid = current.bid_price #买1
        self.logger.info("买1：" + str(self.bid))
        self.logger.info("卖1：" + str(self.ask))

        if self.ask >= self.second_max and self.ask - self.buy_price > self.profit:
            return TradeOpt.Sell
        elif self.bid <= self.second_min:
            return TradeOpt.Buy
        return TradeOpt.Hold


    def do_trade(self, opt, symbol="btcusdt"):
        if opt == TradeOpt.Hold:
            return

        if opt == TradeOpt.Sell:
            position = self.api.get_position()
            position = self.get_float(position, 2)
            self.wechat.send_message("【决策】：卖出\n")
            if position <= 0.01:
                self.wechat.send_message("仓位不足:" + str(position))
                return

            order = self.api.create_order(symbol=symbol, account_type=AccountType.SPOT, order_type=OrderType.SELL_LIMIT,
                                          amount=position, price=self.ask)
            message = "【新建订单】\n 方向：卖出\n 数量：{0}\n 价格：{1}".format(position, self.ask)
            self.wechat.send_message(message)
            self.orders.put(order)
        else:
            self.wechat.send_message("【决策】：买入\n")
            cash = self.api.get_cash()
            if cash < 20:
                self.wechat.send_message("现金不足:" + str(cash))
                return

            amount = cash / self.bid
            amount = self.get_float(amount, 2)
            order = self.api.create_order(symbol=symbol, account_type=AccountType.SPOT, order_type=OrderType.BUY_LIMIT,
                                          amount=amount, price=self.bid)
            self.buy_price = self.bid

            message = "【新建订单】\n 方向：买入\n 数量：{0}\n 价格：{1}".format(amount, self.bid)
            self.wechat.send_message(message)

            self.orders.put(order)

