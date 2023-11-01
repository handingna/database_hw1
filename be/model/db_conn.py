from be.model.store import Store

class DBConn:
    def __init__(self):
        self.db = Store("mongodb://127.0.0.1:27017")

    def user_id_exist(self, user_id):
        # 在MongoDB中查找用户
        user = self.db.db.user.find_one({"user_id": user_id})
        return user is not None

    def book_id_exist(self, store_id, book_id):
        # 在MongoDB中查找书本
        book = self.db.db.store.find_one({"store_id": store_id, "book_id": book_id})
        return book is not None

    def store_id_exist(self, store_id):
        # 在MongoDB中查找商店
        store = self.db.db.user_store.find_one({"store_id": store_id})
        return store is not None

# from be.model import store
#
#
# class DBConn:
#     def __init__(self):
#         self.conn = store.get_db_conn()
#
#     def user_id_exist(self, user_id):
#         cursor = self.conn.execute(
#             "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def book_id_exist(self, store_id, book_id):
#         cursor = self.conn.execute(
#             "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
#             (store_id, book_id),
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def store_id_exist(self, store_id):
#         cursor = self.conn.execute(
#             "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
