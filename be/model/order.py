import uuid
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


class Order:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    # 订单取消 增加余额 增加库存
    def new_order_cancel(self, user_id: str, order_id: str) -> (int, str):
        store_id = ""
        price = ""
        new_order = self.db.new_orders.find_one({"order_id": order_id})
        # 未支付订单取消：手动取消\自动取消
        # 手动取消
        if new_order is not None:
            buyer_id = new_order["user_id"]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            self.db.new_orders.delete_one({"order_id": order_id})

        # 如果已经支付的话需要取消订单以后减少商家余额，增加用户余额
        else:
            new_order_paid = self.db.new_order_paid.find_one({"order_id": order_id})
            if new_order_paid:
                buyer_id = new_order_paid["user_id"]

                if buyer_id != user_id:
                    return error.error_authorization_fail()
                # 找到对应商店和价格
                store_id = new_order_paid["store_id"]
                price = new_order_paid["price"]

                # 根据商店找到卖家
                user_store = self.db.user_stores.find_one({"store_id": store_id})

                seller_id = user_store["user_id"]

                # 减少卖家余额
                condition = {"$inc": {"balance": -price}}
                seller = {"user_id": seller_id}
                self.db.users.update_one(seller, condition)

                # 增加买家余额
                buyer = {"user_id": buyer_id}
                condition = {"$inc": {"balance": price}}
                self.db.used.update_one(buyer, condition)

                # 删除订单
                self.db.new_order_paid.delete_one({"order_id": order_id})

            else:
                return error.error_invalid_order_id(order_id)

            # 增加书籍库存
        orders = self.db.new_order_details.find({"order_id": order_id})
        for order in orders:
            book_id = order["book_id"]
            count = order["count"]
            store_book = {"store_id": store_id, "book_id": book_id}
            condition = {"$inc": {"stock_level": count}}
            result = self.db.stores.update_one(store_book, condition)

        return 200, "ok"

    # 查询历史订单
    def check_order(self, user_id: str):
        # 最后返回一个订单详情
        # his_order_detail = []

        user = self.db.users.find_one({"user_id": user_id})
        if user is None:
            return error.error_non_exist_user_id(user_id)

        # 查询历史订单分为：查询未付款的订单、查询已经付款的订单
        # 查询未付款订单
        user = {"user_id": user_id}
        new_orders = self.db.new_order_details.find(user)
        if new_orders:
            # book_id = ""
            # count = ""
            # price = ""
            # status = ""

            for new_order in new_orders:
                order_id = new_order["order_id"]
                order = {"order_id": order_id}
                new_order_details = self.db.new_order_details.find(order)

                if new_order_details is None:
                    # for new_order_detail in new_order_details:
                    #     # 保存书的详细信息
                    #     book_id = new_order_detail["book_id"]
                    #     count = new_order_detail["count"]
                    #     price = new_order_detail["price"]
                    #     status = new_order_detail["books_status"]

                    return error.error_invalid_order_id(order_id)

                # details = {
                #     "status": status,
                #     "order_id": order_id,
                #     "buyer_id": new_order["user_id"],
                #     "store_id": new_order["store_id"],
                #     "price": price,
                #     "book_id": book_id,
                #     "count": count,
                # }

                # his_order_detail.append(details)


        # 查询已付款订单
        new_orders_paid = self.db.new_order_paid.find(user)

        if new_orders_paid:
            # book_id = ""
            # count = ""
            # price = ""
            # status = ""
            for new_order_paid in new_orders_paid:
                order_id = new_order_paid["order_id"]
                order = {"order_id": order_id}
                new_order_details = self.db.new_order_details.find(order)
                if new_order_details is None:
                    # for new_order_detail in new_order_details:
                        # 保存书的详细信息
                        # book_id = new_order_detail["book_id"]
                        # count = new_order_detail["count"]
                        # price = new_order_detail["price"]
                        # status = new_order_detail["books_status"]


                    return error.error_invalid_order_id(order_id)

                # details = {
                #     "status": status,
                #     "order_id": order_id,
                #     "buyer_id": new_order_paid["user_id"],
                #     "store_id": new_order_paid["store_id"],
                #     "total_price": new_order_paid["price"],
                #     "price": price,
                #     "book_id": book_id,
                #     "count": count,
                # }
                # his_order_detail.append(details)

        return 200, "ok"

    def check_order_status(self):
        timeout_datetime = datetime.now() - timedelta(seconds = 5)
        condition = {"order_time": {"$lte": timeout_datetime}} # 表示小于超时时间戳都应该被取消
        orders = self.db.new_orders.find(condition)
        if orders is not None:
            for order in orders:
                order_id = order["order_id"]
                self.db.new_orders.delete_one({"order_id": order_id})

        return 200, "ok"


