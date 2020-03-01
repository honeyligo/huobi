from huobi.constant.result import OutputKey
from huobi.impl.utils import *
from huobi.impl.utils.channelparser import ChannelParser
from huobi.model.constant import *
from huobi.model.candlestick import Candlestick


class CandlestickRequest:
    """
    The candlestick/kline data received by subscription of candlestick/kline.

    :member
        symbol: the symbol you subscribed.
        timestamp: the UNIX formatted timestamp generated by server in UTC.
        interval: candlestick/kline interval you subscribed.
        data: the data of candlestick/kline.

    """

    def __init__(self):
        self.symbol = ""
        self.timestamp = 0
        self.interval = CandlestickInterval.INVALID
        self.data = list()

    @staticmethod
    def json_parse(json_wrapper):
        ch = json_wrapper.get_string(OutputKey.KeyChannelRep)
        parse = ChannelParser(ch)
        candlestick_event = CandlestickRequest()
        candlestick_event.symbol = parse.symbol
        candlestick_event.interval = ""
        tick = json_wrapper.get_array(OutputKey.KeyData)
        candlestick_list = list()
        for item in tick.get_items():
            data = Candlestick.json_parse(item)
            candlestick_list.append(data)

        candlestick_event.data = candlestick_list
        return candlestick_event
