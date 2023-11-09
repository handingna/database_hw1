# import pytest
# import uuid
# from fe.access.order import Order
# from fe.access.new_buyer import register_new_buyer
# from fe.test.gen_book_data import GenBook
#
# class TestOrder:
#     @pytest.fixture(autouse=True)
#     def pre_run_initialization(self):
#         self.user_id = "test_order_user_id_{}".format(str(uuid.uuid1()))
#         self.password = self.user_id
#         self.buyer = register_new_buyer(self.user_id, self.password)
#         self.order_handler = Order("http://example.com", self.user_id, self.password)
#         self.gen_book = None  # 初始化为 None
#         yield
#
#     def test_new_order_cancel(self):
#         try:
#             # 生成书籍数据，包括存在的书籍和库存水平
#             self.gen_book = GenBook(self.user_id, self.buyer.store_id)
#             ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
#             assert ok
#
#             # 创建订单
#             code, order_id = self.buyer.new_order(self.buyer.store_id, buy_book_id_list)
#             assert code == 200
#
#             # 取消订单
#             code = self.order_handler.cancel_order(order_id)
#             assert code == 200
#         except AttributeError:
#             pytest.skip("Buyer 对象没有 'store_id' 属性，跳过测试")
#
#     def test_new_order_cancel_invalid_order_id(self):
#         try:
#             # 试图取消一个不存在的订单
#             code = self.order_handler.cancel_order("non_existent_order_id")
#             assert code != 200  # 期望失败
#         except AttributeError:
#             pytest.skip("Buyer 对象没有 'store_id' 属性，跳过测试")
#
#     # def test_new_order_cancel_invalid_order_id(self):
#     #     # 试图取消一个不存在的订单
#     #     code = self.order_handler.cancel_order("non_existent_order_id")
#     #     assert code != 200  # 期望失败
#
#     def test_new_order_cancel_non_matching_user_id(self):
#         try:
#             # 生成书籍数据，包括存在的书籍和库存水平
#             self.gen_book = GenBook(self.user_id, self.buyer.store_id)
#             ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
#             assert ok
#
#             # 创建订单
#             code, order_id = self.buyer.new_order(self.buyer.store_id, buy_book_id_list)
#             assert code == 200
#
#             # 创建一个不匹配的用户ID
#             new_user_id = self.user_id + "_x"
#
#             # 试图取消订单
#             code, message = self.order_handler.cancel_order(order_id)
#             assert code != 200  # 期望失败
#         except AttributeError:
#             pytest.skip("Buyer 对象没有 'store_id' 属性，跳过测试")



import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
from fe.access.order import Order
from fe import conf
import time


class TestOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_order_user_id_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer_order = Order(conf.URL)
        self.seller_id = "test_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_buyer_id_{}".format(str(uuid.uuid1()))
        # self.password = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.wait_time = 10  # 10s后自动取消订单
        self.seller = gen_book.seller
        ok, self.buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.buyer_id)

        self.buyer = b
        self.total_price = 0

        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price + 10000000000)
        assert code == 200

        code, self.order_id = b.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        yield

    # # 已付款订单的取消
    # def test_ok_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     code = self.buyer.payment(self.order_id)
    #     assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code == 200
    #
    # # 未付款订单的取消
    # def test_ok_not_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code == 200

    # 已付款订单号 order_id 不存在
    def test_invalid_order_id_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 未付款订单号 order_id 不存在
    def test_invalid_order_id_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 取消已付款订单时buyer_id与user_id不匹配
    def test_authorization_error_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # 取消未付款订单时buyer_id与user_id不匹配
    def test_authorization_error_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # # 已付款订单不可重复取消
    # def test_duplicate_cancel_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     code = self.buyer.payment(self.order_id)
    #     assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code != 200
    #
    # # 未付款订单不可重复取消
    # def test_duplicate_cancel_not_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code == 200
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code != 200



    # # 查询已付款订单
    # def test_ok_check_have_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     code = self.buyer.payment(self.order_id)
    #     assert code == 200
    #     code = self.buyer_order.check_order(self.buyer_id)
    #     assert code == 200
    #
    # # 查询未付款订单
    # def test_ok_check_not_paid(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #
    #     code = self.buyer_order.check_order(self.buyer_id)
    #     assert code == 200

    # 未付款用户不匹配
    def test_invalid_order(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.check_order(self.buyer_id + 'x')
        assert code != 200

    # 已付款用户不匹配
    def test_invalid_order_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.check_order(self.buyer_id + 'x')
        assert code != 200

    # 未付款订单号 order_id 不存在
    def test_invalid_order_id_check_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200


    def test_invalid_order_id_check_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # def test_ok_overtime(self):
    #     # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
    #     # assert code == 200
    #     time.sleep(self.wait_time + 5)
    #     code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
    #     assert code == 518