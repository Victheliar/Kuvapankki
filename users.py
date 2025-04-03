import db

def get_user(user_id):
    sql = "SELECT username FROM Users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_posts(user_id):
    sql = """SELECT I.id,
                    I.description,
                    I.images
            FROM Items I, Users U
            WHERE I.user_id = U.id
            AND U.id = ?
            ORDER BY I.id DESC"""
    return db.query(sql, [user_id])