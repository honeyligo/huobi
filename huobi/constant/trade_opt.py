# coding: utf-8


from enum import Enum, unique

@unique
class TradeOpt(Enum):
    Hold = 0
    Buy = 1
    Sell = 2