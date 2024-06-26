
from huobi.impl.utils.timeservice import convert_cst_in_millisecond_to_utc
from huobi.model import *


class OrderDetailRequest:
    """
    The order update received by subscription of order update.

    :member
        symbol: The symbol you subscribed.
        timestamp: The UNIX formatted timestamp generated by server in UTC.
        topic : request topic
        client_req_id : client request id
        data: The order detail.

    """

    def __init__(self):
        self.symbol = ""
        self.timestamp = 0
        self.topic = ""
        self.client_req_id = ""
        self.data = Order()

    @staticmethod
    def json_parse(json_data, account_id_type_map):
        req_obj = OrderDetailRequest()
        req_obj.timestamp = convert_cst_in_millisecond_to_utc(json_data.get_int("ts"))
        req_obj.client_req_id = json_data.get_string("cid")
        req_obj.topic = json_data.get_string("topic")
        order_json = json_data.get_object("data")

        account_id = order_json.get_int("account-id")
        account_type = AccountType.INVALID
        if account_id in account_id_type_map:
            account_type = account_id_type_map[account_id]

        order_obj = Order.json_parse(order_json, account_type)
        req_obj.symbol = order_obj.symbol
        req_obj.data = order_obj

        return req_obj

    def print_object(self, format_data=""):
        from huobi.base.printobject import PrintBasic
        PrintBasic.print_basic(self.symbol, "Symbol")
        PrintBasic.print_basic(self.timestamp, "Timestamp")
        PrintBasic.print_basic(self.client_req_id, "Client Req ID")
        PrintBasic.print_basic(self.topic, "Topic")
        print("order detail as below :")
        self.data.print_object()

