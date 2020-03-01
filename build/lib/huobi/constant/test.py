import os
if(os.path.exists("huobi/privateconfig.py")):
    from huobi.privateconfig import *
    g_api_key = p_api_key
    g_secret_key = p_secret_key
else:
    g_api_key = "6378d7c8-82964b1e-caa4a6c3-dbuqg6hkte"
    g_secret_key = "53ecbc54-b8b802e0-64ca93f5-8e187"

g_account_id = 12345678



