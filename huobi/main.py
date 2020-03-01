import time
import logging
import os
import sys
from huobi.constant.strategy_type import StrategyType
from optparse import OptionParser
from huobi.trader import *
from huobi.twob import  *
from huobi.macd import  *
from huobi.td import *
from huobi.wechat_push import *

if __name__ == '__main__':
    prog_name = os.path.splitext(os.path.basename(__file__))[0]
    app_home = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
    log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")

    logger = logging.getLogger()
    file_name = "{0}.log".format(prog_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(log_format)
        logger.addHandler(stdout_handler)

        file_handler = logging.FileHandler(
            os.path.join(app_home, "log", file_name), "a+")
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    usage = "usage: %prog  [strategy]"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", help="debug", default=False)

    (options, args) = parser.parse_args()

    args0 = 0
    if len(args) != 1:
        sys.stderr.write("argument error. use -h or --help option\n")
        for i, j in enumerate(StrategyType):
            print("strategy {0}: {1}".format(i, j))
        sys.exit(1)
    else:
        args0 = int(args[0])

    logger.info("start...")

    wechat = wechat_bot()

    strategy = StrategyType(args0)

    trader = None
    if strategy == StrategyType.SECOND:
        trader = Trader(logger, wechat)
    elif strategy == StrategyType.MACD:
        trader = Macd(logger, wechat)
    elif strategy == StrategyType.TD:
        trader = Td(logger, wechat)
    elif strategy == StrategyType.TWO_B:
        trader = TwoB(logger, wechat)

    while(True):
        trader.trade()
        time.sleep(30)
