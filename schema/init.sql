-- Create the 'posts' table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(255),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    emotional_trait VARCHAR(255),
    link TEXT
);

-- Create the 'post_keywords' table
CREATE TABLE IF NOT EXISTS post_keywords (
    id SERIAL PRIMARY KEY,
    post_id INT,
    keyword TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);