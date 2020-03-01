import threading
import datetime
import time

class StatusThread(threading.Thread):
    def __init__(self, api, init_balance, orders, logger, wechat):
        super(StatusThread, self).__init__()

        self.api = api
        self.logger = logger
        self.wechat = wechat
        self.orders = orders
        self.init_balance = init_balance

    def prn_obj(self, obj):
        print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))

    def run(self):
        while True:
            while not self.orders.empty():
                try:
                    id = self.orders.get(False)  # False 如果队列为空，抛出异常
                    info = self.api.get_order("btcusdt", id)
                    #self.prn_obj(info)

                    if info.state == 'filled':
                        profit = self.api.get_profit(self.init_balance)
                        message = "【订单成交】\n订单号:{0}\n方向:{1}\n价格:{2}\n数量:{3}\n总盈利:{4}"\
                            .format(id, info.order_type, info.price, info.amount, profit)
                        self.wechat.send_message(message)
                    else:
                        self.orders.put(id)
                except Exception as e:
                    pass

            time.sleep(6)


