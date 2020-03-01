

class ResultObj():
    def __init__(self):
        self.buySetupIndex=0                                 #Counting for buy setup
        self.sellSetupIndex=0                                #Counting for sell setup
        self.buyCoundownIndex=0                              #Counting for buy countdown
        self.sellCoundownIndex=0                             #Counting for sell countdown

        self.countdownIndexIsEqualToPreviousElement=True     #Indicates that the countdown index on item i is the same as i-1

        self.sellSetup=False                           #Indicates Sell setup happened
        self.buySetup=False                                  #Indicates Buy setup happened
        self.sellSetupPerfection=False                       #Indicates a perfect Sell Setup
        self.buySetupPerfection=False                        #Indicates a perfect Buy Setup

        self.bearishFlip=False                               #Indicates a bearish flip happened
        self.bullishFlip=False                               #Indicates a bullish flip happened

        self.TDSTBuy=0                                       #highest high(usually the high of bar 1) for a buy setup
        self.TDSTSell=0                                      #the lowest low(usually the low of bar 1) for sell setup
        self.countdownResetForTDST=False                      #Indicates the countdown got reset due to observing TDST
