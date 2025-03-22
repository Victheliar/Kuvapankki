import db

def add_item(description, user_id):
    sql = """INSERT INTO Items (description, user_id) VALUES (?, ?)"""
    db.execute(sql, [description, user_id])

def get_items():
    sql = "SELECT id, description FROM Items ORDER BY id DESC"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT Items.description,
                    Users.username
             FROM Items, Users
             WHERE Items.user_id = Users.id AND
                   Items.id = ?"""
    return db.query(sql, [item_id])[0]