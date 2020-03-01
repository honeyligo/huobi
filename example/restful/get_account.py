from huobi import RequestClient
from huobi.constant.test import *
from huobi.base.printobject import *
from huobi.model import Account

request_client = RequestClient(url="https://api-aws.huobi.pro",api_key=g_api_key, secret_key=g_secret_key)
account_balance_list = request_client.get_account_balance()
if account_balance_list and len(account_balance_list):
    for account in account_balance_list:
        if account.account_type == "spot" or account.account_type == "SPOT":
            if  account.balances and len(account.balances):
                for balance in account.balances:
                    if balance.balance > 0.0 and balance.currency == 'usdt':
                        print("\tBalance Currency", balance.currency)
                        print("\tBalance Type", balance.balance_type)
                        print("\tBalance", balance.balance)


