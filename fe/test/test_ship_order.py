import pytest
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid

class TestShipOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_ship_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_ship_order_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 2)
        self.order_id = "test_ship_order_order_id_{}".format(str(uuid.uuid1()))

        yield
        # do after test

    # def test_ok(self):
    #     for b in self.books:
    #         code = self.seller.add_book(self.store_id, 0, b)
    #         assert code == 200
    #
    #     # 创建订单并付款
    #     order_code = self.seller.new_order(self.store_id, self.order_id, self.books)
    #     assert order_code == 200
    #     pay_code = self.seller.pay_order(self.order_id)
    #     assert pay_code == 200
    #
    #     # 发货操作
    #     ship_code, message = self.seller.ship_order(self.order_id, self.store_id)
    #     assert ship_code == 200
    #     assert message == "Order {} has been shipped.".format(self.order_id)

    def test_error_non_exist_store_id(self):
        for b in self.books:
            # non exist store id
            code = self.seller.ship_order(self.order_id, self.store_id + "x")
            assert code != 200

    def test_error_invalid_order_id(self):
        for b in self.books:
            # invalid order id
            code = self.seller.ship_order(self.order_id + "x", self.store_id)
            assert code != 200

    # def test_error_invalid_order_status(self):
    #     for b in self.books:
    #         code = self.seller.add_book(self.store_id, 0, b)
    #         assert code == 200
    #
    #     # 创建订单但不付款
    #     order_code = self.seller.new_order(self.store_id, self.order_id, self.books)
    #     assert order_code == 200
    #
    #     # 发货操作，订单状态为1（已下单未付款），应该返回错误
    #     code = self.seller.ship_order(self.order_id, self.store_id)
    #     assert code != 200
# import pytest
# from fe.access.new_seller import register_new_seller
# from fe.access import book
# import uuid
# class TestShipOrder:
#     @pytest.fixture(autouse=True)
#     def pre_run_initialization(self):
#         # do before test
#         self.seller_id = "test_ship_order_seller_id_{}".format(str(uuid.uuid1()))
#         self.store_id = "test_ship_order_store_id_{}".format(str(uuid.uuid1()))
#         self.password = self.seller_id
#         self.seller = register_new_seller(self.seller_id, self.password)
#         code = self.seller.create_store(self.store_id)
#         assert code == 200
#         book_db = book.BookDB()
#         self.books = book_db.get_book_info(0, 2)
#         self.order_id = "test_ship_order_order_id_{}".format(str(uuid.uuid1()))
#
#         # 创建订单并付款
#         order_code = self.seller.new_order(self.store_id, self.order_id, self.books)
#         assert order_code == 200
#         pay_code = self.seller.pay_order(self.order_id)
#         assert pay_code == 200
#
#         yield
#         # do after test
#
#     def test_error_invalid_order_status(self):
#         for b in self.books:
#             code = self.seller.add_book(self.store_id, 0, b)
#             assert code == 200
#
#         # 发货操作，订单状态为1（已下单未付款），应该返回错误
#         code, message = self.seller.ship_order(self.order_id, self.store_id)
#         assert code != 200
#         assert "error_invalid_order_status" in message
