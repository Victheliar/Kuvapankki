CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    profile_picture BLOB
);

CREATE TABLE Items (
    id INTEGER PRIMARY KEY,
    description TEXT,
    user_id INTEGER REFERENCES Users,
    images BLOB
);

CREATE TABLE Classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE Item_classes (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES Items,
    title TEXT,
    value TEXT
);

CREATE TABLE Comments (
    id INTEGER PRIMARY KEY,
    content TEXT,
    user_id INTEGER REFERENCES Users,
    post_id INTEGER REFERENCES Items
);