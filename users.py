import db

def get_user(user_id):
    sql = """SELECT id, username, profile_picture IS NOT NULL has_pfp
    FROM Users
    WHERE id = ?"""
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

def update_picture(user_id, picture):
    sql = "UPDATE Users SET profile_picture = ? WHERE id = ?"
    db.execute(sql, [picture, user_id])

def get_profile_picture(user_id):
    sql = "SELECT profile_picture FROM Users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None