from huobi.trader import *
import time
import logging
import os
import sys

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

    logger.info("start...")
    trader = Trader(logger)

    while(True):
        trader.trade()
        time.sleep(30)
