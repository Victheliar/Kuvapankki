import db

def item_count():
    sql = "SELECT COUNT(*) FROM Items"
    return db.query(sql)[0][0]

def add_item(user_id, image, description, classes):

    sql = """INSERT INTO Items(user_id, images, description) VALUES(?, ?, ?)"""
    db.execute(sql, [user_id, image, description])

    item_id = db.last_insert_id()

    sql = "INSERT INTO Item_classes(item_id, title, value) VALUES(?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def add_comment(item_id, user_id, comment):
    sql = """INSERT INTO Comments(post_id, user_id, content)
            VALUES(?, ?, ?)"""
    db.execute(sql, [item_id, user_id, comment])

def get_comments(item_id):
    sql = """SELECT Comments.content, Users.id user_id, Users.username
            FROM Comments, Users
            WHERE Comments.post_id = ? AND Comments.user_id = Users.id
            ORDER BY Comments.id DESC"""
    return db.query(sql, [item_id])

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

def get_images(page, page_size):
    sql = """SELECT id, images
    FROM Items
    ORDER BY id DESC
    LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_items(page, page_size):
    sql = """SELECT Items.id, Items.description, Users.id user_id,
                    Users.username, COUNT(Comments.id) comment_count
    FROM Items JOIN Users ON Items.user_id = Users.id
                LEFT JOIN Comments ON Items.id = Comments.post_id
    GROUP BY Items.id
    ORDER BY Items.id DESC
    LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_image(item_id):
    sql = "SELECT images FROM Items WHERE id = ?"
    result = db.query(sql, [item_id])
    return result[0][0] if result else None

def get_item(item_id):
    sql = """SELECT Items.id, Items.description,
                    Users.username, Users.id user_id
             FROM Items, Users
             WHERE Items.user_id = Users.id AND
                   Items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, description, classes):
    sql = """UPDATE Items SET description = ?
                        WHERE id = ?"""
    db.execute(sql, [description, item_id])

    sql = "DELETE FROM Item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO Item_classes(item_id, title, value) VALUES(?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM Item_classes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM Comments WHERE post_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM Items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT Items.id, Items.images, Items.description, Users.id,
                    Users.username, COUNT(Comments.id) comment_count
            FROM Items JOIN Users ON Items.user_id = Users.id
                        LEFT JOIN Comments ON Items.id = Comments.post_id
            WHERE description LIKE ?
            GROUP BY Items.id
            ORDER BY Items.id DESC"""
    return db.query(sql, ["%" + query + "%"])
