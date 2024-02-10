-- Create the database
CREATE DATABASE IF NOT EXISTS backend-svc;
USE backend-svc;

-- Create the 'posts' table
CREATE TABLE IF NOT EXISTS posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    provider_name VARCHAR(255),
    text TEXT NOT NULL,
    timestamp DATETIME,
    emotional_trait VARCHAR(255),
    link TEXT
);

-- Create the 'post_keywords' table
CREATE TABLE IF NOT EXISTS post_keywords (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT,
    keyword TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);