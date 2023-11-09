import requests
from urllib.parse import urljoin


class Order:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "order/")

    def new_order_cancel(self, user_id: str, order_id: str):
        json = {
            "user_id": user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "new_order_cancel")
        r = requests.post(url, json=json)
        return r.status_code

    def check_order(self, user_id: str):
        json = {
            "user_id": user_id
        }
        url = urljoin(self.url_prefix, "check_order")
        r = requests.post(url, json=json)
        return r.status_code



#
# import requests
# from urllib.parse import urljoin
#
# class Order:
#     def __init__(self, url_prefix, user_id, password):
#         self.url_prefix = urljoin(url_prefix, "order/")
#         self.user_id = user_id
#         self.password = password
#         self.token = ""
#         self.terminal = "my terminal"
#
#     # def create_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
#     #     books = []
#     #     for id_count_pair in book_id_and_count:
#     #         books.append({"id": id_count_pair[0], "count": id_count_pair[1})
#     #     json = {"user_id": self.user_id, "store_id": store_id, "books": books}
#     #     url = urljoin(self.url_prefix, "create_order")
#     #     headers = {"token": self.token}
#     #     r = requests.post(url, headers=headers, json=json)
#     #     response_json = r.json()
#     #     return r.status_code, response_json.get("order_id")
#
#     def cancel_order(self, order_id: str) -> int:
#         json = {"user_id": self.user_id, "order_id": order_id}
#         url = urljoin(self.url_prefix, "cancel_order")
#         headers = {"token": self.token}
#         r = requests.post(url, headers=headers, json=json)
#         # r = requests.post(url, json=json)
#         return r.status_code
#
#     def get_paid_orders(self) -> (int, list):
#         url = urljoin(self.url_prefix, "get_paid_orders?user_id=" + self.user_id)
#         headers = {"token": self.token}
#         r = requests.get(url, headers=headers)
#         response_json = r.json()
#         return r.status_code, response_json.get("orders")
#
#     def get_unpaid_orders(self) -> (int, list):
#         url = urljoin(self.url_prefix, "get_unpaid_orders?user_id=" + self.user_id)
#         headers = {"token": self.token}
#         r = requests.get(url, headers=headers)
#         response_json = r.json()
#         return r.status_code, response_json.get("orders")
