import db

def add_item(description, user_id, image, category):
    sql = """INSERT INTO Items(description, user_id, images, category) VALUES(?, ?, ?, ?)"""
    db.execute(sql, [description, user_id, image, category])

# def get_items():
#     sql = "SELECT id, images, description, category FROM Items ORDER BY id DESC"
#     return db.query(sql)

# def get_item(item_id):
#     sql = """SELECT Items.description,
#                     Items.images,
#                     Users.username
#              FROM Items, Users
#              WHERE Items.user_id = Users.id AND
#                    Items.id = ?"""
#     return db.query(sql, [item_id])[0]