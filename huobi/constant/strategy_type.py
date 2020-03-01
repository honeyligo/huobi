# coding: utf-8


from enum import Enum, unique

@unique
class StrategyType(Enum):
    SECOND = 0
    TWO_B = 1
    MACD = 2
    RSI = 3
    TD = 4