b = Order()
scheduler = BackgroundScheduler()
scheduler.add_job(b.check_order_status, 'interval',  seconds=5)
scheduler.start()
#
# import requests
# from urllib.parse import urljoin
# import logging
# import uuid
# from be.model import error
# from be.model import db_conn
# from pymongo import MongoClient
# from datetime import datetime, timedelta
#
# #订单状态，订单查询和取消定单
# #取消定单可由买家主动地取消定单，或者买家下单后，经过一段时间超时仍未付款，定单也会自动取消
#
#
# class Order(db_conn.DBConn):
#     def __init__(self):
#         super().__init__()
#
#     # 获取已付款订单历史
#     def get_paid_order_history(self, user_id):
#         try:
#             # 查询用户的已付款订单
#             paid_order_history = self.db.db.new_order.find({"user_id": user_id, "status": {"$in": [2, 3, 4]}})
#             orders = []
#
#             for order in paid_order_history:
#                 order_id = order["order_id"]
#                 order_details = self.db.db.new_order_detail.find({"order_id": order_id})
#                 order_info = {
#                     "order_id": order_id,
#                     "store_id": order["store_id"],
#                     "order_details": []
#                 }
#
#                 for detail in order_details:
#                     book_id = detail["book_id"]
#                     count = detail["count"]
#                     price = detail["price"]
#                     order_info["order_details"].append({
#                         "book_id": book_id,
#                         "count": count,
#                         "price": price
#                     })
#
#                 orders.append(order_info)
#
#             return 200, "OK", orders
#
#         except Exception as e:
#             logging.error("错误: {}".format(str(e)))
#             return 500, "Internal Server Error", []
#
#     # 获取未付款订单历史
#     def get_unpaid_order_history(self, user_id):
#         try:
#             # 查询用户的未付款订单
#             unpaid_order_history = self.db.db.new_order.find({"user_id": user_id, "status": 1})
#             orders = []
#
#             for order in unpaid_order_history:
#                 order_id = order["order_id"]
#                 order_details = self.db.db.new_order_detail.find({"order_id": order_id})
#                 order_info = {
#                     "order_id": order_id,
#                     "store_id": order["store_id"],
#                     "order_details": []
#                 }
#
#                 for detail in order_details:
#                     book_id = detail["book_id"]
#                     count = detail["count"]
#                     price = detail["price"]
#                     order_info["order_details"].append({
#                         "book_id": book_id,
#                         "count": count,
#                         "price": price
#                     })
#
#                 orders.append(order_info)
#
#             return 200, "OK", orders
#
#         except Exception as e:
#             logging.error("错误: {}".format(str(e)))
#             return 500, "Internal Server Error", []
#
#     # 取消订单
#     def cancel_order(self, user_id, order_id):
#         try:
#             # 查询订单
#             order_data = self.db.db.new_order.find_one({"order_id": order_id})
#             if order_data is None:
#                 return error.error_invalid_order_id(order_id)
#
#             buyer_id = order_data["user_id"]
#
#             # 检查用户是否有取消订单的权限
#             if buyer_id != user_id:
#                 return error.error_authorization_fail()
#
#             # 检查订单是否已经支付
#             if self.is_order_paid(order_id):
#                 return error.error_order_already_paid(order_id)
#
#             # 删除订单及其详情
#             self.db.db.new_order.delete_one({"order_id": order_id})
#             self.db.db.new_order_detail.delete_many({"order_id": order_id})
#
#             return 200, "OK"
#
#         except Exception as e:
#             logging.error("错误: {}".format(str(e)))
#             return 500, "Internal Server Error"
#
#     # 检查订单是否已支付
#     def is_order_paid(self, order_id):
#         order_data = self.db.db.new_order.find_one({"order_id": order_id})
#         if order_data is not None:
#             order_time = order_data["order_time"]
#             current_time = datetime.datetime.now()
#             # 定义超时阈值（例如，1分钟）
#             timeout_threshold = datetime.timedelta(minutes=1)
#             return (current_time - order_time) > timeout_threshold
#         return False
#
#     # 自动取消未支付订单
#     def auto_cancel_orders(self):
#         try:
#             # 查询未支付订单
#             unpaid_orders = self.db.db.new_order.find({"status": 1})
#             current_time = datetime.datetime.now()
#
#             for order in unpaid_orders:
#                 order_id = order["order_id"]
#                 order_time = order["order_time"]
#
#                 # 定义超时阈值（例如，1分钟）
#                 timeout_threshold = datetime.timedelta(minutes=1)
#
#                 if (current_time - order_time) > timeout_threshold:
#                     # 取消订单
#                     self.cancel_order(order["user_id"], order_id)
#
#         except Exception as e:
#             logging.error("错误: {}".format(str(e)))
#
# # 初始化Order类并启动自动取消未支付订单的过程
# if __name__ == "__main__":
#     order_handler = Order()
#     order_handler.auto_cancel_orders()
