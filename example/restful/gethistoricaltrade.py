from huobi import RequestClient


request_client = RequestClient()
trade_list = request_client.get_best_quote("btcusdt")#get_historical_trade("btcusdt", 5)
print(trade_list.ask_price)
print(trade_list.bid_price)
for trade in trade_list:
    trade.print_object()
    print()
