import db

def add_item(user_id, image, description, classes):
    sql = """INSERT INTO Items(user_id, images, description) VALUES(?, ?, ?)"""
    db.execute(sql, [user_id, image, description])

    item_id = db.last_insert_id()
    sql = "INSERT INTO Item_classes(item_id, title, value) VALUES(?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def get_all_classes():
    sql = "SELECT title, value FROM Classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
    return classes

def get_classes(item_id):
    sql = "SELECT title, value FROM Item_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_images():
    sql = "SELECT id, images FROM Items ORDER BY id DESC"
    return db.query(sql)

def get_items():
    sql = "SELECT id, description FROM Items ORDER BY id DESC"
    return db.query(sql)

def get_image(item_id):
    sql = "SELECT images FROM Items WHERE id = ?"
    result = db.query(sql, [item_id])    
    return result[0]["images"] if result else None

def get_item(item_id):
    sql = """SELECT Items.id, Items.description,
                    Users.username, Users.id user_id
             FROM Items, Users
             WHERE Items.user_id = Users.id AND
                   Items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, image, description):
    sql = """UPDATE Items SET images = ?,
                            description = ?
                        WHERE id = ?"""
    db.execute(sql, [image, description, item_id])

def remove_item(item_id):
    sql = "DELETE FROM Items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, images, description
            FROM Items
            WHERE description LIKE ?
            ORDER BY id DESC"""
    return db.query(sql, ["%" + query + "%"])