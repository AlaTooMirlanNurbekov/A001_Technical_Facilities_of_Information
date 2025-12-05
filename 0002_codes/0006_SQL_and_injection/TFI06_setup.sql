-- This is to creates a users table for the safe login demo

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- demo users (simple for demonstration)
INSERT INTO users (username, password) VALUES
('admin', 'admin123'),
('student', 'password123'),
('test', 'qwerty');
