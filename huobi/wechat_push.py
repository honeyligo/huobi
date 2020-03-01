from __future__ import unicode_literals
from threading import Timer
from wxpy import *
import requests
import random


class wechat_bot(object):
    def __init__(self):
        self.bot = Bot(console_qr=True)


    # linux执行登陆请调用下面的这句
    # bot = Bot(console_qr=2,cache_path="botoo.pkl")

    def send_message(self, message):
        try:
            # 你朋友的微信名称，不是备注，也不是微信帐号。
            my_friend = self.bot.friends().search('李斌')[0]
            my_friend.send(message)
        except:
            pass


if __name__ == "__main__":
    bot = wechat_bot()
    cash = 10
    bot.send_message("现金不足:" + str(cash))
