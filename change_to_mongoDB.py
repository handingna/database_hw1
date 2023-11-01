import sqlite3
from pymongo import MongoClient

# 连接到SQLite数据库
sqlite_connection = sqlite3.connect('fe/data/book_lx.db')
sqlite_cursor = sqlite_connection.cursor()

# 连接到MongoDB数据库
mongo_client = MongoClient('mongodb://localhost:27017')  # 根据MongoDB的实际连接信息修改
mongo_db = mongo_client['bookstore']  # 指定MongoDB数据库名称
mongo_collection = mongo_db['books']  # 指定MongoDB数据集合名称

# 查询SQLite数据库中的书籍数据
sqlite_cursor.execute("SELECT * FROM book")
books_data = sqlite_cursor.fetchall()

# 将每本书的数据转换为MongoDB文档并插入MongoDB集合
for book in books_data:
    book_document = {
        "id": book[0],
        "title": book[1],
        "author": book[2],
        "publisher": book[3],
        "original_title": book[4],
        "translator": book[5],
        "pub_year": book[6],
        "pages": book[7],
        "price": book[8],
        "currency_unit": book[9],
        "binding": book[10],
        "isbn": book[11],
        "author_intro": book[12],
        "book_intro": book[13],
        "content": book[14],
        "tags": book[15],
        "picture": book[16],
    }
    mongo_collection.insert_one(book_document)

# 关闭连接
sqlite_connection.close()
mongo_client.close()

print("数据迁移完成")
