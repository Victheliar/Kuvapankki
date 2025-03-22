import db

def add_item(description, user_id):
    sql = """INSERT INTO Items (description, user_id) VALUES (?, ?)"""
    db.execute(sql, [description, user_id])