CREATE TABLE files(
file_id INTEGER NOT NULL PRIMARY KEY,
file_name TEXT,
file_path TEXT,
uploader_id INTEGER,
FOREIGN KEY (uploader_id)
    REFERENCES users (id)
);


CREATE TABLE file_access(
access_record_id INTEGER NOT NULL PRIMARY KEY,
file_id INTEGER,
user_id INTEGER,
FOREIGN KEY (file_id)
    REFERENCES files (file_id),
FOREIGN KEY (user_id)
    REFERENCES users (id)

);