import db

def add_item(user_id, image, description):
    sql = """INSERT INTO Items(user_id, images, description) VALUES(?, ?, ?)"""
    db.execute(sql, [user_id, image, description])

def get_images():
    sql = "SELECT id, images FROM Items ORDER BY id DESC"
    return db.query(sql)

def get_items():
    sql = "SELECT id, description FROM Items ORDER BY id DESC"
    return db.query(sql)

def get_image(item_id):
    sql = "SELECT images FROM Items WHERE id = ?"
    result = db.query(sql, [item_id])    
    return result[0]["images"]

def get_item(item_id):
    sql = """SELECT Items.id, Items.description,
                    Users.username
             FROM Items, Users
             WHERE Items.user_id = Users.id AND
                   Items.id = ?"""
    return db.query(sql, [item_id])[0]