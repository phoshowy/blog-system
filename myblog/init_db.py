import sqlite3

# 创建数据库链接
connection = sqlite3.connect('database.db')

# 执行db.sql中的SQL语句
with open('db.sql') as f:
    connection.executescript(f.read())

# 创建一个执行句柄，用来执行后面的语句
cur = connection.cursor()
# 插入两条文章


cur.execute("INSERT INTO comments (id,content) VALUES (?,?)",
           ('3','test3')
            )
cur.execute("INSERT INTO posts_other (title, content,brief,tag) VALUES (?, ?,?,?)",
            ('test1', '1111111111111111111111111111111111111111111111111111111111','brief1aaaaaaaa','test1')
            )

cur.execute("INSERT INTO posts (title, content,brief,tag) VALUES (?, ?,?,?)",
            ('test2', '2222222222222222222222222222222222222222222222222222222222','brief1aaaaaaaa','test2')
            )

# cur.execute("INSERT INTO users (user_name,password,role) VALUES (?,?,?)",
#             ('admin','admin','admin')
#             )
# cur.execute("INSERT INTO users (user_name,password,role) VALUES (?,?,?)",
#             ('user1','user1','user1')
#             )
# cur.execute("INSERT INTO users (user_name,password,role) VALUES (?,?,?)",
#             ('test','test','test')
#             )
# 提交前面的数据操作
connection.commit()

# 关闭链接
connection.close()
