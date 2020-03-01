from huobi import RequestClient
from huobi.constant.test import *
from huobi.constant.trade_opt import *
from huobi.model import *
from huobi.status_thread import *
from huobi.result_obj import ResultObj
import queue
import time


class Td():
    def __init__(self, logger, wechat):
        self.logger = logger
        self.api = RequestClient(url="https://api-aws.huobi.pro", api_key=g_api_key, secret_key=g_secret_key)
        self.buy_price = 7314
        self.profit = 300
        self.init_balance = 1.257
        self.update_interval = 6 * 60
        self.avg_price = 0
        self.open_price = 0
        self.ask = 0
        self.bid = 0
        self.wechat = wechat

        self.lastTd = None
        self.resetCountdownOnTDST = True
        self.resetSetupCounterAfterCountdownHit13 = True
        self.result = list()

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
        time.sleep(300)
        opt = self.desicion()

        #self.do_trade(opt)

    def get_current_price(self, symbol="btcusdt"):
        return self.api.get_best_quote(symbol)

    def update_candles(self):
        candles = self.api.get_candlestick("btcusdt", CandlestickInterval.HOUR4, 200)
        self.calc_td(candles)

        self.logger.info("td buy seq:==>")
        i = 0
        for item in self.result[-24:]:
            self.logger.info(str(i) +":" + str(item.buySetupIndex))
            #self.logger.info(str(i) +":" + str(item.buyCoundownIndex))
            #self.logger.info(str(i) +":" + str(item.buySetup))
            #self.logger.info(str(i) +":" + str(item.buySetupPerfection))
            i += 1

        self.logger.info("td sell seq:==>")
        i = 0
        for item in self.result[-24:]:
            self.logger.info(str(i) + ":" + str(item.sellSetupIndex))
            #self.logger.info(str(i) + ":" + str(item.sellCoundownIndex))
            #self.logger.info(str(i) + ":" + str(item.sellSetup))
            #self.logger.info(str(i) + ":" + str(item.sellSetupPerfection))
            i += 1



    def desicion(self, symbol="btcusdt"):
        current = self.get_current_price(symbol)
        self.ask = current.ask_price #卖1
        self.bid = current.bid_price #买1

        last_second = self.result[-2]
        self.lastTd = self.result[-1]

        td_buy = (last_second.buySetup == False and last_second.buySetupPerfection == False) \
                 and (self.lastTd.buySetupPerfection and self.lastTd.buySetup
                      and (self.lastTd.buySetupIndex == 9 or self.lastTd.buySetupIndex == 13))
        td_sell = (last_second.sellSetup == False and last_second.sellSetupPerfection == False) \
                 and (self.lastTd.sellSetupPerfection and self.lastTd.sellSetup
                      and (self.lastTd.sellSetupIndex == 9 or self.lastTd.sellSetupIndex == 13))

        self.logger.info("买1：" + str(self.bid))
        self.logger.info("卖1：" + str(self.ask))
        self.logger.info("td_buy：" + str(td_buy))
        self.logger.info("td_sell：" + str(td_sell))

        if td_sell and self.ask - self.buy_price > self.profit:
            return TradeOpt.Sell
        elif td_buy:
            return TradeOpt.Buy
        return TradeOpt.Hold


    def do_trade(self, opt, symbol="btcusdt"):
        if opt == TradeOpt.Hold:
            return

        if opt == TradeOpt.Sell:
            position = self.api.get_position()
            position = self.get_float(position, 2)
            msg = "【状态】卖出TD序列值达标：{0}\n 是否达到最优：{1}\n 【决策】：卖出\n".format(self.lastTd.sellSetup, self.lastTd.sellSetupPerfection)
            self.wechat.send_message(msg)
            if position <= 0.01:
                self.wechat.send_message("仓位不足:" + str(position))
                return

            order = self.api.create_order(symbol=symbol, account_type=AccountType.SPOT, order_type=OrderType.SELL_LIMIT,
                                          amount=position, price=self.ask)
            message = "【新建订单】\n 方向：卖出\n 数量：{0}\n 价格：{1}".format(position, self.ask)
            self.wechat.send_message(message)
            self.orders.put(order)
        else:
            msg = "【状态】买入TD序列值达标：{0}\n 是否达到最优：{1}\n 【决策】：买入\n".format(self.lastTd.buySetup,
                                                                      self.lastTd.buySetupPerfection)
            self.wechat.send_message(msg)
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


    def calc_td(self, ohlc):
        i = 0
        ohlc.reverse()
        for item in ohlc:
            self.logger.info(ohlc[i].close)
            resultObj = ResultObj()
            if i >= 5:
                resultObj.sellCoundownIndex = self.result[i - 1].sellCoundownIndex
                resultObj.buyCoundownIndex = self.result[i - 1].buyCoundownIndex
                resultObj.sellSetup = self.result[i - 1].sellSetup
                resultObj.buySetup = self.result[i - 1].buySetup
                resultObj.TDSTBuy = self.result[i - 1].TDSTBuy
                resultObj.TDSTSell = self.result[i - 1].TDSTSell
                resultObj.sellSetupPerfection = self.result[i - 1].sellSetupPerfection
                resultObj.buySetupPerfection = self.result[i - 1].buySetupPerfection

                closeLessThanCloseOf4BarsEarlier = ohlc[i].close < ohlc[i - 4].close
                closeGreaterThanCloseOf4BarsEarlier = ohlc[i].close > ohlc[i - 4].close

                resultObj.bearishFlip = ohlc[i - 1].close > ohlc[i - 5].close and closeLessThanCloseOf4BarsEarlier
                resultObj.bullishFlip = ohlc[i - 1].close < ohlc[i - 5].close and closeGreaterThanCloseOf4BarsEarlier

                if (resultObj.bearishFlip or (self.result[i - 1].buySetupIndex > 0 and closeLessThanCloseOf4BarsEarlier)):
                    resultObj.buySetupIndex = (self.result[i - 1].buySetupIndex + 1 - 1) % 9 + 1
                    resultObj.TDSTBuy = max(item.high, self.result[i - 1].TDSTBuy)

                elif (resultObj.bullishFlip or (self.result[i - 1].sellSetupIndex > 0 and closeGreaterThanCloseOf4BarsEarlier)):
                    resultObj.sellSetupIndex = (self.result[i - 1].sellSetupIndex + 1 - 1) % 9 + 1
                    resultObj.TDSTSell = min(item.low, self.result[i - 1].TDSTSell)

                if (resultObj.buySetupIndex == 9):
                    resultObj.buySetup = True
                    resultObj.sellSetup = False
                    resultObj.sellSetupPerfection = False

                    resultObj.buySetupPerfection = (ohlc[i - 1].low < ohlc[i - 3].low and ohlc[i - 1].low < ohlc[i - 2].low) or (
                    ohlc[i].low < ohlc[i - 3].low and ohlc[i].low < ohlc[i - 2].low)

                if (resultObj.sellSetupIndex == 9):
                    resultObj.sellSetup = True
                    resultObj.buySetup = False
                    resultObj.buySetupPerfection = False

                    resultObj.sellSetupPerfection = (ohlc[i - 1].high > ohlc[i - 3].high and ohlc[i - 1].high > ohlc[i - 2].high) or (
                        ohlc[i].high > ohlc[i - 3].high and ohlc[i].high > ohlc[i - 2].high)

                self.calculateTDBuyCountdown(self.result, resultObj, ohlc, item, i)
                self.calculateTDSellCountdown(self.result, resultObj, ohlc, item, i)

            self.result.append(resultObj)
            i += 1

    def calculateTDSellCountdown(self, result, resultObj, ohlc, item, i):
        if (result[i - 1].sellSetup and resultObj.buySetup) or (self.resetCountdownOnTDST and item.close < result[i - 1].TDSTSell):
            resultObj.sellCoundownIndex = 0
            resultObj.countdownResetForTDST = True
        elif resultObj.sellSetup:
            if item.close > ohlc[i - 2].high:
                resultObj.sellCoundownIndex = (result[i - 1].sellCoundownIndex + 1 - 1) % 13 + 1
                resultObj.countdownIndexIsEqualToPreviousElement = False

        if (resultObj.sellCoundownIndex == 13 and result[i - 1].sellCoundownIndex == 13):
            resultObj.sellCoundownIndex = 0

        if (self.resetSetupCounterAfterCountdownHit13 and (resultObj.sellCoundownIndex == 13 and resultObj.sellSetupIndex > 0)):
            resultObj.sellSetupIndex = 1

        if (resultObj.sellCoundownIndex != 13 and result[i - 1].sellCoundownIndex == 13):
            resultObj.sellSetup = False
            resultObj.sellSetupPerfection = False
            resultObj.sellCoundownIndex = 0

    def calculateTDBuyCountdown(self, result, resultObj, ohlc, item, i):
        if (result[i - 1].buySetup and resultObj.sellSetup) or (self.resetCountdownOnTDST and item.close > result[i - 1].TDSTBuy):
            resultObj.buyCoundownIndex = 0
            resultObj.countdownResetForTDST = True
        elif resultObj.buySetup:
            if item.close < ohlc[i - 2].low:
                resultObj.buyCoundownIndex = (result[i - 1].buyCoundownIndex + 1 - 1) % 13 + 1
                resultObj.countdownIndexIsEqualToPreviousElement = False

        if (resultObj.buyCoundownIndex == 13 and result[i - 1].buyCoundownIndex == 13):
            resultObj.buyCoundownIndex = 0

        if (self.resetSetupCounterAfterCountdownHit13 and (resultObj.buyCoundownIndex == 13 and resultObj.buySetupIndex > 0)):
            resultObj.buySetupIndex = 1

        if (resultObj.buyCoundownIndex != 13 and result[i - 1].buyCoundownIndex ==13):
            resultObj.buySetup = False
            resultObj.buySetupPerfection = False
            resultObj.buyCoundownIndex = 0

