import jwt
import time
import logging
import pymongo  # 导入MongoDB库
from be.model import error
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 seconds

    def __init__(self, db_url, db_name):
        super().__init__(db_url, db_name)
        self.collection = self.conn['user']

    # ...
    #用户注册
    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            user_data = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            }
            self.collection.insert_one(user_data)
        except pymongo.errors.DuplicateKeyError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"


    #检查用户令牌的有效性，确保令牌与数据库中存储的一致，并且令牌在有效期内。
    def check_token(self, user_id: str, token: str) -> (int, str):
        user_data = self.collection.find_one({"user_id": user_id})
        if user_data is None:
            return error.error_authorization_fail()
        db_token = user_data["token"]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    #检查用户密码的有效性，验证提供的密码与数据库中存储的密码是否一致。
    def check_password(self, user_id: str, password: str) -> (int, str):
        user_data = self.collection.find_one({"user_id": user_id})
        if user_data is None:
            return error.error_authorization_fail()

        if password != user_data["password"]:
            return error.error_authorization_fail()

        return 200, "ok"

    #用户登录方法，检查用户密码
    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)

            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"token": token, "terminal": terminal}}
            )
        except sqlite.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    #用户登出方法
    def logout(self, user_id: str, token: str) -> (int, str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"token": dummy_token, "terminal": terminal}}
            )
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    #用户注销方法，从数据库中删除用户的信息，实现用户注销操作
    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.collection.delete_one({"user_id": user_id})
            if result.deleted_count == 1:
                return 200, "ok"
            else:
                return error.error_authorization_fail()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    #首先检查旧密码是否正确，然后生成新的 JWT 令牌，并将新密码、令牌和终端信息更新到 MongoDB 数据库中
    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            # 更新用户的密码、令牌和终端信息
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"password": new_password, "token": token, "terminal": terminal}}
            )

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e)), ""

        return 200, "ok"